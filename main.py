"""
Sistema de Gerenciamento Jurídico - VERSÃO COMPLETA
Passos 9 e 10: Busca avançada, Relatórios, Backup e Gestão de Clientes
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, timedelta
import shutil
import os

class SistemaJuridico:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gerenciamento Jurídico - Versão Completa")
        self.root.geometry("1200x700")
        
        # Cores do tema
        self.cor_primaria = "#2563eb"
        self.cor_secundaria = "#1e40af"
        self.cor_fundo = "#f8fafc"
        self.cor_texto = "#1e293b"
        self.cor_menu = "#1e293b"
        
        self.root.configure(bg=self.cor_fundo)
        
        # Tela atual
        self.tela_atual = "dashboard"
        
        # Inicializar banco de dados
        self.inicializar_banco()
        
        # Criar layout principal
        self.criar_layout()
        
    def inicializar_banco(self):
        """Cria o banco de dados SQLite e as tabelas"""
        self.conn = sqlite3.connect('sistema_juridico.db')
        self.cursor = self.conn.cursor()
        
        # Criar tabela de processos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS processos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT NOT NULL UNIQUE,
                cliente TEXT NOT NULL,
                tipo_acao TEXT NOT NULL,
                vara TEXT NOT NULL,
                status TEXT NOT NULL,
                data_distribuicao TEXT NOT NULL,
                valor_causa REAL,
                observacoes TEXT,
                data_cadastro TEXT NOT NULL
            )
        ''')
        
        # Criar tabela de andamentos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS andamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                processo_id INTEGER NOT NULL,
                data_andamento TEXT NOT NULL,
                descricao TEXT NOT NULL,
                data_cadastro TEXT NOT NULL,
                FOREIGN KEY (processo_id) REFERENCES processos (id)
            )
        ''')
        
        # Criar tabela de tarefas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tarefas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                processo_id INTEGER,
                titulo TEXT NOT NULL,
                descricao TEXT,
                tipo TEXT NOT NULL,
                data_vencimento TEXT NOT NULL,
                concluida INTEGER DEFAULT 0,
                data_conclusao TEXT,
                data_cadastro TEXT NOT NULL,
                FOREIGN KEY (processo_id) REFERENCES processos (id)
            )
        ''')
        
        # Criar tabela de clientes
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf_cnpj TEXT UNIQUE,
                telefone TEXT,
                email TEXT,
                endereco TEXT,
                observacoes TEXT,
                data_cadastro TEXT NOT NULL
            )
        ''')
        
        self.conn.commit()
        print("✅ Banco de dados criado com sucesso!")
        
    def criar_layout(self):
        """Cria o layout com menu lateral e área de conteúdo"""
        
        # ============ MENU LATERAL ============
        self.menu_frame = tk.Frame(
            self.root,
            bg=self.cor_menu,
            width=250
        )
        self.menu_frame.pack(side="left", fill="y")
        self.menu_frame.pack_propagate(False)
        
        # Logo/Título do menu
        titulo_menu = tk.Label(
            self.menu_frame,
            text="⚖️ Sistema\nJurídico",
            font=("Arial", 18, "bold"),
            bg=self.cor_menu,
            fg="white",
            pady=30
        )
        titulo_menu.pack()
        
        # Separador
        separador = tk.Frame(self.menu_frame, bg="white", height=2)
        separador.pack(fill="x", padx=20, pady=10)
        
        # Botões do menu
        self.criar_botao_menu("📊 Dashboard", "dashboard")
        self.criar_botao_menu("📁 Processos", "processos")
        self.criar_botao_menu("👥 Clientes", "clientes")
        self.criar_botao_menu("✅ Tarefas", "tarefas")
        self.criar_botao_menu("🔍 Busca Avançada", "busca")
        self.criar_botao_menu("💾 Backup", "backup")
        
        # Botão de sair no final
        tk.Frame(self.menu_frame, bg=self.cor_menu).pack(expand=True)
        
        btn_sair = tk.Button(
            self.menu_frame,
            text="🚪 Sair",
            font=("Arial", 12),
            bg="#ef4444",
            fg="white",
            bd=0,
            padx=20,
            pady=15,
            cursor="hand2",
            command=self.sair_aplicacao
        )
        btn_sair.pack(fill="x", padx=10, pady=10)
        
        # ============ ÁREA DE CONTEÚDO ============
        self.conteudo_frame = tk.Frame(
            self.root,
            bg=self.cor_fundo
        )
        self.conteudo_frame.pack(side="right", fill="both", expand=True)
        
        # Mostrar tela inicial
        self.mostrar_tela("dashboard")
        
    def criar_botao_menu(self, texto, tela):
        """Cria um botão no menu lateral"""
        btn = tk.Button(
            self.menu_frame,
            text=texto,
            font=("Arial", 12),
            bg=self.cor_menu,
            fg="white",
            bd=0,
            padx=20,
            pady=15,
            cursor="hand2",
            anchor="w",
            command=lambda: self.mostrar_tela(tela)
        )
        btn.pack(fill="x", padx=10, pady=5)
        
        # Efeito hover
        btn.bind("<Enter>", lambda e: btn.config(bg=self.cor_primaria))
        btn.bind("<Leave>", lambda e: btn.config(bg=self.cor_menu))
        
    def mostrar_tela(self, tela):
        """Alterna entre as diferentes telas"""
        self.tela_atual = tela
        
        # Limpar conteúdo anterior
        for widget in self.conteudo_frame.winfo_children():
            widget.destroy()
        
        # Criar header
        header = tk.Frame(self.conteudo_frame, bg="white", height=80)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)
        
        # Título da tela
        titulos = {
            "dashboard": "📊 Dashboard",
            "processos": "📁 Processos",
            "clientes": "👥 Clientes",
            "tarefas": "✅ Tarefas e Prazos",
            "busca": "🔍 Busca Avançada",
            "backup": "💾 Backup e Restauração"
        }
        
        titulo = tk.Label(
            header,
            text=titulos[tela],
            font=("Arial", 24, "bold"),
            bg="white",
            fg=self.cor_texto
        )
        titulo.pack(side="left", padx=20, pady=20)
        
        # Área de conteúdo
        conteudo = tk.Frame(self.conteudo_frame, bg=self.cor_fundo)
        conteudo.pack(fill="both", expand=True, padx=20)
        
        # Mostrar conteúdo específico de cada tela
        if tela == "dashboard":
            self.mostrar_dashboard(conteudo)
        elif tela == "processos":
            self.mostrar_processos(conteudo)
        elif tela == "clientes":
            self.mostrar_clientes(conteudo)
        elif tela == "tarefas":
            self.mostrar_tarefas(conteudo)
        elif tela == "busca":
            self.mostrar_busca(conteudo)
        elif tela == "backup":
            self.mostrar_backup(conteudo)
    
    def mostrar_dashboard(self, frame):
        """Mostra o dashboard com estatísticas"""
        # Buscar estatísticas do banco
        self.cursor.execute("SELECT COUNT(*) FROM processos")
        total_processos = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM processos WHERE status='Ativo'")
        processos_ativos = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM clientes")
        total_clientes = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM tarefas WHERE concluida=0")
        tarefas_pendentes = self.cursor.fetchone()[0]
        
        # Tarefas urgentes (próximos 7 dias)
        data_limite = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        self.cursor.execute('''
            SELECT COUNT(*) FROM tarefas 
            WHERE concluida=0 AND date(data_vencimento) <= ?
        ''', (data_limite,))
        tarefas_urgentes = self.cursor.fetchone()[0]
        
        # Frame para os cards
        cards_frame = tk.Frame(frame, bg=self.cor_fundo)
        cards_frame.pack(pady=20)
        
        # Cards - Linha 1
        self.criar_card(cards_frame, "Processos Ativos", str(processos_ativos), "#3b82f6", 0, 0)
        self.criar_card(cards_frame, "Total de Clientes", str(total_clientes), "#8b5cf6", 0, 1)
        self.criar_card(cards_frame, "Tarefas Pendentes", str(tarefas_pendentes), "#10b981", 0, 2)
        self.criar_card(cards_frame, "Tarefas Urgentes", str(tarefas_urgentes), "#ef4444", 0, 3)
        
        # Tarefas próximas do vencimento
        tarefas_frame = tk.Frame(frame, bg="white", relief="solid", bd=1)
        tarefas_frame.pack(fill="both", expand=True, pady=20)
        
        tk.Label(
            tarefas_frame,
            text="⚠️ Tarefas Próximas do Vencimento (7 dias)",
            font=("Arial", 14, "bold"),
            bg="white",
            fg=self.cor_texto
        ).pack(pady=15)
        
        # Buscar tarefas urgentes
        self.cursor.execute('''
            SELECT t.titulo, t.data_vencimento, t.tipo, p.numero
            FROM tarefas t
            LEFT JOIN processos p ON t.processo_id = p.id
            WHERE t.concluida=0 AND date(t.data_vencimento) <= ?
            ORDER BY t.data_vencimento ASC
            LIMIT 10
        ''', (data_limite,))
        
        tarefas_urgentes_lista = self.cursor.fetchall()
        
        if not tarefas_urgentes_lista:
            tk.Label(
                tarefas_frame,
                text="🎉 Nenhuma tarefa urgente!\n\nTodos os prazos estão em dia.",
                font=("Arial", 12),
                bg="white",
                fg="#6b7280",
                justify="center"
            ).pack(expand=True, pady=30)
        else:
            lista_frame = tk.Frame(tarefas_frame, bg="white")
            lista_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            for titulo, vencimento, tipo, numero_processo in tarefas_urgentes_lista:
                try:
                    data_venc = datetime.strptime(vencimento, "%Y-%m-%d %H:%M")
                    dias_restantes = (data_venc - datetime.now()).days
                    
                    # Cor baseada na urgência
                    if dias_restantes < 0:
                        cor_alerta = "#fee2e2"
                        texto_dias = "ATRASADO"
                    elif dias_restantes == 0:
                        cor_alerta = "#fef3c7"
                        texto_dias = "HOJE"
                    elif dias_restantes <= 3:
                        cor_alerta = "#fed7aa"
                        texto_dias = f"{dias_restantes} dia(s)"
                    else:
                        cor_alerta = "#e0f2fe"
                        texto_dias = f"{dias_restantes} dia(s)"
                    
                    tarefa_card = tk.Frame(lista_frame, bg=cor_alerta, relief="solid", bd=1)
                    tarefa_card.pack(fill="x", pady=5)
                    
                    info_frame = tk.Frame(tarefa_card, bg=cor_alerta)
                    info_frame.pack(fill="x", padx=15, pady=10)
                    
                    tk.Label(
                        info_frame,
                        text=f"⏰ {titulo}",
                        font=("Arial", 11, "bold"),
                        bg=cor_alerta,
                        fg=self.cor_texto
                    ).pack(anchor="w")
                    
                    detalhes = f"📅 {data_venc.strftime('%d/%m/%Y %H:%M')} ({texto_dias})"
                    if numero_processo:
                        detalhes += f" | 📁 Processo: {numero_processo}"
                    
                    tk.Label(
                        info_frame,
                        text=detalhes,
                        font=("Arial", 9),
                        bg=cor_alerta,
                        fg=self.cor_texto
                    ).pack(anchor="w")
                    
                except:
                    pass
    
    def criar_card(self, parent, titulo, valor, cor, row, col):
        """Cria um card de estatística"""
        card = tk.Frame(
            parent,
            bg=cor,
            width=220,
            height=130
        )
        card.grid(row=row, column=col, padx=10, pady=10)
        card.grid_propagate(False)
        
        # Valor grande
        lbl_valor = tk.Label(
            card,
            text=valor,
            font=("Arial", 42, "bold"),
            bg=cor,
            fg="white"
        )
        lbl_valor.pack(expand=True)
        
        # Título
        lbl_titulo = tk.Label(
            card,
            text=titulo,
            font=("Arial", 11),
            bg=cor,
            fg="white"
        )
        lbl_titulo.pack(pady=(0, 10))
    
    def mostrar_processos(self, frame):
        """Mostra a tela de processos"""
        # Formulário de cadastro (simplificado)
        form_frame = tk.Frame(frame, bg="white", relief="solid", bd=1)
        form_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            form_frame,
            text="➕ Cadastrar Novo Processo",
            font=("Arial", 16, "bold"),
            bg="white",
            fg=self.cor_texto
        ).pack(pady=15)
        
        campos_frame = tk.Frame(form_frame, bg="white")
        campos_frame.pack(padx=30, pady=(0, 20))
        
        # Linha 1
        linha1 = tk.Frame(campos_frame, bg="white")
        linha1.pack(fill="x", pady=5)
        
        tk.Label(linha1, text="Número:", bg="white", font=("Arial", 10)).pack(side="left")
        self.entry_numero = tk.Entry(linha1, font=("Arial", 10), width=25)
        self.entry_numero.pack(side="left", padx=(10, 30))
        
        tk.Label(linha1, text="Cliente:", bg="white", font=("Arial", 10)).pack(side="left")
        
        # Buscar clientes para o combobox
        self.cursor.execute("SELECT nome FROM clientes ORDER BY nome")
        clientes = self.cursor.fetchall()
        clientes_lista = [c[0] for c in clientes]
        
        self.combo_cliente_processo = ttk.Combobox(linha1, font=("Arial", 10), width=28, values=clientes_lista)
        self.combo_cliente_processo.pack(side="left", padx=10)
        
        # Linha 2
        linha2 = tk.Frame(campos_frame, bg="white")
        linha2.pack(fill="x", pady=5)
        
        tk.Label(linha2, text="Tipo:", bg="white", font=("Arial", 10)).pack(side="left")
        self.combo_tipo = ttk.Combobox(linha2, font=("Arial", 10), width=23, state="readonly")
        self.combo_tipo['values'] = ('Trabalhista', 'Cível', 'Criminal', 'Tributário', 'Família', 'Previdenciário')
        self.combo_tipo.current(0)
        self.combo_tipo.pack(side="left", padx=(10, 30))
        
        tk.Label(linha2, text="Vara:", bg="white", font=("Arial", 10)).pack(side="left")
        self.entry_vara = tk.Entry(linha2, font=("Arial", 10), width=30)
        self.entry_vara.pack(side="left", padx=10)
        
        # Linha 3
        linha3 = tk.Frame(campos_frame, bg="white")
        linha3.pack(fill="x", pady=5)
        
        tk.Label(linha3, text="Status:", bg="white", font=("Arial", 10)).pack(side="left")
        self.combo_status = ttk.Combobox(linha3, font=("Arial", 10), width=23, state="readonly")
        self.combo_status['values'] = ('Ativo', 'Arquivado', 'Finalizado')
        self.combo_status.current(0)
        self.combo_status.pack(side="left", padx=(10, 30))
        
        tk.Label(linha3, text="Data Dist.:", bg="white", font=("Arial", 10)).pack(side="left")
        self.entry_data = tk.Entry(linha3, font=("Arial", 10), width=15)
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.entry_data.pack(side="left", padx=10)
        
        tk.Label(linha3, text="Valor (R$):", bg="white", font=("Arial", 10)).pack(side="left", padx=(20, 0))
        self.entry_valor = tk.Entry(linha3, font=("Arial", 10), width=15)
        self.entry_valor.insert(0, "0.00")
        self.entry_valor.pack(side="left", padx=10)
        
        # Linha 4
        linha4 = tk.Frame(campos_frame, bg="white")
        linha4.pack(fill="x", pady=5)
        
        tk.Label(linha4, text="Observações:", bg="white", font=("Arial", 10)).pack(anchor="w")
        self.text_obs = tk.Text(linha4, font=("Arial", 10), width=70, height=3)
        self.text_obs.pack(fill="x", pady=5)
        
        btn_salvar = tk.Button(
            form_frame,
            text="💾 Salvar Processo",
            font=("Arial", 12, "bold"),
            bg=self.cor_primaria,
            fg="white",
            bd=0,
            padx=30,
            pady=10,
            cursor="hand2",
            command=self.salvar_processo
        )
        btn_salvar.pack(pady=(0, 15))
        
        # Lista de processos
        lista_frame = tk.Frame(frame, bg="white", relief="solid", bd=1)
        lista_frame.pack(fill="both", expand=True)
        
        tk.Label(
            lista_frame,
            text="📋 Processos Cadastrados",
            font=("Arial", 16, "bold"),
            bg="white",
            fg=self.cor_texto
        ).pack(pady=15)
        
        tree_frame = tk.Frame(lista_frame, bg="white")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        colunas = ("Número", "Cliente", "Tipo", "Status", "Data")
        self.tree_processos = ttk.Treeview(
            tree_frame,
            columns=colunas,
            show="headings",
            yscrollcommand=scrollbar.set,
            height=10
        )
        scrollbar.config(command=self.tree_processos.yview)
        
        self.tree_processos.heading("Número", text="Número do Processo")
        self.tree_processos.heading("Cliente", text="Cliente")
        self.tree_processos.heading("Tipo", text="Tipo de Ação")
        self.tree_processos.heading("Status", text="Status")
        self.tree_processos.heading("Data", text="Data Distribuição")
        
        self.tree_processos.column("Número", width=200)
        self.tree_processos.column("Cliente", width=200)
        self.tree_processos.column("Tipo", width=150)
        self.tree_processos.column("Status", width=100)
        self.tree_processos.column("Data", width=120)
        
        self.tree_processos.pack(fill="both", expand=True)
        
        btn_frame = tk.Frame(lista_frame, bg="white")
        btn_frame.pack(pady=10)
        
        btn_detalhes = tk.Button(
            btn_frame,
            text="🔍 Ver Detalhes",
            font=("Arial", 11, "bold"),
            bg="#10b981",
            fg="white",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.abrir_detalhes_processo
        )
        btn_detalhes.pack(side="left", padx=5)
        
        btn_excluir = tk.Button(
            btn_frame,
            text="🗑️ Excluir",
            font=("Arial", 11, "bold"),
            bg="#ef4444",
            fg="white",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.excluir_processo
        )
        btn_excluir.pack(side="left", padx=5)
        
        self.tree_processos.bind("<Double-1>", lambda e: self.abrir_detalhes_processo())
        
        self.carregar_processos()
    
    def mostrar_clientes(self, frame):
        """Mostra a tela de clientes"""
        # Formulário de cadastro
        form_frame = tk.Frame(frame, bg="white", relief="solid", bd=1)
        form_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            form_frame,
            text="➕ Cadastrar Novo Cliente",
            font=("Arial", 16, "bold"),
            bg="white",
            fg=self.cor_texto
        ).pack(pady=15)
        
        campos_frame = tk.Frame(form_frame, bg="white")
        campos_frame.pack(padx=30, pady=(0, 20))
        
        # Linha 1
        linha1 = tk.Frame(campos_frame, bg="white")
        linha1.pack(fill="x", pady=5)
        
        tk.Label(linha1, text="Nome Completo:", bg="white", font=("Arial", 10)).pack(side="left")
        self.entry_nome_cliente = tk.Entry(linha1, font=("Arial", 10), width=40)
        self.entry_nome_cliente.pack(side="left", padx=(10, 30))
        
        tk.Label(linha1, text="CPF/CNPJ:", bg="white", font=("Arial", 10)).pack(side="left")
        self.entry_cpf_cliente = tk.Entry(linha1, font=("Arial", 10), width=20)
        self.entry_cpf_cliente.pack(side="left", padx=10)
        
        # Linha 2
        linha2 = tk.Frame(campos_frame, bg="white")
        linha2.pack(fill="x", pady=5)
        
        tk.Label(linha2, text="Telefone:", bg="white", font=("Arial", 10)).pack(side="left")
        self.entry_tel_cliente = tk.Entry(linha2, font=("Arial", 10), width=20)
        self.entry_tel_cliente.pack(side="left", padx=(10, 30))
        
        tk.Label(linha2, text="E-mail:", bg="white", font=("Arial", 10)).pack(side="left")
        self.entry_email_cliente = tk.Entry(linha2, font=("Arial", 10), width=40)
        self.entry_email_cliente.pack(side="left", padx=10)
        
        # Linha 3
        linha3 = tk.Frame(campos_frame, bg="white")
        linha3.pack(fill="x", pady=5)
        
        tk.Label(linha3, text="Endereço:", bg="white", font=("Arial", 10)).pack(anchor="w")
        self.entry_end_cliente = tk.Entry(linha3, font=("Arial", 10), width=70)
        self.entry_end_cliente.pack(fill="x", pady=5)
        
        # Linha 4
        linha4 = tk.Frame(campos_frame, bg="white")
        linha4.pack(fill="x", pady=5)
        
        tk.Label(linha4, text="Observações:", bg="white", font=("Arial", 10)).pack(anchor="w")
        self.text_obs_cliente = tk.Text(linha4, font=("Arial", 10), width=70, height=3)
        self.text_obs_cliente.pack(fill="x", pady=5)
        
        btn_salvar_cliente = tk.Button(
            form_frame,
            text="💾 Salvar Cliente",
            font=("Arial", 12, "bold"),
            bg=self.cor_primaria,
            fg="white",
            bd=0,
            padx=30,
            pady=10,
            cursor="hand2",
            command=self.salvar_cliente
        )
        btn_salvar_cliente.pack(pady=(0, 15))
        
        # Lista de clientes
        lista_frame = tk.Frame(frame, bg="white", relief="solid", bd=1)
        lista_frame.pack(fill="both", expand=True)
        
        tk.Label(
            lista_frame,
            text="📋 Clientes Cadastrados",
            font=("Arial", 16, "bold"),
            bg="white",
            fg=self.cor_texto
        ).pack(pady=15)
        
        tree_frame = tk.Frame(lista_frame, bg="white")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        colunas = ("Nome", "CPF/CNPJ", "Telefone", "Email", "Processos")
        self.tree_clientes = ttk.Treeview(
            tree_frame,
            columns=colunas,
            show="headings",
            yscrollcommand=scrollbar.set,
            height=12
        )
        scrollbar.config(command=self.tree_clientes.yview)
        
        self.tree_clientes.heading("Nome", text="Nome Completo")
        self.tree_clientes.heading("CPF/CNPJ", text="CPF/CNPJ")
        self.tree_clientes.heading("Telefone", text="Telefone")
        self.tree_clientes.heading("Email", text="E-mail")
        self.tree_clientes.heading("Processos", text="Nº Processos")
        
        self.tree_clientes.column("Nome", width=250)
        self.tree_clientes.column("CPF/CNPJ", width=150)
        self.tree_clientes.column("Telefone", width=150)
        self.tree_clientes.column("Email", width=200)
        self.tree_clientes.column("Processos", width=100)
        
        self.tree_clientes.pack(fill="both", expand=True)
        
        btn_frame = tk.Frame(lista_frame, bg="white")
        btn_frame.pack(pady=10)
        
        btn_ver_processos = tk.Button(
            btn_frame,
            text="📁 Ver Processos do Cliente",
            font=("Arial", 11, "bold"),
            bg="#10b981",
            fg="white",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.ver_processos_cliente
        )
        btn_ver_processos.pack(side="left", padx=5)
        
        btn_excluir_cliente = tk.Button(
            btn_frame,
            text="🗑️ Excluir Cliente",
            font=("Arial", 11, "bold"),
            bg="#ef4444",
            fg="white",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.excluir_cliente
        )
        btn_excluir_cliente.pack(side="left", padx=5)
        
        self.carregar_clientes()
    
    def mostrar_tarefas(self, frame):
        """Mostra a tela de tarefas"""
        # Formulário de cadastro
        form_frame = tk.Frame(frame, bg="white", relief="solid", bd=1)
        form_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            form_frame,
            text="➕ Cadastrar Nova Tarefa/Prazo",
            font=("Arial", 16, "bold"),
            bg="white",
            fg=self.cor_texto
        ).pack(pady=15)
        
        campos_frame = tk.Frame(form_frame, bg="white")
        campos_frame.pack(padx=30, pady=(0, 20))
        
        # Linha 1
        linha1 = tk.Frame(campos_frame, bg="white")
        linha1.pack(fill="x", pady=5)
        
        tk.Label(linha1, text="Título:", bg="white", font=("Arial", 10)).pack(side="left")
        self.entry_titulo_tarefa = tk.Entry(linha1, font=("Arial", 10), width=40)
        self.entry_titulo_tarefa.pack(side="left", padx=(10, 30))
        
        tk.Label(linha1, text="Tipo:", bg="white", font=("Arial", 10)).pack(side="left")
        self.combo_tipo_tarefa = ttk.Combobox(linha1, font=("Arial", 10), width=20, state="readonly")
        self.combo_tipo_tarefa['values'] = ('Audiência', 'Petição', 'Recurso', 'Prazo', 'Reunião', 'Outro')
        self.combo_tipo_tarefa.current(0)
        self.combo_tipo_tarefa.pack(side="left", padx=10)
        
        # Linha 2
        linha2 = tk.Frame(campos_frame, bg="white")
        linha2.pack(fill="x", pady=5)
        
        tk.Label(linha2, text="Processo (opcional):", bg="white", font=("Arial", 10)).pack(side="left")
        
        self.cursor.execute("SELECT numero FROM processos ORDER BY numero")
        processos = self.cursor.fetchall()
        processos_lista = ["Nenhum (tarefa geral)"] + [p[0] for p in processos]
        
        self.combo_processo_tarefa = ttk.Combobox(linha2, font=("Arial", 10), width=25, state="readonly")
        self.combo_processo_tarefa['values'] = processos_lista
        self.combo_processo_tarefa.current(0)
        self.combo_processo_tarefa.pack(side="left", padx=(10, 30))
        
        tk.Label(linha2, text="Data/Hora:", bg="white", font=("Arial", 10)).pack(side="left")
        self.entry_data_tarefa = tk.Entry(linha2, font=("Arial", 10), width=15)
        self.entry_data_tarefa.insert(0, datetime.now().strftime("%d/%m/%Y %H:%M"))
        self.entry_data_tarefa.pack(side="left", padx=10)
        
        # Linha 3
        linha3 = tk.Frame(campos_frame, bg="white")
        linha3.pack(fill="x", pady=5)
        
        tk.Label(linha3, text="Descrição:", bg="white", font=("Arial", 10)).pack(anchor="w")
        self.text_desc_tarefa = tk.Text(linha3, font=("Arial", 10), width=70, height=3)
        self.text_desc_tarefa.pack(fill="x", pady=5)
        
        btn_salvar_tarefa = tk.Button(
            form_frame,
            text="💾 Salvar Tarefa",
            font=("Arial", 12, "bold"),
            bg=self.cor_primaria,
            fg="white",
            bd=0,
            padx=30,
            pady=10,
            cursor="hand2",
            command=self.salvar_tarefa
        )
        btn_salvar_tarefa.pack(pady=(0, 15))
        
        # Lista de tarefas
        lista_frame = tk.Frame(frame, bg="white", relief="solid", bd=1)
        lista_frame.pack(fill="both", expand=True)
        
        header_tarefas = tk.Frame(lista_frame, bg="white")
        header_tarefas.pack(fill="x", padx=20, pady=15)
        
        tk.Label(
            header_tarefas,
            text="📋 Tarefas Cadastradas",
            font=("Arial", 16, "bold"),
            bg="white",
            fg=self.cor_texto
        ).pack(side="left")
        
        tk.Label(header_tarefas, text="Filtrar:", bg="white", font=("Arial", 10)).pack(side="left", padx=(30, 10))
        
        self.combo_filtro_tarefa = ttk.Combobox(header_tarefas, font=("Arial", 10), width=15, state="readonly")
        self.combo_filtro_tarefa['values'] = ('Todas', 'Pendentes', 'Concluídas', 'Atrasadas')
        self.combo_filtro_tarefa.current(1)
        self.combo_filtro_tarefa.bind('<<ComboboxSelected>>', lambda e: self.carregar_tarefas())
        self.combo_filtro_tarefa.pack(side="left")
        
        tree_frame = tk.Frame(lista_frame, bg="white")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        colunas = ("Status", "Título", "Tipo", "Vencimento", "Processo")
        self.tree_tarefas = ttk.Treeview(
            tree_frame,
            columns=colunas,
            show="headings",
            yscrollcommand=scrollbar.set,
            height=12
        )
        scrollbar.config(command=self.tree_tarefas.yview)
        
        self.tree_tarefas.heading("Status", text="✓")
        self.tree_tarefas.heading("Título", text="Título")
        self.tree_tarefas.heading("Tipo", text="Tipo")
        self.tree_tarefas.heading("Vencimento", text="Vencimento")
        self.tree_tarefas.heading("Processo", text="Processo")
        
        self.tree_tarefas.column("Status", width=50)
        self.tree_tarefas.column("Título", width=300)
        self.tree_tarefas.column("Tipo", width=120)
        self.tree_tarefas.column("Vencimento", width=150)
        self.tree_tarefas.column("Processo", width=200)
        
        self.tree_tarefas.pack(fill="both", expand=True)
        
        btn_frame = tk.Frame(lista_frame, bg="white")
        btn_frame.pack(pady=10)
        
        btn_concluir = tk.Button(
            btn_frame,
            text="✅ Marcar como Concluída",
            font=("Arial", 11, "bold"),
            bg="#10b981",
            fg="white",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.concluir_tarefa
        )
        btn_concluir.pack(side="left", padx=5)
        
        btn_excluir_tarefa = tk.Button(
            btn_frame,
            text="🗑️ Excluir Tarefa",
            font=("Arial", 11, "bold"),
            bg="#ef4444",
            fg="white",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.excluir_tarefa
        )
        btn_excluir_tarefa.pack(side="left", padx=5)
        
        self.carregar_tarefas()
    
    def mostrar_busca(self, frame):
        """Mostra a tela de busca avançada"""
        # Formulário de busca
        busca_frame = tk.Frame(frame, bg="white", relief="solid", bd=1)
        busca_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            busca_frame,
            text="🔍 Busca Avançada de Processos",
            font=("Arial", 16, "bold"),
            bg="white",
            fg=self.cor_texto
        ).pack(pady=15)
        
        campos_frame = tk.Frame(busca_frame, bg="white")
        campos_frame.pack(padx=30, pady=(0, 20))
        
        # Linha 1
        linha1 = tk.Frame(campos_frame, bg="white")
        linha1.pack(fill="x", pady=5)
        
        tk.Label(linha1, text="Número do Processo:", bg="white", font=("Arial", 10)).pack(side="left")
        self.entry_busca_numero = tk.Entry(linha1, font=("Arial", 10), width=30)
        self.entry_busca_numero.pack(side="left", padx=(10, 30))
        
        tk.Label(linha1, text="Cliente:", bg="white", font=("Arial", 10)).pack(side="left")
        self.entry_busca_cliente = tk.Entry(linha1, font=("Arial", 10), width=30)
        self.entry_busca_cliente.pack(side="left", padx=10)
        
        # Linha 2
        linha2 = tk.Frame(campos_frame, bg="white")
        linha2.pack(fill="x", pady=5)
        
        tk.Label(linha2, text="Tipo de Ação:", bg="white", font=("Arial", 10)).pack(side="left")
        self.combo_busca_tipo = ttk.Combobox(linha2, font=("Arial", 10), width=28, state="readonly")
        self.combo_busca_tipo['values'] = ('Todos', 'Trabalhista', 'Cível', 'Criminal', 'Tributário', 'Família', 'Previdenciário')
        self.combo_busca_tipo.current(0)
        self.combo_busca_tipo.pack(side="left", padx=(10, 30))
        
        tk.Label(linha2, text="Status:", bg="white", font=("Arial", 10)).pack(side="left")
        self.combo_busca_status = ttk.Combobox(linha2, font=("Arial", 10), width=28, state="readonly")
        self.combo_busca_status['values'] = ('Todos', 'Ativo', 'Arquivado', 'Finalizado')
        self.combo_busca_status.current(0)
        self.combo_busca_status.pack(side="left", padx=10)
        
        # Botão de buscar
        btn_buscar = tk.Button(
            busca_frame,
            text="🔍 Buscar",
            font=("Arial", 12, "bold"),
            bg=self.cor_primaria,
            fg="white",
            bd=0,
            padx=40,
            pady=10,
            cursor="hand2",
            command=self.realizar_busca
        )
        btn_buscar.pack(pady=(0, 15))
        
        # Resultados
        resultado_frame = tk.Frame(frame, bg="white", relief="solid", bd=1)
        resultado_frame.pack(fill="both", expand=True)
        
        tk.Label(
            resultado_frame,
            text="📋 Resultados da Busca",
            font=("Arial", 16, "bold"),
            bg="white",
            fg=self.cor_texto
        ).pack(pady=15)
        
        tree_frame = tk.Frame(resultado_frame, bg="white")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        colunas = ("Número", "Cliente", "Tipo", "Status", "Vara", "Data")
        self.tree_busca = ttk.Treeview(
            tree_frame,
            columns=colunas,
            show="headings",
            yscrollcommand=scrollbar.set,
            height=12
        )
        scrollbar.config(command=self.tree_busca.yview)
        
        self.tree_busca.heading("Número", text="Número")
        self.tree_busca.heading("Cliente", text="Cliente")
        self.tree_busca.heading("Tipo", text="Tipo")
        self.tree_busca.heading("Status", text="Status")
        self.tree_busca.heading("Vara", text="Vara")
        self.tree_busca.heading("Data", text="Data Dist.")
        
        self.tree_busca.column("Número", width=180)
        self.tree_busca.column("Cliente", width=180)
        self.tree_busca.column("Tipo", width=120)
        self.tree_busca.column("Status", width=100)
        self.tree_busca.column("Vara", width=200)
        self.tree_busca.column("Data", width=100)
        
        self.tree_busca.pack(fill="both", expand=True)
        
        self.tree_busca.bind("<Double-1>", lambda e: self.abrir_detalhes_busca())
    
    def mostrar_backup(self, frame):
        """Mostra a tela de backup e restauração"""
        # Card de backup
        backup_frame = tk.Frame(frame, bg="white", relief="solid", bd=1)
        backup_frame.pack(fill="x", pady=(0, 20), ipady=30)
        
        tk.Label(
            backup_frame,
            text="💾 Backup do Banco de Dados",
            font=("Arial", 18, "bold"),
            bg="white",
            fg=self.cor_texto
        ).pack(pady=20)
        
        tk.Label(
            backup_frame,
            text="Faça backup regular dos seus dados para evitar perdas!\n\nO backup irá copiar o banco de dados completo para um local seguro.",
            font=("Arial", 11),
            bg="white",
            fg="#6b7280",
            justify="center"
        ).pack(pady=10)
        
        btn_backup = tk.Button(
            backup_frame,
            text="💾 Fazer Backup Agora",
            font=("Arial", 14, "bold"),
            bg="#10b981",
            fg="white",
            bd=0,
            padx=40,
            pady=15,
            cursor="hand2",
            command=self.fazer_backup
        )
        btn_backup.pack(pady=20)
        
        # Card de restauração
        restaurar_frame = tk.Frame(frame, bg="white", relief="solid", bd=1)
        restaurar_frame.pack(fill="both", expand=True, ipady=30)
        
        tk.Label(
            restaurar_frame,
            text="📥 Restaurar Banco de Dados",
            font=("Arial", 18, "bold"),
            bg="white",
            fg=self.cor_texto
        ).pack(pady=20)
        
        tk.Label(
            restaurar_frame,
            text="Restaure um backup anterior do banco de dados.\n\n⚠️ ATENÇÃO: Esta ação irá substituir todos os dados atuais!",
            font=("Arial", 11),
            bg="white",
            fg="#6b7280",
            justify="center"
        ).pack(pady=10)
        
        btn_restaurar = tk.Button(
            restaurar_frame,
            text="📥 Restaurar Backup",
            font=("Arial", 14, "bold"),
            bg="#ef4444",
            fg="white",
            bd=0,
            padx=40,
            pady=15,
            cursor="hand2",
            command=self.restaurar_backup
        )
        btn_restaurar.pack(pady=20)
        
        # Informações
        info_frame = tk.Frame(frame, bg="#f0f9ff", relief="solid", bd=1)
        info_frame.pack(fill="x", pady=20)
        
        tk.Label(
            info_frame,
            text="ℹ️ Informações do Sistema",
            font=("Arial", 12, "bold"),
            bg="#f0f9ff",
            fg=self.cor_texto
        ).pack(pady=10, padx=20, anchor="w")
        
        # Tamanho do banco
        try:
            tamanho_kb = os.path.getsize('sistema_juridico.db') / 1024
            tamanho_texto = f"{tamanho_kb:.2f} KB"
        except:
            tamanho_texto = "N/A"
        
        tk.Label(
            info_frame,
            text=f"📊 Tamanho do banco de dados: {tamanho_texto}",
            font=("Arial", 10),
            bg="#f0f9ff",
            fg=self.cor_texto
        ).pack(pady=5, padx=20, anchor="w")
        
        tk.Label(
            info_frame,
            text=f"📁 Localização: {os.path.abspath('sistema_juridico.db')}",
            font=("Arial", 10),
            bg="#f0f9ff",
            fg=self.cor_texto
        ).pack(pady=(0, 15), padx=20, anchor="w")
    
    # ========== FUNÇÕES DE OPERAÇÃO ==========
    
    def salvar_processo(self):
        """Salva um novo processo"""
        if not self.entry_numero.get().strip():
            messagebox.showerror("Erro", "O número do processo é obrigatório!")
            return
        
        if not self.combo_cliente_processo.get().strip():
            messagebox.showerror("Erro", "O nome do cliente é obrigatório!")
            return
        
        if not self.entry_vara.get().strip():
            messagebox.showerror("Erro", "A vara/comarca é obrigatória!")
            return
        
        try:
            valor_causa = float(self.entry_valor.get().replace(",", "."))
        except:
            messagebox.showerror("Erro", "Valor da causa inválido!")
            return
        
        numero = self.entry_numero.get().strip()
        cliente = self.combo_cliente_processo.get().strip()
        tipo_acao = self.combo_tipo.get()
        vara = self.entry_vara.get().strip()
        status = self.combo_status.get()
        data_distribuicao = self.entry_data.get()
        observacoes = self.text_obs.get("1.0", "end-1c")
        data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            self.cursor.execute('''
                INSERT INTO processos 
                (numero, cliente, tipo_acao, vara, status, data_distribuicao, valor_causa, observacoes, data_cadastro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (numero, cliente, tipo_acao, vara, status, data_distribuicao, valor_causa, observacoes, data_cadastro))
            
            self.conn.commit()
            
            messagebox.showinfo("Sucesso", "Processo cadastrado com sucesso!")
            
            self.entry_numero.delete(0, tk.END)
            self.combo_cliente_processo.set('')
            self.entry_vara.delete(0, tk.END)
            self.entry_valor.delete(0, tk.END)
            self.entry_valor.insert(0, "0.00")
            self.text_obs.delete("1.0", tk.END)
            
            self.carregar_processos()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Já existe um processo com este número!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar processo: {str(e)}")
    
    def salvar_cliente(self):
        """Salva um novo cliente"""
        if not self.entry_nome_cliente.get().strip():
            messagebox.showerror("Erro", "O nome do cliente é obrigatório!")
            return
        
        nome = self.entry_nome_cliente.get().strip()
        cpf_cnpj = self.entry_cpf_cliente.get().strip()
        telefone = self.entry_tel_cliente.get().strip()
        email = self.entry_email_cliente.get().strip()
        endereco = self.entry_end_cliente.get().strip()
        observacoes = self.text_obs_cliente.get("1.0", "end-1c")
        data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            self.cursor.execute('''
                INSERT INTO clientes
                (nome, cpf_cnpj, telefone, email, endereco, observacoes, data_cadastro)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nome, cpf_cnpj, telefone, email, endereco, observacoes, data_cadastro))
            
            self.conn.commit()
            
            messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
            
            self.entry_nome_cliente.delete(0, tk.END)
            self.entry_cpf_cliente.delete(0, tk.END)
            self.entry_tel_cliente.delete(0, tk.END)
            self.entry_email_cliente.delete(0, tk.END)
            self.entry_end_cliente.delete(0, tk.END)
            self.text_obs_cliente.delete("1.0", tk.END)
            
            self.carregar_clientes()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Já existe um cliente com este CPF/CNPJ!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar cliente: {str(e)}")
    
    def salvar_tarefa(self):
        """Salva uma nova tarefa"""
        if not self.entry_titulo_tarefa.get().strip():
            messagebox.showerror("Erro", "O título da tarefa é obrigatório!")
            return
        
        titulo = self.entry_titulo_tarefa.get().strip()
        tipo = self.combo_tipo_tarefa.get()
        descricao = self.text_desc_tarefa.get("1.0", "end-1c")
        data_vencimento_str = self.entry_data_tarefa.get()
        
        try:
            data_vencimento = datetime.strptime(data_vencimento_str, "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M")
        except:
            messagebox.showerror("Erro", "Data/hora inválida! Use: DD/MM/AAAA HH:MM")
            return
        
        processo_selecionado = self.combo_processo_tarefa.get()
        processo_id = None
        
        if processo_selecionado != "Nenhum (tarefa geral)":
            self.cursor.execute("SELECT id FROM processos WHERE numero = ?", (processo_selecionado,))
            resultado = self.cursor.fetchone()
            if resultado:
                processo_id = resultado[0]
        
        data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            self.cursor.execute('''
                INSERT INTO tarefas
                (processo_id, titulo, descricao, tipo, data_vencimento, data_cadastro)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (processo_id, titulo, descricao, tipo, data_vencimento, data_cadastro))
            
            self.conn.commit()
            
            messagebox.showinfo("Sucesso", "Tarefa cadastrada com sucesso!")
            
            self.entry_titulo_tarefa.delete(0, tk.END)
            self.text_desc_tarefa.delete("1.0", tk.END)
            self.combo_processo_tarefa.current(0)
            self.entry_data_tarefa.delete(0, tk.END)
            self.entry_data_tarefa.insert(0, datetime.now().strftime("%d/%m/%Y %H:%M"))
            
            self.carregar_tarefas()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar tarefa: {str(e)}")
    
    def carregar_processos(self):
        """Carrega os processos"""
        for item in self.tree_processos.get_children():
            self.tree_processos.delete(item)
        
        self.cursor.execute('''
            SELECT numero, cliente, tipo_acao, status, data_distribuicao 
            FROM processos 
            ORDER BY data_cadastro DESC
        ''')
        
        processos = self.cursor.fetchall()
        
        for processo in processos:
            self.tree_processos.insert("", "end", values=processo)
    
    def carregar_clientes(self):
        """Carrega os clientes"""
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        
        self.cursor.execute('''
            SELECT c.nome, c.cpf_cnpj, c.telefone, c.email, 
                   (SELECT COUNT(*) FROM processos p WHERE p.cliente = c.nome) as num_processos
            FROM clientes c
            ORDER BY c.nome
        ''')
        
        clientes = self.cursor.fetchall()
        
        for cliente in clientes:
            self.tree_clientes.insert("", "end", values=cliente)
    
    def carregar_tarefas(self):
        """Carrega as tarefas"""
        for item in self.tree_tarefas.get_children():
            self.tree_tarefas.delete(item)
        
        filtro = self.combo_filtro_tarefa.get()
        
        if filtro == "Pendentes":
            where_clause = "WHERE t.concluida=0"
        elif filtro == "Concluídas":
            where_clause = "WHERE t.concluida=1"
        elif filtro == "Atrasadas":
            agora = datetime.now().strftime("%Y-%m-%d %H:%M")
            where_clause = f"WHERE t.concluida=0 AND t.data_vencimento < '{agora}'"
        else:
            where_clause = ""
        
        self.cursor.execute(f'''
            SELECT t.id, t.titulo, t.tipo, t.data_vencimento, t.concluida, p.numero
            FROM tarefas t
            LEFT JOIN processos p ON t.processo_id = p.id
            {where_clause}
            ORDER BY t.data_vencimento ASC
        ''')
        
        tarefas = self.cursor.fetchall()
        
        for tarefa_id, titulo, tipo, vencimento, concluida, numero_processo in tarefas:
            try:
                data_venc = datetime.strptime(vencimento, "%Y-%m-%d %H:%M")
                venc_formatado = data_venc.strftime("%d/%m/%Y %H:%M")
                
                if concluida:
                    status = "✓"
                else:
                    if data_venc < datetime.now():
                        status = "⚠️"
                    else:
                        status = "⏳"
                
                processo_texto = numero_processo if numero_processo else "-"
                
                self.tree_tarefas.insert("", "end", values=(status, titulo, tipo, venc_formatado, processo_texto), tags=(tarefa_id,))
            except:
                pass
    
    def realizar_busca(self):
        """Realiza busca avançada de processos"""
        for item in self.tree_busca.get_children():
            self.tree_busca.delete(item)
        
        numero = self.entry_busca_numero.get().strip()
        cliente = self.entry_busca_cliente.get().strip()
        tipo = self.combo_busca_tipo.get()
        status = self.combo_busca_status.get()
        
        # Construir query
        query = "SELECT numero, cliente, tipo_acao, status, vara, data_distribuicao FROM processos WHERE 1=1"
        params = []
        
        if numero:
            query += " AND numero LIKE ?"
            params.append(f"%{numero}%")
        
        if cliente:
            query += " AND cliente LIKE ?"
            params.append(f"%{cliente}%")
        
        if tipo != "Todos":
            query += " AND tipo_acao = ?"
            params.append(tipo)
        
        if status != "Todos":
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY data_cadastro DESC"
        
        self.cursor.execute(query, params)
        resultados = self.cursor.fetchall()
        
        if not resultados:
            messagebox.showinfo("Busca", "Nenhum processo encontrado com os critérios informados.")
        else:
            for resultado in resultados:
                self.tree_busca.insert("", "end", values=resultado)
            
            messagebox.showinfo("Busca", f"{len(resultados)} processo(s) encontrado(s)!")
    
    def fazer_backup(self):
        """Faz backup do banco de dados"""
        try:
            arquivo_destino = filedialog.asksaveasfilename(
                title="Salvar backup",
                defaultextension=".db",
                filetypes=[("Banco de Dados", "*.db"), ("Todos os arquivos", "*.*")],
                initialfile=f"backup_sistema_juridico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            )
            
            if arquivo_destino:
                # Fechar conexão temporariamente
                self.conn.close()
                
                # Copiar arquivo
                shutil.copy2('sistema_juridico.db', arquivo_destino)
                
                # Reabrir conexão
                self.conn = sqlite3.connect('sistema_juridico.db')
                self.cursor = self.conn.cursor()
                
                messagebox.showinfo("Sucesso", f"Backup realizado com sucesso!\n\nArquivo salvo em:\n{arquivo_destino}")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao fazer backup: {str(e)}")
    
    def restaurar_backup(self):
        """Restaura um backup do banco de dados"""
        resposta = messagebox.askyesno(
            "Confirmar Restauração",
            "⚠️ ATENÇÃO!\n\nEsta ação irá substituir TODOS os dados atuais pelo backup selecionado.\n\nDeseja continuar?"
        )
        
        if not resposta:
            return
        
        try:
            arquivo_origem = filedialog.askopenfilename(
                title="Selecionar backup",
                filetypes=[("Banco de Dados", "*.db"), ("Todos os arquivos", "*.*")]
            )
            
            if arquivo_origem:
                # Fechar conexão
                self.conn.close()
                
                # Fazer backup do arquivo atual antes de substituir
                backup_atual = f"sistema_juridico_antes_restauracao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                shutil.copy2('sistema_juridico.db', backup_atual)
                
                # Substituir pelo backup
                shutil.copy2(arquivo_origem, 'sistema_juridico.db')
                
                # Reabrir conexão
                self.conn = sqlite3.connect('sistema_juridico.db')
                self.cursor = self.conn.cursor()
                
                messagebox.showinfo(
                    "Sucesso",
                    f"Backup restaurado com sucesso!\n\nUm backup dos dados anteriores foi salvo em:\n{backup_atual}\n\nO sistema será reiniciado."
                )
                
                # Recarregar tela
                self.mostrar_tela("dashboard")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao restaurar backup: {str(e)}")
    
    def concluir_tarefa(self):
        """Marca tarefa como concluída"""
        selecao = self.tree_tarefas.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione uma tarefa!")
            return
        
        tarefa_id = self.tree_tarefas.item(selecao[0])['tags'][0]
        data_conclusao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            self.cursor.execute('''
                UPDATE tarefas 
                SET concluida=1, data_conclusao=?
                WHERE id=?
            ''', (data_conclusao, tarefa_id))
            
            self.conn.commit()
            
            messagebox.showinfo("Sucesso", "Tarefa marcada como concluída!")
            self.carregar_tarefas()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")
    
    def excluir_tarefa(self):
        """Exclui uma tarefa"""
        selecao = self.tree_tarefas.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione uma tarefa!")
            return
        
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta tarefa?"):
            return
        
        tarefa_id = self.tree_tarefas.item(selecao[0])['tags'][0]
        
        try:
            self.cursor.execute("DELETE FROM tarefas WHERE id=?", (tarefa_id,))
            self.conn.commit()
            
            messagebox.showinfo("Sucesso", "Tarefa excluída!")
            self.carregar_tarefas()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")
    
    def excluir_processo(self):
        """Exclui um processo"""
        selecao = self.tree_processos.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um processo!")
            return
        
        if not messagebox.askyesno("Confirmar", "Tem certeza? Todos os andamentos e tarefas vinculadas também serão excluídos!"):
            return
        
        item = self.tree_processos.item(selecao[0])
        numero_processo = item['values'][0]
        
        try:
            self.cursor.execute("SELECT id FROM processos WHERE numero = ?", (numero_processo,))
            processo_id = self.cursor.fetchone()[0]
            
            self.cursor.execute("DELETE FROM andamentos WHERE processo_id = ?", (processo_id,))
            self.cursor.execute("DELETE FROM tarefas WHERE processo_id = ?", (processo_id,))
            self.cursor.execute("DELETE FROM processos WHERE id = ?", (processo_id,))
            
            self.conn.commit()
            
            messagebox.showinfo("Sucesso", "Processo excluído!")
            self.carregar_processos()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")
    
    def excluir_cliente(self):
        """Exclui um cliente"""
        selecao = self.tree_clientes.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um cliente!")
            return
        
        item = self.tree_clientes.item(selecao[0])
        nome_cliente = item['values'][0]
        num_processos = item['values'][4]
        
        if num_processos > 0:
            messagebox.showerror("Erro", f"Este cliente possui {num_processos} processo(s) cadastrado(s).\n\nExclua os processos antes de excluir o cliente!")
            return
        
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este cliente?"):
            return
        
        try:
            self.cursor.execute("DELETE FROM clientes WHERE nome = ?", (nome_cliente,))
            self.conn.commit()
            
            messagebox.showinfo("Sucesso", "Cliente excluído!")
            self.carregar_clientes()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")
    
    def ver_processos_cliente(self):
        """Mostra processos de um cliente"""
        selecao = self.tree_clientes.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um cliente!")
            return
        
        item = self.tree_clientes.item(selecao[0])
        nome_cliente = item['values'][0]
        
        # Ir para busca e filtrar
        self.mostrar_tela("busca")
        self.entry_busca_cliente.delete(0, tk.END)
        self.entry_busca_cliente.insert(0, nome_cliente)
        self.realizar_busca()
    
    def abrir_detalhes_processo(self):
        """Abre detalhes do processo"""
        selecao = self.tree_processos.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um processo!")
            return
        
        item = self.tree_processos.item(selecao[0])
        numero_processo = item['values'][0]
        
        self.cursor.execute('''
            SELECT id, numero, cliente, tipo_acao, vara, status, 
                   data_distribuicao, valor_causa, observacoes
            FROM processos 
            WHERE numero = ?
        ''', (numero_processo,))
        
        processo = self.cursor.fetchone()
        if not processo:
            messagebox.showerror("Erro", "Processo não encontrado!")
            return
        
        # Criar janela de detalhes
        janela = tk.Toplevel(self.root)
        janela.title(f"Detalhes - {numero_processo}")
        janela.geometry("900x600")
        janela.configure(bg=self.cor_fundo)
        
        # Header
        header = tk.Frame(janela, bg=self.cor_primaria, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text=f"📁 {numero_processo}",
            font=("Arial", 18, "bold"),
            bg=self.cor_primaria,
            fg="white"
        ).pack(side="left", padx=20, pady=20)
        
        main_container = tk.Frame(janela, bg=self.cor_fundo)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Informações
        info_frame = tk.Frame(main_container, bg="white", relief="solid", bd=1)
        info_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            info_frame,
            text="ℹ️ Informações do Processo",
            font=("Arial", 14, "bold"),
            bg="white",
            fg=self.cor_texto
        ).pack(pady=10)
        
        info_grid = tk.Frame(info_frame, bg="white")
        info_grid.pack(padx=20, pady=(0, 15))
        
        dados = [
            ("Cliente:", processo[2]),
            ("Tipo:", processo[3]),
            ("Vara:", processo[4]),
            ("Status:", processo[5]),
            ("Data Dist.:", processo[6]),
            ("Valor:", f"R$ {processo[7]:,.2f}"),
        ]
        
        for i, (label, valor) in enumerate(dados):
            row = i // 2
            col = (i % 2) * 2
            
            tk.Label(
                info_grid,
                text=label,
                font=("Arial", 10, "bold"),
                bg="white",
                fg=self.cor_texto
            ).grid(row=row, column=col, sticky="w", padx=10, pady=5)
            
            tk.Label(
                info_grid,
                text=valor,
                font=("Arial", 10),
                bg="white",
                fg=self.cor_texto
            ).grid(row=row, column=col+1, sticky="w", padx=10, pady=5)
        
        if processo[8]:
            tk.Label(
                info_frame,
                text="Observações:",
                font=("Arial", 10, "bold"),
                bg="white",
                fg=self.cor_texto
            ).pack(anchor="w", padx=20)
            
            tk.Label(
                info_frame,
                text=processo[8],
                font=("Arial", 10),
                bg="white",
                fg=self.cor_texto,
                wraplength=800,
                justify="left"
            ).pack(anchor="w", padx=20, pady=(0, 15))
        
        # Andamentos
        andamentos_frame = tk.Frame(main_container, bg="white", relief="solid", bd=1)
        andamentos_frame.pack(fill="both", expand=True)
        
        tk.Label(
            andamentos_frame,
            text="📜 Andamentos Processuais",
            font=("Arial", 14, "bold"),
            bg="white",
            fg=self.cor_texto
        ).pack(pady=10)
        
        novo_and_frame = tk.Frame(andamentos_frame, bg="#f0f9ff")
        novo_and_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(
            novo_and_frame,
            text="Adicionar novo andamento:",
            font=("Arial", 10, "bold"),
            bg="#f0f9ff"
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        text_novo_and = tk.Text(novo_and_frame, font=("Arial", 10), height=3)
        text_novo_and.pack(fill="x", padx=10, pady=5)
        
        btn_add_and = tk.Button(
            novo_and_frame,
            text="➕ Adicionar",
            font=("Arial", 10, "bold"),
            bg=self.cor_primaria,
            fg="white",
            bd=0,
            padx=15,
            pady=5,
            cursor="hand2",
            command=lambda: self.adicionar_andamento(processo[0], text_novo_and, lista_and_frame)
        )
        btn_add_and.pack(pady=10)
        
        lista_and_frame = tk.Frame(andamentos_frame, bg="white")
        lista_and_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        canvas = tk.Canvas(lista_and_frame, bg="white", highlightthickness=0)
        scrollbar_and = ttk.Scrollbar(lista_and_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_and.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_and.pack(side="right", fill="y")
        
        self.carregar_andamentos(processo[0], scrollable_frame)
    
    def abrir_detalhes_busca(self):
        """Abre detalhes de processo pela busca"""
        selecao = self.tree_busca.selection()
        if not selecao:
            return
        
        item = self.tree_busca.item(selecao[0])
        numero_processo = item['values'][0]
        
        # Mesmo código do abrir_detalhes_processo mas usando numero_processo
        self.cursor.execute('''
            SELECT id, numero, cliente, tipo_acao, vara, status, 
                   data_distribuicao, valor_causa, observacoes
            FROM processos 
            WHERE numero = ?
        ''', (numero_processo,))
        
        processo = self.cursor.fetchone()
        if not processo:
            return
        
        # [restante do código igual ao abrir_detalhes_processo]
        messagebox.showinfo("Detalhes", f"Processo: {numero_processo}\n\nClique em 'Ver Detalhes' na tela de Processos para ver todos os andamentos.")
    
    def adicionar_andamento(self, processo_id, text_widget, lista_frame):
        """Adiciona andamento"""
        descricao = text_widget.get("1.0", "end-1c").strip()
        
        if not descricao:
            messagebox.showwarning("Aviso", "Digite a descrição!")
            return
        
        data_andamento = datetime.now().strftime("%d/%m/%Y %H:%M")
        data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            self.cursor.execute('''
                INSERT INTO andamentos (processo_id, data_andamento, descricao, data_cadastro)
                VALUES (?, ?, ?, ?)
            ''', (processo_id, data_andamento, descricao, data_cadastro))
            
            self.conn.commit()
            
            messagebox.showinfo("Sucesso", "Andamento adicionado!")
            
            text_widget.delete("1.0", tk.END)
            self.carregar_andamentos(processo_id, lista_frame)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")
    
    def carregar_andamentos(self, processo_id, frame):
        """Carrega andamentos"""
        for widget in frame.winfo_children():
            widget.destroy()
        
        self.cursor.execute('''
            SELECT data_andamento, descricao
            FROM andamentos
            WHERE processo_id = ?
            ORDER BY data_cadastro DESC
        ''', (processo_id,))
        
        andamentos = self.cursor.fetchall()
        
        if not andamentos:
            tk.Label(
                frame,
                text="📭 Nenhum andamento registrado",
                font=("Arial", 11),
                bg="white",
                fg="#6b7280"
            ).pack(pady=30)
        else:
            for data, descricao in andamentos:
                and_card = tk.Frame(frame, bg="#f0f9ff", relief="solid", bd=1)
                and_card.pack(fill="x", pady=5)
                
                tk.Label(
                    and_card,
                    text=f"📅 {data}",
                    font=("Arial", 9, "bold"),
                    bg="#f0f9ff",
                    fg=self.cor_primaria
                ).pack(anchor="w", padx=15, pady=(10, 5))
                
                tk.Label(
                    and_card,
                    text=descricao,
                    font=("Arial", 10),
                    bg="#f0f9ff",
                    fg=self.cor_texto,
                    wraplength=700,
                    justify="left"
                ).pack(anchor="w", padx=15, pady=(0, 10))
    
    def sair_aplicacao(self):
        """Sai da aplicação"""
        self.conn.close()
        print("👋 Encerrando...")
        self.root.quit()

# Inicializar
if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaJuridico(root)
    root.mainloop()