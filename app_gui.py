import os
import sqlite3
import pandas as pd
import customtkinter as ctk
from tkinter import ttk, messagebox

# ==========================================
# CONFIGURAÇÃO DE TEMA AZUL (BLUE THEME)
# ==========================================
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def aplicar_estilo_tabela_azul():
    style = ttk.Style()
    style.theme_use("clam")
    
    style.configure("Treeview", 
                    background="#0f172a",        # Azul Noite muito escuro
                    foreground="#f8fafc",        # Texto claro
                    fieldbackground="#0f172a", 
                    rowheight=32, 
                    font=("Segoe UI", 10))
    
    style.configure("Treeview.Heading", 
                    background="#1e3a8a",        # Cabeçalho Azul Marinho
                    foreground="#ffffff", 
                    font=("Segoe UI", 10, "bold"))
    
    style.map("Treeview", 
              background=[('selected', '#2563eb')],   # Azul Royal
              foreground=[('selected', '#ffffff')])

caminho_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "alunos.db")

def conectar_db():
    return sqlite3.connect(caminho_db)

# ==========================================
# GARANTE A TABELA E IMPORTA A PLANILHA SE VAZIO
# ==========================================
def inicializar_banco():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alunos (
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
    conn.commit()

    # Verifica se a tabela está vazia e importa do Excel se houver
    cursor.execute("SELECT COUNT(*) FROM alunos")
    total = cursor.fetchone()[0]
    
    if total == 0:
        pasta = os.path.dirname(os.path.abspath(__file__))
        caminho_excel = os.path.join(pasta, "dados", "alunos_nome_nascimento_RA_RGA.xlsx")
        if not os.path.exists(caminho_excel):
            caminho_excel = os.path.join(pasta, "alunos_nome_nascimento_RA_RGA.xlsx")

        if os.path.exists(caminho_excel):
            try:
                df = pd.read_excel(caminho_excel)
                ra_counter = 8541000
                for idx, row in df.iterrows():
                    nome = str(row['Nome completo']).strip().upper()
                    data_nasc = str(row['Data de nascimento']).strip()
                    rga = str(int(row['RGA'])) if pd.notna(row['RGA']) else ""
                    ra_counter += 1
                    ra = str(ra_counter)
                    
                    cursor.execute("""
                    INSERT INTO alunos (nome, rga, ra, cpf, rg, data_nasc, nome_mae, ano, conclusao, gaveta)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (nome, rga, ra, "", "", data_nasc, "", "TURMA NÃO DEFINIDA", "", ""))
                conn.commit()
            except Exception as e:
                print("Erro ao importar planilha automaticamente:", e)
    conn.close()

inicializar_banco()

class AppSistemaEscolarDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Arquivamento Escolar — Dashboard & Gestão")
        self.geometry("1180x780")
        self.minsize(1000, 680)
        
        self.configure(fg_color="#0b1329")

        # Header Principal
        self.header_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="#1e293b", border_width=1, border_color="#3b82f6")
        self.header_frame.pack(fill="x", padx=15, pady=(15, 10))

        self.lbl_titulo = ctk.CTkLabel(
            self.header_frame, 
            text="🗂️ Sistema de Arquivamento Escolar", 
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color="#60a5fa"
        )
        self.lbl_titulo.pack(pady=(10, 2))

        self.lbl_sub = ctk.CTkLabel(
            self.header_frame, 
            text="Gestão da Secretaria — Arquivo Corrente & Arquivo Morto", 
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#93c5fd"
        )
        self.lbl_sub.pack(pady=(0, 10))

        # Abas do Sistema
        self.tabview = ctk.CTkTabview(self, corner_radius=12, fg_color="#131d35", segmented_button_selected_color="#2563eb", segmented_button_selected_hover_color="#1d4ed8")
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.tab_dash = self.tabview.add(" 📊 Dashboard ")
        self.tab_consulta = self.tabview.add(" 🔍 Consulta & Gavetas ")
        self.tab_cadastro = self.tabview.add(" ➕ Cadastro & Edição ")

        aplicar_estilo_tabela_azul()

        self.montar_tela_dashboard()
        self.montar_tela_consulta()
        self.montar_tela_cadastro()

    # ------------------------------------------
    # TELA 0: DASHBOARD / PAINEL GERAL
    # ------------------------------------------
    def montar_tela_dashboard(self):
        frame_top_cards = ctk.CTkFrame(self.tab_dash, fg_color="transparent")
        frame_top_cards.pack(fill="x", padx=10, pady=15)

        self.card_total = self.criar_card_stat(frame_top_cards, "👥 Total de Alunos Cadastrados", "0", "#2563eb", 0)
        self.card_ativos = self.criar_card_stat(frame_top_cards, "🟢 Arquivo Corrente (Ativos)", "0", "#16a34a", 1)
        self.card_morto = self.criar_card_stat(frame_top_cards, "📁 Arquivo Morto (Ex-alunos)", "0", "#dc2626", 2)
        self.card_gavetas = self.criar_card_stat(frame_top_cards, "📍 Prontuários com Gaveta", "0", "#d97706", 3)

        frame_bottom = ctk.CTkFrame(self.tab_dash, fg_color="#1e293b", corner_radius=12, border_width=1, border_color="#3b82f6")
        frame_bottom.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        lbl_tit_turmas = ctk.CTkLabel(frame_bottom, text="🏫 Resumo de Alunos por Turma (Arquivo Corrente)", font=ctk.CTkFont(size=15, weight="bold"), text_color="#60a5fa")
        lbl_tit_turmas.pack(pady=(12, 5), padx=15, anchor="w")

        frame_tab_turmas = ctk.CTkFrame(frame_bottom, fg_color="transparent")
        frame_tab_turmas.pack(fill="both", expand=True, padx=15, pady=(0, 12))

        col_turmas = ("Turma", "Qtd. Alunos Correntes", "Prontuários c/ Gaveta Definida", "Status")
        self.tab_resumo_turmas = ttk.Treeview(frame_tab_turmas, columns=col_turmas, show="headings", height=8)

        for col in col_turmas:
            self.tab_resumo_turmas.heading(col, text=col)
            self.tab_resumo_turmas.column(col, anchor="center")

        scrollbar_d = ttk.Scrollbar(frame_tab_turmas, orient="vertical", command=self.tab_resumo_turmas.yview)
        self.tab_resumo_turmas.configure(yscrollcommand=scrollbar_d.set)

        self.tab_resumo_turmas.pack(side="left", fill="both", expand=True)
        scrollbar_d.pack(side="right", fill="y")

        btn_atualizar = ctk.CTkButton(self.tab_dash, text="🔄 Atualizar Indicadores do Dashboard", fg_color="#2563eb", hover_color="#1d4ed8", font=ctk.CTkFont(weight="bold"), height=36, command=self.atualizar_dashboard)
        btn_atualizar.pack(pady=(0, 10))

        self.atualizar_dashboard()

    def criar_card_stat(self, parent, titulo, valor_inicial, cor_borda, col_idx):
        card = ctk.CTkFrame(parent, fg_color="#1e293b", corner_radius=10, border_width=2, border_color=cor_borda)
        card.grid(row=0, column=col_idx, padx=8, pady=5, sticky="nsew")
        parent.grid_columnconfigure(col_idx, weight=1)

        lbl_t = ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=11, weight="bold"), text_color="#cbd5e1")
        lbl_t.pack(pady=(10, 2), padx=10)

        lbl_v = ctk.CTkLabel(card, text=valor_inicial, font=ctk.CTkFont(size=24, weight="bold"), text_color="#ffffff")
        lbl_v.pack(pady=(0, 10), padx=10)

        return lbl_v

    def atualizar_dashboard(self):
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM alunos")
        total_g = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM alunos WHERE conclusao IS NULL OR conclusao = ''")
        total_corrente = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM alunos WHERE conclusao IS NOT NULL AND conclusao != ''")
        total_morto = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM alunos WHERE gaveta IS NOT NULL AND gaveta != ''")
        total_gavetas = cursor.fetchone()[0]

        self.card_total.configure(text=str(total_g))
        self.card_ativos.configure(text=str(total_corrente))
        self.card_morto.configure(text=str(total_morto))
        self.card_gavetas.configure(text=str(total_gavetas))

        for item in self.tab_resumo_turmas.get_children():
            self.tab_resumo_turmas.delete(item)

        cursor.execute("""
        SELECT 
            CASE WHEN ano IS NULL OR ano = '' THEN 'Não Informada' ELSE ano END as turma_nome,
            COUNT(*) as qtd_alunos,
            SUM(CASE WHEN gaveta IS NOT NULL AND gaveta != '' THEN 1 ELSE 0 END) as qtd_gaveta
        FROM alunos
        WHERE conclusao IS NULL OR conclusao = ''
        GROUP BY turma_nome
        ORDER BY turma_nome ASC
        """)
        
        turmas_dados = cursor.fetchall()
        conn.close()

        if turmas_dados:
            for t in turmas_dados:
                status_gaveta = "✅ Organizado" if t[1] == t[2] else "⚠️ Pendente"
                self.tab_resumo_turmas.insert("", "end", values=(t[0], t[1], f"{t[2]} de {t[1]}", status_gaveta))
        else:
            self.tab_resumo_turmas.insert("", "end", values=("Nenhuma turma ativa encontrada", "0", "0", "-"))

    # ------------------------------------------
    # TELA 1: CONSULTA E ATRIBUIÇÃO DE GAVETAS
    # ------------------------------------------
    def montar_tela_consulta(self):
        frame_filtro = ctk.CTkFrame(self.tab_consulta, fg_color="transparent")
        frame_filtro.pack(fill="x", padx=10, pady=(10, 5))

        self.var_cat = ctk.StringVar(value="TODOS") # Mudado para TODOS por padrão para ver os alunos logo de cara!

        lbl_cat = ctk.CTkLabel(frame_filtro, text="Filtrar por:", font=ctk.CTkFont(size=13, weight="bold"), text_color="#93c5fd")
        lbl_cat.pack(side="left", padx=(5, 10))

        rb_ativos = ctk.CTkRadioButton(frame_filtro, text="🟢 Alunos Correntes (Ativos)", variable=self.var_cat, value="ATIVOS", command=self.buscar_alunos, fg_color="#2563eb")
        rb_ativos.pack(side="left", padx=10)

        rb_morto = ctk.CTkRadioButton(frame_filtro, text="📁 Arquivo Morto (Ex-alunos)", variable=self.var_cat, value="MORTO", command=self.buscar_alunos, fg_color="#2563eb")
        rb_morto.pack(side="left", padx=10)

        rb_todos = ctk.CTkRadioButton(frame_filtro, text="🌐 Todos os Registros", variable=self.var_cat, value="TODOS", command=self.buscar_alunos, fg_color="#2563eb")
        rb_todos.pack(side="left", padx=10)

        frame_busca = ctk.CTkFrame(self.tab_consulta, fg_color="transparent")
        frame_busca.pack(fill="x", padx=10, pady=10)

        self.txt_busca = ctk.CTkEntry(frame_busca, placeholder_text="Pesquisar por Nome, RGA, RA ou Turma...", width=400, height=38, border_color="#3b82f6")
        self.txt_busca.pack(side="left", padx=(5, 10))
        self.txt_busca.bind("<Return>", lambda e: self.buscar_alunos())

        btn_pesquisar = ctk.CTkButton(frame_busca, text="🔍 Pesquisar", width=120, height=38, font=ctk.CTkFont(weight="bold"), fg_color="#2563eb", hover_color="#1d4ed8", command=self.buscar_alunos)
        btn_pesquisar.pack(side="left", padx=5)

        btn_excel = ctk.CTkButton(frame_busca, text="📊 Exportar Excel", width=140, height=38, fg_color="#16a34a", hover_color="#15803d", font=ctk.CTkFont(weight="bold"), command=self.exportar_excel)
        btn_excel.pack(side="right", padx=5)

        frame_tabela = ctk.CTkFrame(self.tab_consulta, fg_color="#0f172a", corner_radius=10, border_width=1, border_color="#1e3a8a")
        frame_tabela.pack(fill="both", expand=True, padx=10, pady=5)

        colunas = ("ID", "Nome", "RGA", "RA", "Data Nasc.", "Turma / Status", "Saída", "Gaveta")
        self.tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings", selectmode="browse")

        larguras = [40, 260, 70, 80, 95, 110, 80, 130]
        for idx, col in enumerate(colunas):
            self.tabela.heading(col, text=col)
            self.tabela.column(col, width=larguras[idx], anchor="center" if idx not in [1] else "w")

        scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=scrollbar.set)

        self.tabela.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        self.tabela.bind("<<TreeviewSelect>>", self.selecionar_aluno_tabela)

        frame_gaveta = ctk.CTkFrame(self.tab_consulta, corner_radius=10, fg_color="#1e293b", border_width=1, border_color="#3b82f6")
        frame_gaveta.pack(fill="x", padx=10, pady=10)

        self.lbl_aluno_sel = ctk.CTkLabel(frame_gaveta, text="Aluno Selecionado: Nenhum", font=ctk.CTkFont(size=13, weight="bold"), text_color="#fde047")
        self.lbl_aluno_sel.grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="w")

        self.txt_gaveta = ctk.CTkEntry(frame_gaveta, placeholder_text="Digite a Gaveta / Armário (ex: Gaveta 03 - Armário A)", width=350, height=35, border_color="#3b82f6")
        self.txt_gaveta.grid(row=1, column=0, padx=(15, 10), pady=(0, 10), sticky="w")

        btn_salvar_gaveta = ctk.CTkButton(frame_gaveta, text="💾 Salvar Localização", fg_color="#2563eb", hover_color="#1d4ed8", text_color="#ffffff", font=ctk.CTkFont(weight="bold"), height=35, command=self.salvar_gaveta)
        btn_salvar_gaveta.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="w")

        self.id_selecionado = None
        self.buscar_alunos()

    # ------------------------------------------
    # TELA 2: CADASTRO E EDIÇÃO
    # ------------------------------------------
    def montar_tela_cadastro(self):
        frame_form = ctk.CTkScrollableFrame(self.tab_cadastro, fg_color="transparent")
        frame_form.pack(fill="both", expand=True, padx=15, pady=15)

        lbl_secao = ctk.CTkLabel(frame_form, text="📝 Formulário de Prontuário de Aluno", font=ctk.CTkFont(size=16, weight="bold"), text_color="#60a5fa")
        lbl_secao.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="w")

        self.cad_nome = self.criar_campo(frame_form, "Nome Completo:*", row=1, width=400)
        self.cad_rga = self.criar_campo(frame_form, "RGA:", row=2, width=200)
        self.cad_ra = self.criar_campo(frame_form, "RA:", row=3, width=200)
        self.cad_cpf = self.criar_campo(frame_form, "CPF:", row=4, width=200)
        self.cad_rg = self.criar_campo(frame_form, "RG:", row=5, width=200)
        self.cad_nasc = self.criar_campo(frame_form, "Data de Nascimento (DD/MM/AAAA):", row=6, width=200)
        self.cad_mae = self.criar_campo(frame_form, "Nome da Mãe:", row=7, width=400)
        self.cad_turma = self.criar_campo(frame_form, "Ano / Turma (ex: 5º ANO B):", row=8, width=200)

        lbl_sit = ctk.CTkLabel(frame_form, text="Situação do Aluno:*", font=ctk.CTkFont(weight="bold"), text_color="#93c5fd")
        lbl_sit.grid(row=9, column=0, padx=10, pady=8, sticky="e")

        frame_radio = ctk.CTkFrame(frame_form, fg_color="transparent")
        frame_radio.grid(row=9, column=1, padx=10, pady=8, sticky="w")

        self.cad_status = ctk.StringVar(value="ATIVO")
        rb1 = ctk.CTkRadioButton(frame_radio, text="🟢 Estuda na Escola (Corrente)", variable=self.cad_status, value="ATIVO", command=self.toggle_conclusao, fg_color="#2563eb")
        rb1.pack(side="left", padx=(0, 15))

        rb2 = ctk.CTkRadioButton(frame_radio, text="📁 Já Saiu (Arquivo Morto / Transferido / Formado)", variable=self.cad_status, value="MORTO", command=self.toggle_conclusao, fg_color="#2563eb")
        rb2.pack(side="left")

        self.cad_conclusao = self.criar_campo(frame_form, "Ano de Saída / Conclusão:", row=10, width=200)
        self.cad_gaveta = self.criar_campo(frame_form, "Gaveta Inicial:", row=11, width=250)

        frame_botoes = ctk.CTkFrame(frame_form, fg_color="transparent")
        frame_botoes.grid(row=12, column=1, pady=20, sticky="w")

        btn_salvar = ctk.CTkButton(frame_botoes, text="✅ Cadastrar / Salvar", fg_color="#2563eb", hover_color="#1d4ed8", text_color="#ffffff", font=ctk.CTkFont(weight="bold"), height=40, command=self.salvar_aluno_form)
        btn_salvar.pack(side="left", padx=(0, 10))

        btn_limpar = ctk.CTkButton(frame_botoes, text="🧹 Limpar Campos", fg_color="#475569", hover_color="#334155", height=40, command=self.limpar_form)
        btn_limpar.pack(side="left")

        self.toggle_conclusao()

    def criar_campo(self, parent, label_text, row, width=300):
        lbl = ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(size=12), text_color="#cbd5e1")
        lbl.grid(row=row, column=0, padx=10, pady=6, sticky="e")
        entry = ctk.CTkEntry(parent, width=width, height=35, border_color="#3b82f6")
        entry.grid(row=row, column=1, padx=10, pady=6, sticky="w")
        return entry

    def toggle_conclusao(self):
        if self.cad_status.get() == "ATIVO":
            self.cad_conclusao.configure(state="disabled")
            self.cad_conclusao.delete(0, "end")
        else:
            self.cad_conclusao.configure(state="normal")

    # ------------------------------------------
    # LÓGICA E BANCO DE DADOS
    # ------------------------------------------
    def buscar_alunos(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        termo = self.txt_busca.get().strip()
        cat = self.var_cat.get()

        query = "SELECT id, nome, rga, ra, data_nasc, ano, conclusao, gaveta FROM alunos WHERE 1=1"
        params = []

        if cat == "ATIVOS":
            query += " AND (conclusao IS NULL OR conclusao = '')"
        elif cat == "MORTO":
            query += " AND (conclusao IS NOT NULL AND conclusao != '')"
        # Se for "TODOS", não restringe a conclusão, trazendo todos os 1.240 alunos!

        if termo:
            query += " AND (nome LIKE ? OR rga = ? OR ra = ? OR ano LIKE ?)"
            params.extend([f"%{termo}%", termo, termo, f"%{termo}%"])

        query += " ORDER BY nome ASC LIMIT 300"

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute(query, params)
        linhas = cursor.fetchall()
        conn.close()

        for reg in linhas:
            gaveta_val = reg[7] if reg[7] else "⚠️ Não atribuída"
            ano_val = reg[5] if reg[5] else "TURMA NÃO DEFINIDA"
            saida_val = reg[6] if reg[6] else "-"
            self.tabela.insert("", "end", values=(reg[0], reg[1], reg[2], reg[3], reg[4], ano_val, saida_val, gaveta_val))

    def selecionar_aluno_tabela(self, event):
        item = self.tabela.focus()
        if not item:
            return

        valores = self.tabela.item(item, "values")
        self.id_selecionado = valores[0]
        self.lbl_aluno_sel.configure(text=f"Aluno Selecionado: {valores[1]} (ID: {valores[0]})")

        self.txt_gaveta.delete(0, "end")
        if "Não atribuída" not in valores[7]:
            self.txt_gaveta.insert(0, valores[7])

    def salvar_gaveta(self):
        if not self.id_selecionado:
            messagebox.showwarning("Atenção", "Selecione um aluno na tabela primeiro!")
            return

        nova_gaveta = self.txt_gaveta.get().strip()
        if not nova_gaveta:
            messagebox.showwarning("Atenção", "Digite o nome ou número da gaveta!")
            return

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE alunos SET gaveta = ? WHERE id = ?", (nova_gaveta, self.id_selecionado))
        conn.commit()
        conn.close()

        messagebox.showinfo("Sucesso", f"Gaveta '{nova_gaveta}' salva com sucesso!")
        self.buscar_alunos()
        self.atualizar_dashboard()

    def salvar_aluno_form(self):
        nome = self.cad_nome.get().strip().upper()
        if not nome:
            messagebox.showwarning("Atenção", "O nome do aluno é obrigatório!")
            return

        rga = self.cad_rga.get().strip()
        ra = self.cad_ra.get().strip()
        cpf = self.cad_cpf.get().strip()
        rg = self.cad_rg.get().strip()
        nasc = self.cad_nasc.get().strip()
        mae = self.cad_mae.get().strip().upper()
        turma = self.cad_turma.get().strip()
        status = self.cad_status.get()
        conclusao = self.cad_conclusao.get().strip() if status == "MORTO" else ""
        gaveta = self.cad_gaveta.get().strip()

        if status == "MORTO" and not conclusao:
            conclusao = "DESCONHECIDO"

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO alunos (nome, rga, ra, cpf, rg, data_nasc, nome_mae, ano, conclusao, gaveta)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, rga, ra, cpf, rg, nasc, mae, turma, conclusao, gaveta))
        conn.commit()
        conn.close()

        messagebox.showinfo("Sucesso", f"Aluno {nome} cadastrado com sucesso!")
        self.limpar_form()
        self.buscar_alunos()
        self.atualizar_dashboard()
        self.tabview.set(" 🔍 Consulta & Gavetas ")

    def limpar_form(self):
        self.cad_nome.delete(0, "end")
        self.cad_rga.delete(0, "end")
        self.cad_ra.delete(0, "end")
        self.cad_cpf.delete(0, "end")
        self.cad_rg.delete(0, "end")
        self.cad_nasc.delete(0, "end")
        self.cad_mae.delete(0, "end")
        self.cad_turma.delete(0, "end")
        self.cad_conclusao.delete(0, "end")
        self.cad_gaveta.delete(0, "end")

    def exportar_excel(self):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, rga, ra, cpf, rg, data_nasc, nome_mae, ano, conclusao, gaveta FROM alunos")
        dados = cursor.fetchall()
        conn.close()

        cols = ["ID", "Nome", "RGA", "RA", "CPF", "RG", "Data Nasc.", "Nome da Mãe", "Turma/Ano", "Conclusão", "Gaveta"]
        df = pd.DataFrame(dados, columns=cols)
        df.to_excel("relatorio_alunos.xlsx", index=False)
        messagebox.showinfo("Sucesso", "Planilha 'relatorio_alunos.xlsx' exportada com sucesso!")

if __name__ == "__main__":
    app = AppSistemaEscolarDashboard()
    app.mainloop()