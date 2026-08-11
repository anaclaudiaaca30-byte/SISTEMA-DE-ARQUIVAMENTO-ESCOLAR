import sqlite3
import pandas as pd
import os

pasta_atual = os.path.dirname(os.path.abspath(__file__))
caminho_excel = os.path.join(pasta_atual, "dados", "alunos_nome_nascimento_RA_RGA.xlsx")
if not os.path.exists(caminho_excel):
    caminho_excel = os.path.join(pasta_atual, "DADOS", "alunos_nome_nascimento_RA_RGA.xlsx")

caminho_db = os.path.join(pasta_atual, "alunos.db")

if not os.path.exists(caminho_excel):
    print("❌ Erro: Planilha Excel não encontrada na pasta 'dados'!")
    exit()

print(f"📖 Lendo a planilha: {caminho_excel}...")
df = pd.read_excel(caminho_excel)

conn = sqlite3.connect(caminho_db)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS alunos")
cursor.execute("""
CREATE TABLE alunos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    rga TEXT,
    ra TEXT,
    cpf TEXT,
    rg TEXT,
    data_nasc TEXT,
    nome_mae TEXT,
    ano TEXT,
    conclusao TEXT,
    gaveta TEXT
)
""")

ra_counter = 8541000
alunos_inseridos = 0

for idx, row in df.iterrows():
    nome = str(row['Nome completo']).strip().upper()
    data_nasc = str(row['Data de nascimento']).strip()
    rga = str(int(row['RGA'])) if pd.notna(row['RGA']) else ""
    
    ra_counter += 1
    ra = str(ra_counter)

    cursor.execute("""
    INSERT INTO alunos (nome, rga, ra, cpf, rg, data_nasc, nome_mae, ano, conclusao, gaveta)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (nome, rga, ra, "", "", data_nasc, "", "", "", ""))
    
    alunos_inseridos += 1

conn.commit()
conn.close()

print(f"🎉 SUCESSO! {alunos_inseridos} alunos gravados no banco '{caminho_db}'!")