<h1 align="center">Analisador de Jornada de Trabalho</h1>

<p align="center">
Uma ferramenta online para calcular horas extras, adicional noturno e analisar relatórios de ponto de forma rápida e precisa.
</p>

🚀 Sobre o Projeto
Este projeto é uma calculadora trabalhista desenvolvida em Python com a interface web do Streamlit. Ele foi criado para automatizar a análise de registros de ponto, fornecendo um resumo financeiro e um relatório detalhado. Com ele, é possível processar dados inseridos manualmente ou extraídos de diversos tipos de arquivos.

✨ Funcionalidades
Entrada de Dados Flexível: Insira os registros de ponto manualmente ou faça upload de arquivos para extração automática de texto.

Compatibilidade de Arquivos: Analisa dados de arquivos de texto (.txt), Word (.docx), PDF (.pdf) e imagens (.png, .jpg, .jpeg).

Cálculos Inteligentes: Realiza o cálculo de horas extras (normais e atípicas), adicional noturno e custo total.

Filtros Avançados: Filtre o relatório por data, dias da semana ou tipo de ocorrência.

Exportação em Excel: Gere e baixe um relatório completo em formato .xlsx.

💻 Tecnologias Utilizadas
Python: A linguagem de programação principal.

Streamlit: O framework que cria a interface web interativa.

Pandas: Essencial para a manipulação e análise dos dados.

Outras Bibliotecas: openpyxl, PyPDF2, python-docx, Pillow e pytesseract.

⚙️ Como Executar Localmente
Siga estes passos para ter a aplicação rodando na sua máquina:

Clone o repositório e navegue até a pasta do projeto.

Instale todas as dependências do requirements.txt:

Bash

pip install -r requirements.txt
Inicie a aplicação com o Streamlit:

Bash

streamlit run app.py
☁️ Deploy na Nuvem (Streamlit Community Cloud)
A melhor forma de hospedar esta aplicação é usando a plataforma Streamlit Community Cloud, que é gratuita e otimizada para projetos como o seu.

Garanta que os arquivos app.py, requirements.txt e sua lógica de cálculo estão no seu repositório do GitHub.

Acesse share.streamlit.io e faça login com sua conta do GitHub.

Clique em "New app", selecione o repositório do seu projeto e clique em "Deploy".

A plataforma fará todo o trabalho de deploy para você, e sua calculadora estará online em poucos minutos.

📄 Licença
Este projeto está licenciado sob a Licença MIT. Para mais detalhes, consulte o arquivo LICENSE.md na raiz do repositório.
