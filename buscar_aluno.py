import sqlite3
import os

pasta_atual = os.path.dirname(os.path.abspath(__file__))
caminho_db = os.path.join(pasta_atual, "alunos.db")

def buscar_aluno(termo):
    conn = sqlite3.connect(caminho_db)
    cursor = conn.cursor()
    
    query = "SELECT id, nome, rga, ra, data_nasc, gaveta FROM alunos WHERE nome LIKE ? OR rga = ?"
    cursor.execute(query, (f"%{termo}%", termo))
    resultados = cursor.fetchall()
    
    conn.close()
    return resultados

def atualizar_gaveta(aluno_id, numero_gaveta):
    conn = sqlite3.connect(caminho_db)
    cursor = conn.cursor()
    
    cursor.execute("UPDATE alunos SET gaveta = ? WHERE id = ?", (numero_gaveta, aluno_id))
    conn.commit()
    conn.close()
    print(f"✅ Gaveta '{numero_gaveta}' atualizada para o aluno ID {aluno_id}!")

if __name__ == "__main__":
    busca = input("Digite o nome ou RGA do aluno: ")
    alunos = buscar_aluno(busca)
    
    if alunos:
        print("\n--- ALUNOS ENCONTRADOS ---")
        for a in alunos:
            gaveta_status = a[5] if a[5] else 'Não definida'
            print(f"ID: {a[0]} | Nome: {a[1]} | RGA: {a[2]} | Nasc: {a[4]} | Gaveta: {gaveta_status}")
            
        opcao = input("\nDeseja atualizar a gaveta de algum aluno? (s/n): ")
        if opcao.lower() == 's':
            id_sel = input("Digite o ID do aluno: ")
            gaveta = input("Digite a gaveta/armário (ex: Gaveta 02): ")
            atualizar_gaveta(id_sel, gaveta)
    else:
        print("❌ Nenhum aluno encontrado.")