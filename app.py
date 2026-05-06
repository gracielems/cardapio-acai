import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager
import urllib.parse

# --- ⚙️ 1. CONFIGURAÇÕES E PREÇOS ---
PRECOS_COMBOS = {
    "🍫 Laka Oreo (500ml)": 28.00,
    "🍓 Clássico Morango (500ml)": 27.00,
    "⭐ Nutella Premium (500ml)": 34.00,
}
PRECOS_GARRAFAS = {
    "🥤 Tradicional": 10.00,
    "🥤 Leite em Pó": 13.00,
    "🥤 Morango": 13.00,
    "🥤 Maracujá": 13.00,
}
PRECOS_COPOS = {"300ml": 13.0, "500ml": 18.0, "700ml": 23.0, "1 Litro": 32.0}
VALOR_ADICIONAL = 3.00

# --- 🔐 SENHA: lida de variável de ambiente ou st.secrets ---
# No Streamlit Cloud: adicione SENHA_DONO em Settings > Secrets
# Localmente: crie um arquivo .env ou defina a variável no terminal
try:
    SENHA_DONO = st.secrets["SENHA_DONO"]
except Exception:
    SENHA_DONO = os.environ.get("SENHA_DONO", "")

NOME_IMAGEM_LOGO = "logo3d.jpg.png"
NOME_IMAGEM_MONTE = "download (1).jpg"
DB_NAME = "jubileu_database.db"


# --- 🛠️ 2. FUNÇÕES DO BANCO DE DADOS (SQLite) ---

