import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager
import urllib.parse

# ─── PRODUTOS E PREÇOS ───────────────────────

ACAI_TAMANHOS = {
    "Açaí 300ml": 13.00,
    "Açaí 500ml": 18.00,
    "Açaí 700ml": 23.00,
    "Açaí 1 Litro": 32.00,
}

COMPLEMENTOS = {
    "Leite em Pó": 4.00,
    "Leite Condensado": 4.00,
    "Nutella": 8.00,
    "Creme de Avelã": 6.00,
    "Ovomaltine": 4.00,
    "Confete": 5.00,
    "Gotas de Chocolate": 4.00,
    "Fine Beijo": 4.00,
    "Fine Banana": 4.00,
    "Paçoca": 2.00,
    "Granola": 2.00,
    "Uva Verde": 4.00,
    "Chantilly": 4.00,
    "Mousse de Maracujá": 5.00,
}

GARRAFAS = {
    "Garrafa Tradicional": 10.00,
    "Garrafa Leite em Pó": 13.00,
    "Garrafa Morango": 13.00,
    "Garrafa Maracujá": 13.00,
}

CHOCOLATE_QUENTE = {"Chocolate Quente": 12.00}

# Curadoria dos mais pedidos — edite à vontade
MAIS_PEDIDOS = {
    "Açaí 500ml": 18.00,
    "Açaí 700ml": 23.00,
    "Açaí 1 Litro": 32.00,
    "Garrafa Tradicional": 10.00,
    "Nutella": 8.00,
    "Mousse de Maracujá": 5.00,
}

EMOJIS = {
    "Açaí 300ml": "🍧", "Açaí 500ml": "🍧", "Açaí 700ml": "🍧", "Açaí 1 Litro": "🍧",
    "Leite em Pó": "🥛", "Leite Condensado": "🍯", "Nutella": "🍫", "Creme de Avelã": "🍫",
    "Ovomaltine": "☕", "Confete": "🎉", "Gotas de Chocolate": "🍫", "Fine Beijo": "🍬",
    "Fine Banana": "🍌", "Paçoca": "🍬", "Granola": "🌾", "Uva Verde": "🍇",
    "Chantilly": "🍦", "Mousse de Maracujá": "🌸",
    "Garrafa Tradicional": "🥤", "Garrafa Leite em Pó": "🥤",
    "Garrafa Morango": "🥤", "Garrafa Maracujá": "🥤",
    "Chocolate Quente": "☕",
}

try:
    SENHA_DONO = st.secrets["SENHA_DONO"]
except Exception:
    SENHA_DONO = os.environ.get("SENHA_DONO", "")

DB_NAME = "jubileu_database.db"
WHATSAPP_NUMBER = "5537991031933"

# ─── BANCO DE DADOS ───────────────────────────

