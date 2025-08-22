import pandas as pd
import re
from datetime import datetime, time, date
from dateutil import parser
import logging

# Configuração de logging para depuração
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Tenta importar openpyxl para exportação em Excel
try:
    import openpyxl
except ImportError:
    openpyxl = None
    logging.warning(
        "Módulo 'openpyxl' não encontrado. A funcionalidade de exportação para Excel não estará disponível. Por favor, instale-o com 'pip install openpyxl'.")


def parse_data_hora(texto):
    """
    Tenta parsear uma string para um objeto datetime ou time,
    usando dateutil.parser de forma flexível para reconhecer vários formatos.
    """
    try:
        # Aprimorado para ser mais flexível com o formato
        return parser.parse(texto, dayfirst=True)
    except (ValueError, parser.ParserError):
        return None


def analise_jornada_trabalho(texto_completo, jornada_diaria, carga_horaria_semanal, tempo_intervalo,
                             salario_bruto, horario_inicio_str, horario_fim_str):
    """
    Analisa um texto de chat para gerar um relatório de trabalho,
    incluindo cálculos de horas extras e adicionais com base na CLT.
    """
    mensagens_analisadas = []
    linhas = texto_completo.splitlines()

    # Padrão flexível para capturar a data e hora
    padrao_regex = re.compile(
        r'^[\[\(\{]?(\d{1,2}[./-]\d{1,2}[./-]\d{2,4}),?\s*(\d{1,2}:\d{2}(?::\d{2})?)[\}\)]?\]?\s*[-]?\s*(.+?):\s(.*)',
        re.IGNORECASE
    )

    ultima_mensagem = None

    for linha in linhas:
        # Limpa caracteres invisíveis e espaços extras no início da linha
        linha = linha.lstrip('\u200e\u200f').strip()

        if not linha:
            continue

        match = padrao_regex.match(linha)

        if match:
            # Se a linha corresponde ao padrão, processamos como uma nova mensagem
            data_str = match.group(1)
            hora_str = match.group(2)
            remetente = match.group(3)
            conteudo = match.group(4)

            # Tenta converter a data e hora
            try:
                data_hora = parse_data_hora(f"{data_str} {hora_str}")
                if data_hora:
                    # Ignora linhas de notificação do sistema
                    if "criptografia" in remetente.lower() or "lista de contatos" in remetente.lower():
                        ultima_mensagem = None
                        continue

                    ultima_mensagem = {
                        'data': data_hora.date(),
                        'hora': data_hora.time(),
                        'remetente': remetente,
                        'conteudo': conteudo.strip()
                    }
                    mensagens_analisadas.append(ultima_mensagem)
                else:
                    ultima_mensagem = None
                    logging.warning(f"Erro ao parsear a linha: {linha}. Formato de data e hora não encontrado.")

            except Exception as e:
                ultima_mensagem = None
                logging.warning(f"Erro inesperado ao processar a linha: {linha}. Erro: {e}")

        elif ultima_mensagem:
            # Se a linha não tem data/hora, é uma continuação da mensagem anterior
            ultima_mensagem['conteudo'] += f" {linha.strip()}"

        else:
            # Linha não tem data/hora e não é uma continuação, ignoramos
            logging.warning(f"Erro ao parsear a linha: {linha}. Formato de data e hora não encontrado.")
            continue

    if not mensagens_analisadas:
        return pd.DataFrame(), {
            "erro": "Não foi possível extrair registros válidos do arquivo. Verifique se o formato de data e hora está presente."}

    df_mensagens = pd.DataFrame(mensagens_analisadas)
    df_mensagens = df_mensagens[df_mensagens['data'].notna()]
    df_mensagens = df_mensagens[df_mensagens['hora'].notna()]

    if df_mensagens.empty:
        return pd.DataFrame(), {
            "erro": "Não foi possível extrair registros válidos do arquivo. Verifique se o formato de data e hora está presente."}

    df_mensagens['data'] = pd.to_datetime(df_mensagens['data']).dt.date

    # Lógica para remover mensagens de "Mensagem apagada" ou "imagem omitida"
    df_mensagens = df_mensagens[
        ~df_mensagens['conteudo'].str.contains(
            "mensagem apagada|vídeo ocultado|imagem ocultada|áudio ocultado|vídeo omitido|imagem omitida|audio omitido",
            case=False, na=False)
    ]

    if df_mensagens.empty:
        return pd.DataFrame(), {
            "erro": "Nenhuma mensagem válida (sem mídia ou mensagens apagadas) encontrada para análise."
        }

    # Calcula o tempo de trabalho sem o intervalo
    jornada_diaria_sem_intervalo = jornada_diaria - tempo_intervalo

    # Parâmetros para cálculo de horas extras e adicionais
    horario_inicio_comercial = datetime.strptime(horario_inicio_str, "%H:%M").time()
    horario_fim_comercial = datetime.strptime(horario_fim_str, "%H:%M").time()

    # Taxas CLT (ajustáveis)
    percentual_hora_extra_normal = 1.50  # 50%
    percentual_hora_extra_atipica = 2.00  # 100%
    percentual_adicional_noturno = 0.20  # 20%

    # Cálculo do valor da hora normal de trabalho (assumindo 220 horas mensais)
    valor_hora_normal = salario_bruto / 220 if salario_bruto > 0 else 0

    dias = df_mensagens['data'].unique()
    relatorio = []

    for dia in sorted(dias):
        mensagens_dia = df_mensagens[df_mensagens['data'] == dia]

        entrada = mensagens_dia['hora'].min()
        saida = mensagens_dia['hora'].max()

        jornada_total = 0
        horas_extras = 0
        custo_horas_extras = 0
        adicional_noturno = 0
        observacoes = ""

        if entrada and saida:
            hora_entrada = datetime.combine(dia, entrada)
            hora_saida = datetime.combine(dia, saida)
            jornada_bruta = (hora_saida - hora_entrada).total_seconds() / 3600
            jornada_liquida = jornada_bruta - tempo_intervalo

            if jornada_liquida > 0:
                jornada_total = jornada_liquida

            dia_semana_num = dia.weekday()
            dia_semana_nome = \
            ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"][
                dia_semana_num]

            if dia_semana_num >= 5:  # Fim de semana
                horas_extras = jornada_total
                observacoes = "Fim de semana"
            else:  # Dias de semana
                if jornada_total > jornada_diaria_sem_intervalo:
                    horas_extras = jornada_total - jornada_diaria_sem_intervalo
                else:
                    horas_extras = 0

            # Cálculo do custo da hora extra
            if horas_extras > 0:
                if "Fim de semana" in observacoes:
                    custo_horas_extras = horas_extras * valor_hora_normal * percentual_hora_extra_atipica
                else:
                    custo_horas_extras = horas_extras * valor_hora_normal * percentual_hora_extra_normal

            # Adicional Noturno
            if saida > horario_fim_comercial:
                # Calcula as horas trabalhadas fora do horário comercial até a saída
                horas_apos_horario_fim = (datetime.combine(dia, saida) - datetime.combine(dia,
                                                                                          horario_fim_comercial)).total_seconds() / 3600
                adicional_noturno = horas_apos_horario_fim * valor_hora_normal * percentual_adicional_noturno

            if entrada < horario_inicio_comercial:
                observacoes += ", Acionamento atípico" if not observacoes else ", Acionamento atípico"

        else:
            dia_semana_nome = \
            ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"][
                dia.weekday()]
            entrada = "N/A"
            saida = "N/A"
            observacoes = "Registros incompletos"
            custo_horas_extras = 0
            adicional_noturno = 0
            if dia.weekday() >= 5:
                observacoes += ", Fim de semana"

        relatorio.append({
            "Data": dia.strftime("%d/%m/%Y"),
            "Dia da Semana": dia_semana_nome,
            "Entrada": entrada.strftime("%H:%M") if isinstance(entrada, time) else entrada,
            "Saída": saida.strftime("%H:%M") if isinstance(saida, time) else saida,
            "Jornada Total": round(jornada_total, 2),
            "Horas Extras": round(horas_extras, 2),
            "Custo Horas Extras": round(custo_horas_extras, 2),
            "Adicional Noturno": round(adicional_noturno, 2),
            "Observações": observacoes
        })

    df_relatorio = pd.DataFrame(relatorio)

    if not df_relatorio.empty:
        df_relatorio['Data'] = pd.to_datetime(df_relatorio['Data'], format='%d/%m/%Y').dt.date
        df_relatorio['Jornada Total'] = pd.to_numeric(df_relatorio['Jornada Total'], errors='coerce').fillna(0)
        df_relatorio['semana_do_ano'] = df_relatorio['Data'].apply(lambda x: x.isocalendar()[1])

        total_semanal_df = df_relatorio.groupby(['semana_do_ano'])['Jornada Total'].sum().reset_index()
        total_semanal_df['horas_extras_semanais'] = total_semanal_df['Jornada Total'] - carga_horaria_semanal
        total_semanal_df['horas_extras_semanais'] = total_semanal_df['horas_extras_semanais'].apply(lambda x: max(0, x))

        total_extras_normais = df_relatorio[~df_relatorio['Observações'].str.contains('Fim de semana', na=False)][
            'Horas Extras'].sum()
        total_extras_atipicas = df_relatorio[df_relatorio['Observações'].str.contains('Fim de semana', na=False)][
            'Horas Extras'].sum()
        total_horas_extras_semanal = total_semanal_df['horas_extras_semanais'].sum()

        custo_total_horas_extras = df_relatorio['Custo Horas Extras'].sum()
        adicional_noturno_total = df_relatorio['Adicional Noturno'].sum()
    else:
        total_extras_normais = 0
        total_extras_atipicas = 0
        total_horas_extras_semanal = 0
        custo_total_horas_extras = 0
        adicional_noturno_total = 0

    resumo = {
        "Total de Horas Extras": round(total_extras_normais + total_extras_atipicas, 2),
        "Horas Extras Normais": round(total_extras_normais, 2),
        "Horas Extras Atípicas": round(total_extras_atipicas, 2),
        "Horas Extras Semanais (Total)": round(total_horas_extras_semanal, 2),
        "Custo Total de Horas Extras": round(custo_total_horas_extras, 2),
        "Adicional Noturno": round(adicional_noturno_total, 2),
        "Inconsistencias":
            df_relatorio[df_relatorio['Observações'].str.contains('incompleto', case=False, na=False)].shape[
                0] if not df_relatorio.empty else 0,
        "Acionamentos atípicos":
            df_relatorio[df_relatorio['Observações'].str.contains('atípico', case=False, na=False)].shape[
                0] if not df_relatorio.empty else 0,
    }

    return df_relatorio, resumo