@contextmanager
def get_db():
    """Context manager central para conexões SQLite.
    Garante commit em caso de sucesso, rollback em erro, e close sempre."""
    conn = sqlite3.connect(DB_NAME)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS vendas
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       data TEXT, cliente TEXT, telefone TEXT, total REAL, itens TEXT)''')
        # Migração segura: adiciona coluna telefone se já existir banco antigo sem ela
        try:
            c.execute("ALTER TABLE vendas ADD COLUMN telefone TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass  # Coluna já existe, tudo certo
        c.execute('''CREATE TABLE IF NOT EXISTS fidelidade
                      (nome TEXT PRIMARY KEY, pedidos INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS config
                      (chave TEXT PRIMARY KEY, valor TEXT)''')
        c.execute("INSERT OR IGNORE INTO config (chave, valor) VALUES ('status_loja', 'ABERTA')")


def get_status_loja():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT valor FROM config WHERE chave = 'status_loja'")
        res = c.fetchone()
    return res[0] == "ABERTA" if res else True


def set_status_loja(status):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("UPDATE config SET valor = ? WHERE chave = 'status_loja'", (status,))


def registrar_venda_db(nome, telefone, total, itens):
    data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
    with get_db() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO vendas (data, cliente, telefone, total, itens) VALUES (?, ?, ?, ?, ?)",
            (data_hoje, nome, telefone, total, itens),
        )


def carregar_fidelidade_db(nome):
    nome = nome.strip().upper()
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT pedidos FROM fidelidade WHERE nome = ?", (nome,))
        res = c.fetchone()
    return res[0] if res else 0


def atualizar_fidelidade_db(nome, brinde):
    nome = nome.strip().upper()
    atual = carregar_fidelidade_db(nome)
    nova_qtd = 0 if brinde else atual + 1
    with get_db() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO fidelidade (nome, pedidos) VALUES (?, ?)",
            (nome, nova_qtd),
        )


init_db()


# --- 🎨 3. INTERFACE E ESTILO ---
st.set_page_config(page_title="Jubileu Açaí", page_icon="🍧")

st.markdown("""
<style>
    .secao { color: #4B0082 !important; font-weight: bold; border-bottom: 2px solid #4B0082; padding-bottom: 5px; margin-top: 20px; }
    .btn-whats { background: linear-gradient(90deg, #25D366 0%, #128C7E 100%); color: white !important; padding: 15px; text-align: center; border-radius: 12px; font-weight: bold; text-decoration: none; display: block; margin-top: 10px; }
    .check-out { background-color: #f9f9f9; padding: 15px; border-radius: 10px; border: 1px solid #ddd; margin-top: 15px; }
</style>
""", unsafe_allow_html=True)

if "admin_logado" not in st.session_state:
    st.session_state.admin_logado = False


# --- 🍧 4. ÁREA DO CLIENTE ---
if not st.session_state.admin_logado:
    if os.path.exists(NOME_IMAGEM_LOGO):
        st.image(NOME_IMAGEM_LOGO, use_container_width=True)

    # Status lido a cada rerun para refletir mudanças em tempo real
    loja_aberta = get_status_loja()

    if not loja_aberta:
        st.error("🔴 DESCULPE, ESTAMOS FECHADOS NO MOMENTO")
    else:
        st.success("🟢 ESTAMOS ABERTOS! PEÇA JÁ O SEU.")

    itens_pedido = []
    total_itens = 0.0
    tab1, tab2, tab3 = st.tabs(["🔥 Combos", "🥤 Na Garrafa", "🍧 Monte o Seu"])

    with tab1:
        for n, p in PRECOS_COMBOS.items():
            if st.checkbox(f"{n} - R$ {p:.2f}", key=f"c_{n}"):
                itens_pedido.append(n)
                total_itens += p

    with tab2:
        for n, p in PRECOS_GARRAFAS.items():
            if st.checkbox(f"{n} - R$ {p:.2f}", key=f"g_{n}"):
                itens_pedido.append(n)
                total_itens += p

    with tab3:
        if os.path.exists(NOME_IMAGEM_MONTE):
            st.image(NOME_IMAGEM_MONTE, width=200)

        st.markdown('<div class="secao">1. TAMANHO</div>', unsafe_allow_html=True)
        esc = st.selectbox("Selecione o tamanho:", list(PRECOS_COPOS.keys()), index=None)
        if esc:
            total_itens += PRECOS_COPOS[esc]
            itens_pedido.append(f"Copo {esc}")
            st.markdown('<div class="secao">2. ADICIONAIS (R$ 3,00)</div>', unsafe_allow_html=True)
            for e in ["Banana", "Morango", "Leite em Pó", "Paçoca", "Nutella", "Chantilly", "Granola", "Oreo"]:
                if st.checkbox(e, key=f"e_{e}"):
                    itens_pedido.append(f"Add {e}")
                    total_itens += VALOR_ADICIONAL

    st.markdown('<div class="secao">IDENTIFICAÇÃO E ENTREGA (Frete Grátis)</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    np_ = c1.text_input("Seu Nome:").strip()
    sp_ = c2.text_input("Sobrenome:").strip()
    nome_completo = f"{np_} {sp_}".upper().strip()

    telefone = st.text_input("📱 WhatsApp / Telefone:", placeholder="(37) 99999-9999").strip()

    brinde_ativo = False
    if np_ and sp_:
        q = carregar_fidelidade_db(nome_completo)
        if q >= 9:
            st.success("🎁 PARABÉNS! Seu próximo açaí é um BRINDE!")
            brinde_ativo = True
        else:
            st.write(f"Sua Fidelidade: **{q}/10**")
            st.progress(q / 10)

    col_rua, col_num = st.columns([3, 1])
    rua = col_rua.text_input("Rua:")
    numero = col_num.text_input("Nº:")
    bairro = st.text_input("Bairro:")

    pag = st.selectbox("Pagamento:", ["Pix", "Cartão", "Dinheiro"])
    troco_msg = ""
    if pag == "Dinheiro" and st.radio("Precisa de troco?", ["Não", "Sim"], horizontal=True) == "Sim":
        v = st.text_input("Troco para quanto?")
        troco_msg = f" (Troco para {v})"

    total_final = 0.00 if brinde_ativo else total_itens

    if total_itens > 0:
        st.markdown('<div class="check-out">', unsafe_allow_html=True)
        st.subheader("Resumo do Pedido")
        for item in itens_pedido:
            st.write(f"• {item}")
        if brinde_ativo:
            st.write("🎁 **Brinde Fidelidade Aplicado!**")
        st.write(f"**TOTAL: R$ {total_final:.2f}**")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("✅ FINALIZAR PEDIDO", disabled=not loja_aberta):
            if not (np_ and rua and numero and bairro):
                st.warning("Preencha nome e endereço completo (incluindo número)!")
            elif not telefone:
                st.warning("Preencha o campo de telefone para contato!")
            elif not itens_pedido:
                st.warning("Adicione pelo menos um item ao pedido!")
            else:
                registrar_venda_db(nome_completo, telefone, total_final, ", ".join(itens_pedido))
                atualizar_fidelidade_db(nome_completo, brinde_ativo)
                msg = (
                    f"*NOVO PEDIDO JUBILEU AÇAÍ*\n------------------\n"
                    f"*Cliente:* {nome_completo}\n"
                    f"*Telefone:* {telefone}\n"
                    f"*Endereço:* {rua}, {numero} - {bairro}\n------------------\n"
                    f"*Itens:* {', '.join(itens_pedido)}\n"
                    f"*Pagamento:* {pag}{troco_msg}\n"
                    f"*TOTAL: R$ {total_final:.2f}*"
                )
                link = f"https://wa.me/5537991031933?text={urllib.parse.quote(msg)}"
                st.markdown(
                    f'<a href="{link}" target="_blank" class="btn-whats">🚀 ENVIAR PARA O WHATSAPP</a>',
                    unsafe_allow_html=True,
                )

    # --- 🔐 ACESSO DISCRETO ---
    st.markdown("---")
    if st.button("v1.5", help="Informações do Sistema"):
        st.session_state.admin_logado = "solicitar_senha"
        st.rerun()


# --- 🔐 5. PAINEL DO DONO ---
if st.session_state.admin_logado == "solicitar_senha":
    senha = st.text_input("Senha de Acesso:", type="password")
    if st.button("Entrar"):
        if not SENHA_DONO:
            st.error("Senha não configurada no servidor. Contate o administrador.")
        elif senha == SENHA_DONO:
            st.session_state.admin_logado = True
            st.rerun()
        else:
            st.error("Acesso negado!")
    if st.button("Voltar"):
        st.session_state.admin_logado = False
        st.rerun()

if st.session_state.admin_logado is True:
    st.title("📊 Gestão Jubileu Açaí")

    loja_aberta = get_status_loja()
    col_st1, col_st2 = st.columns(2)
    if col_st1.button("🟢 ABRIR LOJA"):
        set_status_loja("ABERTA")
        st.rerun()
    if col_st2.button("🔴 FECHAR LOJA"):
        set_status_loja("FECHADA")
        st.rerun()

    st.write(f"Status Atual: **{'ABERTA' if loja_aberta else 'FECHADA'}**")

    with get_db() as conn:
        df_v = pd.read_sql_query("SELECT * FROM vendas", conn)

    if not df_v.empty:
        st.metric("Faturamento Total", f"R$ {df_v['total'].sum():.2f}")

        st.markdown('<div class="secao">ANÁLISE DE DESEMPENHO</div>', unsafe_allow_html=True)

        st.subheader("📅 Faturamento Diário")
        df_v["Data_F"] = pd.to_datetime(df_v["data"], dayfirst=True).dt.date
        faturamento_diario = df_v.groupby("Data_F")["total"].sum()
        st.line_chart(faturamento_diario)

        st.subheader("🏆 Top 5 Produtos (Mais Vendidos)")
        todos_itens = df_v["itens"].str.split(", ").explode()
        top_produtos = todos_itens.value_counts().head(5)
        st.bar_chart(top_produtos)

        st.subheader("📋 Histórico Recente")
        df_exibir = df_v.sort_values(by="id", ascending=False)
        st.dataframe(df_exibir, use_container_width=True)

        st.markdown('<div class="secao">EXPORTAR DADOS</div>', unsafe_allow_html=True)
        csv = df_exibir.to_csv(index=False, sep=";", decimal=",", encoding="utf-8-sig")
        nome_arquivo = f"vendas_jubileu_{datetime.now().strftime('%d-%m-%Y')}.csv"
        st.download_button(
            label="⬇️ Baixar histórico em CSV",
            data=csv,
            file_name=nome_arquivo,
            mime="text/csv",
            help="Abre no Excel — pronto para controle financeiro",
        )
    else:
        st.info("Aguardando primeiras vendas para gerar gráficos.")

    if st.button("⬅️ Sair do Painel"):
        st.session_state.admin_logado = False
        st.rerun()