@contextmanager
def get_db():
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
        try:
            c.execute("ALTER TABLE vendas ADD COLUMN telefone TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass
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

# ─── CONFIG DA PÁGINA ─────────────────────────

st.set_page_config(page_title="Jubileu Açaí", page_icon="🍧", layout="centered")

st.markdown(
    '<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">',
    unsafe_allow_html=True,
)

# CSS 1 — reset e scroll
st.markdown("""<style>
html, body, [class*="css"] { font-family: 'Nunito', sans-serif !important; }
html { scroll-behavior: smooth; scroll-padding-top: 54px; }
.stApp { background: #f5f0fa !important; }
[data-testid="stHeader"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
#MainMenu { display: none !important; }
footer { display: none !important; }
.block-container { padding-top: 0 !important; padding-left: 0.8rem !important; padding-right: 0.8rem !important; max-width: 560px !important; }
</style>""", unsafe_allow_html=True)

# CSS 2 — banner
st.markdown("""<style>
.jub-banner { background: linear-gradient(135deg, #6A0DAD 0%, #9b30d9 100%); padding: 28px 20px 52px; text-align: center; position: relative; border-radius: 0 0 24px 24px; }
.jub-banner h1 { color: white; font-size: 22px; font-weight: 800; margin: 0; letter-spacing: 2px; text-shadow: 0 2px 8px rgba(0,0,0,0.2); }
.jub-banner p { color: rgba(255,255,255,0.85); font-size: 13px; margin: 5px 0 0; }
.jub-logo { width: 66px; height: 66px; border-radius: 50%; background: white; display: flex; align-items: center; justify-content: center; font-size: 28px; position: absolute; bottom: -33px; left: 50%; transform: translateX(-50%); box-shadow: 0 2px 12px rgba(0,0,0,0.18); }
</style>""", unsafe_allow_html=True)

# CSS 3 — barra de categorias sticky
st.markdown("""<style>
.sticky-nav { position: sticky; top: 0; z-index: 999; background: white; border-bottom: 2px solid #f0e6ff; box-shadow: 0 2px 8px rgba(0,0,0,0.07); display: flex; gap: 8px; overflow-x: auto; white-space: nowrap; margin: 0 -0.8rem; padding: 10px 0.8rem; scrollbar-width: none; }
.sticky-nav::-webkit-scrollbar { display: none; }
.nav-pill { display: inline-block; padding: 7px 15px; border-radius: 20px; border: 1.5px solid #6A0DAD; font-size: 13px; font-weight: 700; color: #6A0DAD; background: white; text-decoration: none; white-space: nowrap; font-family: 'Nunito', sans-serif; cursor: pointer; transition: all 0.18s; flex-shrink: 0; }
.nav-pill:hover { background: #f0e6ff; color: #6A0DAD; text-decoration: none; }
</style>""", unsafe_allow_html=True)

# CSS 4 — cards e seções
st.markdown("""<style>
.sec-anchor { display: block; scroll-margin-top: 54px; }
.sec-header { font-size: 17px; font-weight: 800; color: #1a1a1a; margin: 18px 0 10px 2px; padding-bottom: 6px; border-bottom: 2px solid #f0e6ff; }
.sec-header-top { color: #6A0DAD; border-bottom: 2px solid #6A0DAD; }
.prod-card { background: white; border: 1.5px solid #ede8f7; border-radius: 14px; overflow: hidden; margin-bottom: 2px; }
.prod-emoji-area { background: linear-gradient(135deg, #f7f2fd, #ede8f7); display: flex; align-items: center; justify-content: center; padding: 14px; font-size: 44px; min-height: 88px; }
.prod-details { padding: 8px 10px 10px; }
.prod-price-tag { font-size: 14px; font-weight: 800; color: #1a1a1a; }
.prod-name-tag { font-size: 12px; color: #666; margin-top: 2px; line-height: 1.3; }
</style>""", unsafe_allow_html=True)

# CSS 5 — formulário e checkout
st.markdown("""<style>
.resumo-box { background: white; border: 2px solid #6A0DAD; border-radius: 14px; padding: 16px; margin: 12px 0; }
.resumo-titulo { font-size: 15px; font-weight: 800; color: #6A0DAD; margin-bottom: 10px; }
.resumo-linha { font-size: 13px; color: #444; padding: 3px 0; }
.resumo-total { font-size: 16px; font-weight: 800; color: #1a1a1a; margin-top: 10px; padding-top: 10px; border-top: 1px solid #ede8f7; }
.btn-whats { background: linear-gradient(90deg, #25D366, #128C7E); color: white !important; padding: 15px; text-align: center; border-radius: 12px; font-weight: 800; font-size: 15px; text-decoration: none !important; display: block; margin-top: 10px; box-shadow: 0 4px 12px rgba(37,211,102,0.3); }
.fid-box { background: #fffbea; border: 1.5px solid #f5c518; border-radius: 12px; padding: 10px 14px; margin: 8px 0; font-size: 13px; color: #7a5a00; }
.fid-brinde { background: #eafaf0; border: 1.5px solid #1a9e4a; border-radius: 12px; padding: 10px 14px; margin: 8px 0; font-size: 13px; color: #0d5c2b; font-weight: 700; }
.sec-label { font-size: 14px; font-weight: 800; color: #444; margin-top: 16px; margin-bottom: 4px; }
div.stButton > button { background: #6A0DAD !important; color: white !important; border-radius: 12px !important; font-weight: 800 !important; font-size: 14px !important; width: 100% !important; border: none !important; padding: 10px !important; }
div.stButton > button:hover { opacity: 0.9 !important; }
div.stButton > button:disabled { background: #ccc !important; color: #888 !important; }
</style>""", unsafe_allow_html=True)

# ─── SESSION STATE ────────────────────────────

if "admin_logado" not in st.session_state:
    st.session_state.admin_logado = False

# ─────────────────────────────────────────────
# ÁREA DO CLIENTE
# ─────────────────────────────────────────────

if not st.session_state.admin_logado:
    loja_aberta = get_status_loja()

    # Banner roxo
    st.markdown("""<div class="jub-banner">
  <h1>🍧 JUBILEU AÇAÍ</h1>
  <p>Delivery &middot; Frete Grátis</p>
  <div class="jub-logo">🍧</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Status da loja
    if loja_aberta:
        st.success("🟢 ESTAMOS ABERTOS! PEÇA JÁ O SEU.")
    else:
        st.error("🔴 FECHADO NO MOMENTO — Em breve estamos de volta!")

    # ── Barra de categorias (sticky, rola com atalhos) ──
    st.markdown("""<div class="sticky-nav">
  <a href="#sec-top" class="nav-pill">⭐ Mais Pedidos</a>
  <a href="#sec-acai" class="nav-pill">🍧 Monte o Seu</a>
  <a href="#sec-comp" class="nav-pill">➕ Complementos</a>
  <a href="#sec-garr" class="nav-pill">🥤 Na Garrafa</a>
  <a href="#sec-choc" class="nav-pill">☕ Chocolate</a>
</div>""", unsafe_allow_html=True)

    # Carrinho acumulado
    cart = []

    def render_grid(produtos, prefix):
        items = list(produtos.items())
        for i in range(0, len(items), 2):
            row = items[i:i+2]
            cols = st.columns(2)
            for j, (nome, preco) in enumerate(row):
                with cols[j]:
                    emoji = EMOJIS.get(nome, "🍧")
                    st.markdown(
                        f'<div class="prod-card">'
                        f'<div class="prod-emoji-area">{emoji}</div>'
                        f'<div class="prod-details">'
                        f'<div class="prod-price-tag">R$ {preco:.2f}</div>'
                        f'<div class="prod-name-tag">{nome}</div>'
                        f'</div></div>',
                        unsafe_allow_html=True,
                    )
                    if st.checkbox("＋ Adicionar", key=f"{prefix}_{nome}"):
                        cart.append((nome, preco))

    # ── SEÇÃO: Os Mais Pedidos ──
    st.markdown('<div id="sec-top" class="sec-anchor"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-header sec-header-top">⭐ OS MAIS PEDIDOS</div>', unsafe_allow_html=True)
    render_grid(MAIS_PEDIDOS, "top")

    # ── SEÇÃO: Monte o Seu ──
    st.markdown('<div id="sec-acai" class="sec-anchor"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-header">🍧 Monte de Seu Jeito</div>', unsafe_allow_html=True)
    render_grid(ACAI_TAMANHOS, "acai")

    # ── SEÇÃO: Complementos ──
    st.markdown('<div id="sec-comp" class="sec-anchor"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-header">➕ Complementos</div>', unsafe_allow_html=True)
    render_grid(COMPLEMENTOS, "comp")

    # ── SEÇÃO: Açaí na Garrafa ──
    st.markdown('<div id="sec-garr" class="sec-anchor"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-header">🥤 Açaí na Garrafa</div>', unsafe_allow_html=True)
    render_grid(GARRAFAS, "garr")

    # ── SEÇÃO: Chocolate Quente ──
    st.markdown('<div id="sec-choc" class="sec-anchor"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-header">☕ Chocolate Quente</div>', unsafe_allow_html=True)
    render_grid(CHOCOLATE_QUENTE, "choc")

    st.markdown("---")

    # ── Formulário ──
    st.markdown('<div class="sec-label">👤 Seus dados</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    np_ = c1.text_input("Nome", placeholder="Nome").strip()
    sp_ = c2.text_input("Sobrenome", placeholder="Sobrenome").strip()
    nome_completo = f"{np_} {sp_}".upper().strip()
    telefone = st.text_input("📱 WhatsApp / Telefone", placeholder="(37) 99999-9999").strip()

    brinde_ativo = False
    if np_ and sp_:
        q = carregar_fidelidade_db(nome_completo)
        if q >= 9:
            st.markdown('<div class="fid-brinde">🎁 PARABÉNS! Seu próximo açaí é um BRINDE!</div>', unsafe_allow_html=True)
            brinde_ativo = True
        else:
            st.markdown(f'<div class="fid-box">⭐ Fidelidade: <b>{q}/10</b> pedidos</div>', unsafe_allow_html=True)
            st.progress(q / 10)

    st.markdown('<div class="sec-label">📍 Endereço de entrega</div>', unsafe_allow_html=True)
    col_rua, col_num = st.columns([3, 1])
    rua    = col_rua.text_input("Rua", placeholder="Rua / Avenida")
    numero = col_num.text_input("Nº", placeholder="Nº")
    bairro = st.text_input("Bairro", placeholder="Bairro")

    st.markdown('<div class="sec-label">💳 Forma de pagamento</div>', unsafe_allow_html=True)
    pag = st.selectbox("Pagamento", ["Pix", "Cartão", "Dinheiro"], label_visibility="collapsed")
    troco_msg = ""
    if pag == "Dinheiro":
        if st.radio("Precisa de troco?", ["Não", "Sim"], horizontal=True) == "Sim":
            v = st.text_input("Troco para quanto?", placeholder="Ex: R$ 50,00")
            troco_msg = f" (Troco para {v})"

    # ── Resumo e finalizar ──
    total_itens = sum(p for _, p in cart)
    total_final = 0.00 if brinde_ativo else total_itens

    if cart:
        linhas = "".join(
            f'<div class="resumo-linha">• {n} &mdash; R$ {p:.2f}</div>' for n, p in cart
        )
        brinde_html = (
            '<div class="resumo-linha" style="color:#1a9e4a;font-weight:700;">🎁 Brinde Fidelidade Aplicado!</div>'
            if brinde_ativo else ""
        )
        st.markdown(
            f'<div class="resumo-box">'
            f'<div class="resumo-titulo">🧾 Resumo do Pedido</div>'
            f'{linhas}{brinde_html}'
            f'<div class="resumo-total">TOTAL: R$ {total_final:.2f}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if st.button("✅ FINALIZAR PEDIDO", disabled=not loja_aberta):
            if not (np_ and rua and numero and bairro):
                st.warning("Preencha nome e endereço completo!")
            elif not telefone:
                st.warning("Preencha o telefone para contato!")
            else:
                nomes = [n for n, _ in cart]
                registrar_venda_db(nome_completo, telefone, total_final, ", ".join(nomes))
                atualizar_fidelidade_db(nome_completo, brinde_ativo)
                msg = (
                    f"*NOVO PEDIDO JUBILEU AÇAÍ*\n"
                    f"------------------\n"
                    f"*Cliente:* {nome_completo}\n"
                    f"*Telefone:* {telefone}\n"
                    f"*Endereço:* {rua}, {numero} - {bairro}\n"
                    f"------------------\n"
                    f"*Itens:* {', '.join(nomes)}\n"
                    f"*Pagamento:* {pag}{troco_msg}\n"
                    f"*TOTAL: R$ {total_final:.2f}*"
                )
                link = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(msg)}"
                st.markdown(
                    f'<a href="{link}" target="_blank" class="btn-whats">🚀 ENVIAR PEDIDO PELO WHATSAPP</a>',
                    unsafe_allow_html=True,
                )

    st.markdown("---")
    if st.button("v2.0", help="Sistema"):
        st.session_state.admin_logado = "solicitar_senha"
        st.rerun()

# ─────────────────────────────────────────────
# LOGIN ADMIN
# ─────────────────────────────────────────────

if st.session_state.admin_logado == "solicitar_senha":
    st.markdown("### 🔐 Acesso Restrito")
    senha = st.text_input("Senha:", type="password")
    c1, c2 = st.columns(2)
    if c1.button("Entrar"):
        if not SENHA_DONO:
            st.error("Senha não configurada. Contate o administrador.")
        elif senha == SENHA_DONO:
            st.session_state.admin_logado = True
            st.rerun()
        else:
            st.error("Acesso negado!")
    if c2.button("Voltar"):
        st.session_state.admin_logado = False
        st.rerun()

# ─────────────────────────────────────────────
# PAINEL DO DONO
# ─────────────────────────────────────────────

if st.session_state.admin_logado is True:
    st.title("📊 Gestão Jubileu Açaí")

    loja_aberta = get_status_loja()
    col1, col2 = st.columns(2)
    if col1.button("🟢 ABRIR LOJA"):
        set_status_loja("ABERTA")
        st.rerun()
    if col2.button("🔴 FECHAR LOJA"):
        set_status_loja("FECHADA")
        st.rerun()
    st.write(f"Status Atual: **{'ABERTA ✅' if loja_aberta else 'FECHADA 🔴'}**")

    with get_db() as conn:
        df_v = pd.read_sql_query("SELECT * FROM vendas", conn)

    if not df_v.empty:
        c1, c2 = st.columns(2)
        c1.metric("Faturamento Total", f"R$ {df_v['total'].sum():.2f}")
        c2.metric("Total de Pedidos", len(df_v))

        st.subheader("📅 Faturamento Diário")
        df_v["Data_F"] = pd.to_datetime(df_v["data"], dayfirst=True).dt.date
        st.line_chart(df_v.groupby("Data_F")["total"].sum())

        st.subheader("🏆 Top 5 Produtos")
        todos_itens = df_v["itens"].str.split(", ").explode()
        st.bar_chart(todos_itens.value_counts().head(5))

        st.subheader("📋 Histórico de Pedidos")
        st.dataframe(df_v.sort_values("id", ascending=False), use_container_width=True)

        csv = df_v.sort_values("id", ascending=False).to_csv(
            index=False, sep=";", decimal=",", encoding="utf-8-sig"
        )
        st.download_button(
            "⬇️ Exportar CSV",
            data=csv,
            file_name=f"vendas_jubileu_{datetime.now().strftime('%d-%m-%Y')}.csv",
            mime="text/csv",
        )
    else:
        st.info("Aguardando primeiras vendas para exibir análises.")

    if st.button("⬅️ Sair do Painel"):
        st.session_state.admin_logado = False
        st.rerun()
