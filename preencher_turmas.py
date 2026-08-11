import sqlite3
import os
import re
from pypdf import PdfReader

# Caminho do banco de dados na mesma pasta do script
pasta = os.path.dirname(os.path.abspath(__file__))
caminho_db = os.path.join(pasta, "alunos.db")

if not os.path.exists(caminho_db):
    print("❌ Erro: Banco de dados 'alunos.db' não foi encontrado na pasta!")
    exit()

conn = sqlite3.connect(caminho_db)
cursor = conn.cursor()

# Procura qualquer arquivo .pdf na pasta do projeto
arquivos_pdf = [f for f in os.listdir(pasta) if f.lower().endswith(".pdf")]

# Se não achar na raiz, procura também dentro da pasta 'dados'
if not arquivos_pdf:
    pasta_dados = os.path.join(pasta, "dados")
    if os.path.exists(pasta_dados):
        arquivos_pdf = [os.path.join("dados", f) for f in os.listdir(pasta_dados) if f.lower().endswith(".pdf")]

if not arquivos_pdf:
    print("❌ Erro: Nenhum arquivo PDF com as turmas foi encontrado na pasta!")
    print("👉 Certifique-se de salvar o PDF do EOL dentro da pasta 'SISTEMA-DE-ARQUIVAMENTO-ESCOLAR'.")
    conn.close()
    exit()

pdf_path = os.path.join(pasta, arquivos_pdf[0])
print(f"📖 Lendo e extraindo turmas do PDF: '{arquivos_pdf[0]}'...")

reader = PdfReader(pdf_path)
turmas_atualizadas = 0

for page_idx, page in enumerate(reader.pages):
    text = page.extract_text()
    if not text:
        continue
    
    # Identifica o padrão da Turma na página (ex: 1A, 2B, 5C, 9A)
    turma_match = re.search(r'Turma:\s*(\d+-[1-9][A-Z])', text)
    if turma_match:
        cod_turma = turma_match.group(1).split('-')[-1]
        nome_turma = f"{cod_turma[0]}º ANO {cod_turma[1]}"
        
        lines = text.split('\n')
        for line in lines:
            # Captura o RGA (4 dígitos) do aluno
            match_rga = re.search(r'\b(\d{4})\b', line)
            if match_rga:
                rga = match_rga.group(1)
                # Atualiza a turma no banco onde o RGA for correspondente
                cursor.execute("UPDATE alunos SET ano = ? WHERE rga = ?", (nome_turma, rga))
                if cursor.rowcount > 0:
                    turmas_atualizadas += 1

conn.commit()
conn.close()

if turmas_atualizadas > 0:
    print(f"🎉 SUCESSO COMPLETO! Turmas atualizadas para {turmas_atualizadas} alunos no banco de dados!")
else:
    print("⚠️ Nenhum aluno correspondente foi atualizado. Verifique se o RGA do PDF coincide com a planilha.")
    