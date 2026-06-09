import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager
import urllib.parse

# ─────────────────────────────────────────────
# 1. CONFIGURAÇÕES E PREÇOS
# ─────────────────────────────────────────────

ACAI_TAMANHOS = {
    "Açaí 300ml": 13.00,
    "Açaí 500ml": 18.00,
    "Açaí 700ml": 23.00,
    "Açaí 1 Litro": 32.00,
}

COMPLEMENTOS = {
    "Leite em Pó":        4.00,
    "Leite Condensado":   4.00,
    "Nutella":            8.00,
    "Creme de Avelã":     6.00,
    "Ovomaltine":         4.00,
    "Confete":            5.00,
    "Gotas de Chocolate": 4.00,
    "Fine Beijo":         4.00,
    "Fine Banana":        4.00,
    "Paçoca":             2.00,
    "Granola":            2.00,
    "Uva Verde":          4.00,
    "Chantilly":          4.00,
    "Mousse de Maracujá": 5.00,
}

GARRAFAS = {
    "Tradicional": 10.00,
    "Leite em Pó": 13.00,
    "Morango":     13.00,
    "Maracujá":    13.00,
}

CHOCOLATE_QUENTE = {"Chocolate Quente": 12.00}

# Emoji de representação para cada produto (usado nos cards)
EMOJIS = {
    "Açaí 300ml": "🍧", "Açaí 500ml": "🍧", "Açaí 700ml": "🍧", "Açaí 1 Litro": "🍧",
    "Leite em Pó": "🥛", "Leite Condensado": "🍯", "Nutella": "🍫", "Creme de Avelã": "🍫",
    "Ovomaltine": "☕", "Confete": "🎉", "Gotas de Chocolate": "🍫", "Fine Beijo": "🍬",
    "Fine Banana": "🍌", "Paçoca": "🍬", "Granola": "🌾", "Uva Verde": "🍇",
    "Chantilly": "🍦", "Mousse de Maracujá": "🌸",
    "Tradicional": "🥤", "Morango": "🥤", "Maracujá": "🥤",
    "Chocolate Quente": "☕",
}

try:
    SENHA_DONO = st.secrets["SENHA_DONO"]
except Exception:
    SENHA_DONO = os.environ.get("SENHA_DONO", "")

DB_NAME = "jubileu_database.db"
WHATSAPP_NUMBER = "5537991031933"

# ─────────────────────────────────────────────
# 2. BANCO DE DADOS
# ─────────────────────────────────────────────

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

# ─────────────────────────────────────────────
# 3. PÁGINA E CSS GLOBAL
# ─────────────────────────────────────────────

st.set_page_config(page_title="Jubileu Açaí", page_icon="🍧", layout="centered")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  /* ── Reset e fonte ── */
  html, body, [class*="css"] { font-family: 'Nunito', sans-serif !important; }
  .stApp { background: #f5f0fa !important; }

  /* ── Oculta elementos padrão do Streamlit ── */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding: 0 !important; max-width: 540px !important; margin: 0 auto !important; }

  /* ── Banner roxo do topo ── */
  .banner {
    background: #6A0DAD;
    padding: 28px 20px 56px;
    text-align: center;
    position: relative;
  }
  .banner h1 { color: white; font-size: 22px; font-weight: 800; letter-spacing: 1px; margin: 0; }
  .banner p  { color: rgba(255,255,255,0.85); font-size: 13px; margin: 4px 0 0; }
  .logo-circle {
    width: 72px; height: 72px; border-radius: 50%;
    background: #f0e6ff; border: 3px solid white;
    display: flex; align-items: center; justify-content: center;
    font-size: 30px;
    position: absolute; bottom: -36px; left: 50%; transform: translateX(-50%);
    box-shadow: 0 2px 12px rgba(106,13,173,0.25);
  }

  /* ── Card branco principal ── */
  .main-card {
    background: white;
    border-radius: 16px 16px 0 0;
    margin-top: 50px;
    padding: 20px 16px 100px;
    min-height: 80vh;
  }
  .store-name { font-size: 17px; font-weight: 800; text-align: center; color: #1a1a1a; margin-bottom: 4px; }

  /* ── Status loja ── */
  .status-open   { color: #1a9e4a; font-size: 13px; font-weight: 700; text-align: center; margin-bottom: 16px; }
  .status-closed { color: #d84444; font-size: 13px; font-weight: 700; text-align: center; margin-bottom: 16px; }

  /* ── Abas de categoria ── */
  .tabs-row {
    display: flex; gap: 8px; overflow-x: auto;
    padding-bottom: 6px; margin-bottom: 20px;
    border-bottom: 1.5px solid #f0e6ff;
    scrollbar-width: none;
  }
  .tabs-row::-webkit-scrollbar { display: none; }
  .tab-pill {
    flex-shrink: 0;
    padding: 7px 18px;
    border-radius: 20px;
    border: 1.5px solid #6A0DAD;
    font-size: 13px; font-weight: 700;
    cursor: pointer;
    background: white; color: #6A0DAD;
    white-space: nowrap;
    transition: all 0.18s;
    font-family: 'Nunito', sans-serif;
  }
  .tab-pill:hover { background: #f0e6ff; }
  .tab-pill.ativo { background: #6A0DAD; color: white; }

  /* ── Título de seção ── */
  .section-title {
    font-size: 16px; font-weight: 800; color: #1a1a1a;
    margin: 4px 0 14px 2px;
  }

  /* ── Grid de produtos ── */
  .produtos-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(148px, 1fr));
    gap: 12px;
    margin-bottom: 24px;
  }

  /* ── Card de produto ── */
  .prod-card {
    background: white;
    border: 1px solid #ede8f7;
    border-radius: 12px;
    overflow: hidden;
    position: relative;
    transition: transform 0.15s;
  }
  .prod-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(106,13,173,0.10); }
  .prod-emoji {
    width: 100%; height: 110px;
    display: flex; align-items: center; justify-content: center;
    background: #f7f2fd;
    font-size: 42px;
  }
  .prod-info { padding: 8px 10px 36px; }
  .prod-price { font-size: 13px; font-weight: 800; color: #1a1a1a; margin-bottom: 2px; }
  .prod-name  { font-size: 12px; color: #666; line-height: 1.3; }

  /* ── Botão + ── */
  .add-btn-wrap {
    position: absolute; bottom: 8px; right: 8px;
  }

  /* ── Checkbox estilizado como + ── */
  .prod-check { display: none; }
  .prod-check + label {
    width: 30px; height: 30px; border-radius: 50%;
    background: #6A0DAD; color: white;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; font-weight: 400; line-height: 1;
    cursor: pointer;
    box-shadow: 0 2px 6px rgba(106,13,173,0.30);
    transition: transform 0.15s, background 0.15s;
    user-select: none;
  }
  .prod-check:checked + label {
    background: #1a9e4a;
    font-size: 16px;
  }
  .prod-check + label:hover { transform: scale(1.12); }

  /* ── Resumo do pedido ── */
  .resumo-box {
    background: #f7f2fd;
    border: 1.5px solid #d4b8f5;
    border-radius: 14px;
    padding: 16px;
    margin: 16px 0;
  }
  .resumo-titulo { font-size: 15px; font-weight: 800; color: #6A0DAD; margin-bottom: 10px; }
  .resumo-item   { font-size: 13px; color: #333; padding: 3px 0; }
  .resumo-total  { font-size: 16px; font-weight: 800; color: #1a1a1a; margin-top: 10px; padding-top: 10px; border-top: 1px solid #d4b8f5; }

  /* ── Botão WhatsApp ── */
  .btn-whats {
    background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
    color: white !important; padding: 15px; text-align: center;
    border-radius: 12px; font-weight: 800; font-size: 15px;
    text-decoration: none; display: block; margin-top: 12px;
  }
  .btn-whats:hover { opacity: 0.92; }

  /* ── Fidelidade ── */
  .fid-box {
    background: #fffbea; border: 1.5px solid #f5c518;
    border-radius: 12px; padding: 12px 14px; margin: 12px 0;
    font-size: 13px; color: #7a5a00;
  }
  .fid-brinde {
    background: #eafaf0; border: 1.5px solid #1a9e4a;
    border-radius: 12px; padding: 12px 14px; margin: 12px 0;
    font-size: 13px; color: #0d5c2b; font-weight: 700;
  }

  /* ── Inputs ── */
  .stTextInput input {
    border-radius: 10px !important;
    border: 1.5px solid #d4b8f5 !important;
    font-family: 'Nunito', sans-serif !important;
  }
  .stTextInput input:focus {
    border-color: #6A0DAD !important;
    box-shadow: 0 0 0 2px rgba(106,13,173,0.12) !important;
  }
  .stSelectbox > div > div {
    border-radius: 10px !important;
    border: 1.5px solid #d4b8f5 !important;
  }

  /* ── Botão principal ── */
  .stButton > button {
    background: #6A0DAD !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    font-family: 'Nunito', sans-serif !important;
    border: none !important;
    padding: 12px 24px !important;
    width: 100% !important;
    font-size: 15px !important;
    transition: opacity 0.15s !important;
  }
  .stButton > button:hover { opacity: 0.88 !important; }
  .stButton > button:disabled { background: #ccc !important; }

  /* ── Barra inferior fixa ── */
  .bottom-bar {
    position: fixed; bottom: 0; left: 50%; transform: translateX(-50%);
    width: 100%; max-width: 540px;
    background: white; border-top: 1px solid #ede8f7;
    display: flex; justify-content: space-around; padding: 10px 0 14px;
    z-index: 999;
  }
  .nav-item { display: flex; flex-direction: column; align-items: center; font-size: 11px; color: #999; gap: 2px; }
  .nav-item.ativo { color: #6A0DAD; }
  .nav-icon { font-size: 22px; }

  /* ── Divider ── */
  hr.divider { border: none; border-top: 1.5px solid #f0e6ff; margin: 20px 0; }

  /* ── Label campos ── */
  .campo-label { font-size: 13px; font-weight: 700; color: #444; margin-bottom: 4px; margin-top: 12px; }

  /* ── Painel admin ── */
  .admin-metric {
    background: #f7f2fd; border-radius: 12px; padding: 16px;
    text-align: center; margin-bottom: 8px;
  }
  .admin-metric-val { font-size: 26px; font-weight: 800; color: #6A0DAD; }
  .admin-metric-lbl { font-size: 12px; color: #888; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 4. SESSION STATE
# ─────────────────────────────────────────────

if "admin_logado" not in st.session_state:
    st.session_state.admin_logado = False
if "aba" not in st.session_state:
    st.session_state.aba = "acai"

# ─────────────────────────────────────────────
# 5. ÁREA DO CLIENTE
# ─────────────────────────────────────────────

if not st.session_state.admin_logado:
    loja_aberta = get_status_loja()

    # ── Banner ──
    st.markdown("""
    <div class="banner">
      <h1>🍧 JUBILEU AÇAÍ</h1>
      <p>Delivery · Frete Grátis</p>
      <div class="logo-circle">🍧</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown('<div class="store-name">Jubileu Açaí</div>', unsafe_allow_html=True)

    if loja_aberta:
        st.markdown('<div class="status-open">🟢 ESTAMOS ABERTOS! PEÇA JÁ O SEU.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-closed">🔴 FECHADO NO MOMENTO</div>', unsafe_allow_html=True)

    # ── Abas de navegação ──
    abas = {
        "acai":       "Monte o Seu",
        "complementos": "Complementos",
        "garrafa":    "Açaí na Garrafa",
        "chocolate":  "Chocolate Quente",
    }

    tabs_html = '<div class="tabs-row">'
    for key, label in abas.items():
        ativo = "ativo" if st.session_state.aba == key else ""
        tabs_html += f'<button class="tab-pill {ativo}" onclick="window.location.href=\'?aba={key}\'">{label}</button>'
    tabs_html += "</div>"
    st.markdown(tabs_html, unsafe_allow_html=True)

    # Lê parâmetro de aba da URL
    params = st.query_params
    if "aba" in params:
        st.session_state.aba = params["aba"]

    aba_atual = st.session_state.aba

    # Usa lista mutável para acumular itens em todas as abas
    _carrinho: list = []
    _total_ref = [0.0]  # lista para ser mutável dentro das funções

    def render_grid(produtos: dict, prefix: str):
        cols_per_row = 2
        prod_list = list(produtos.items())
        for i in range(0, len(prod_list), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, (nome, preco) in enumerate(prod_list[i:i+cols_per_row]):
                with cols[j]:
                    emoji = EMOJIS.get(nome, "🍧")
                    st.markdown(f"""
                    <div class="prod-card">
                      <div class="prod-emoji">{emoji}</div>
                      <div class="prod-info">
                        <div class="prod-price">R$ {preco:.2f}</div>
                        <div class="prod-name">{nome}</div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                    key = f"{prefix}_{nome}"
                    selecionado = st.checkbox(f"Adicionar {nome}", key=key, label_visibility="collapsed")
                    if selecionado:
                        _carrinho.append(nome)
                        _total_ref[0] += preco

    itens_pedido = _carrinho
    def get_total(): return _total_ref[0]

    # ── Conteúdo por aba ──
    if aba_atual == "acai":
        st.markdown('<div class="section-title">Monte de seu jeito</div>', unsafe_allow_html=True)
        render_grid(ACAI_TAMANHOS, "acai")

    elif aba_atual == "complementos":
        st.markdown('<div class="section-title">Complementos</div>', unsafe_allow_html=True)
        render_grid(COMPLEMENTOS, "comp")

    elif aba_atual == "garrafa":
        st.markdown('<div class="section-title">Açaí na Garrafa</div>', unsafe_allow_html=True)
        render_grid(GARRAFAS, "garr")

    elif aba_atual == "chocolate":
        st.markdown('<div class="section-title">Chocolate Quente</div>', unsafe_allow_html=True)
        render_grid(CHOCOLATE_QUENTE, "choc")

    # ── Identificação ──
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="campo-label">👤 Seu nome</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    np_ = c1.text_input("Nome", placeholder="Nome", label_visibility="collapsed").strip()
    sp_ = c2.text_input("Sobrenome", placeholder="Sobrenome", label_visibility="collapsed").strip()
    nome_completo = f"{np_} {sp_}".upper().strip()

    st.markdown('<div class="campo-label">📱 WhatsApp / Telefone</div>', unsafe_allow_html=True)
    telefone = st.text_input("Telefone", placeholder="(37) 99999-9999", label_visibility="collapsed").strip()

    # ── Fidelidade ──
    brinde_ativo = False
    if np_ and sp_:
        q = carregar_fidelidade_db(nome_completo)
        if q >= 9:
            st.markdown('<div class="fid-brinde">🎁 PARABÉNS! Seu próximo açaí é um BRINDE!</div>', unsafe_allow_html=True)
            brinde_ativo = True
        else:
            st.markdown(f'<div class="fid-box">⭐ Fidelidade: <b>{q}/10</b> pedidos</div>', unsafe_allow_html=True)
            st.progress(q / 10)

    # ── Endereço ──
    st.markdown('<div class="campo-label">📍 Endereço de entrega</div>', unsafe_allow_html=True)
    col_rua, col_num = st.columns([3, 1])
    rua    = col_rua.text_input("Rua", placeholder="Rua / Avenida", label_visibility="collapsed")
    numero = col_num.text_input("Nº", placeholder="Nº", label_visibility="collapsed")
    bairro = st.text_input("Bairro", placeholder="Bairro", label_visibility="collapsed")

    # ── Pagamento ──
    st.markdown('<div class="campo-label">💳 Forma de pagamento</div>', unsafe_allow_html=True)
    pag = st.selectbox("Pagamento", ["Pix", "Cartão", "Dinheiro"], label_visibility="collapsed")
    troco_msg = ""
    if pag == "Dinheiro":
        if st.radio("Precisa de troco?", ["Não", "Sim"], horizontal=True) == "Sim":
            v = st.text_input("Troco para quanto?", placeholder="Ex: R$ 50,00")
            troco_msg = f" (Troco para {v})"

    total_itens = get_total()
    total_final = 0.00 if brinde_ativo else total_itens

    # ── Resumo e finalizar ──
    if itens_pedido:
        itens_str = ""
        for item in itens_pedido:
            preco_item = {**ACAI_TAMANHOS, **COMPLEMENTOS, **GARRAFAS, **CHOCOLATE_QUENTE}.get(item, 0)
            itens_str += f'<div class="resumo-item">• {item} — R$ {preco_item:.2f}</div>'

        brinde_html = '<div class="resumo-item" style="color:#1a9e4a;">🎁 Brinde Fidelidade Aplicado!</div>' if brinde_ativo else ""

        st.markdown(f"""
        <div class="resumo-box">
          <div class="resumo-titulo">🧾 Resumo do Pedido</div>
          {itens_str}
          {brinde_html}
          <div class="resumo-total">TOTAL: R$ {total_final:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("✅ FINALIZAR PEDIDO", disabled=not loja_aberta):
            if not (np_ and rua and numero and bairro):
                st.warning("Preencha nome e endereço completo!")
            elif not telefone:
                st.warning("Preencha o telefone para contato!")
            else:
                registrar_venda_db(nome_completo, telefone, total_final, ", ".join(itens_pedido))
                atualizar_fidelidade_db(nome_completo, brinde_ativo)
                msg = (
                    f"*NOVO PEDIDO JUBILEU AÇAÍ*\n"
                    f"------------------\n"
                    f"*Cliente:* {nome_completo}\n"
                    f"*Telefone:* {telefone}\n"
                    f"*Endereço:* {rua}, {numero} - {bairro}\n"
                    f"------------------\n"
                    f"*Itens:* {', '.join(itens_pedido)}\n"
                    f"*Pagamento:* {pag}{troco_msg}\n"
                    f"*TOTAL: R$ {total_final:.2f}*"
                )
                link = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(msg)}"
                st.markdown(
                    f'<a href="{link}" target="_blank" class="btn-whats">🚀 ENVIAR PEDIDO PELO WHATSAPP</a>',
                    unsafe_allow_html=True,
                )

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Barra inferior fixa ──
    st.markdown("""
    <div class="bottom-bar">
      <div class="nav-item ativo">
        <span class="nav-icon">☰</span>
        <span>menu</span>
      </div>
      <div class="nav-item">
        <span class="nav-icon">🛒</span>
        <span>pedidos</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Acesso admin discreto ──
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("v2.0", help="Sistema"):
        st.session_state.admin_logado = "solicitar_senha"
        st.rerun()

# ─────────────────────────────────────────────
# 6. LOGIN ADMIN
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
# 7. PAINEL DO DONO
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
        total = df_v["total"].sum()
        qtd   = len(df_v)

        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="admin-metric"><div class="admin-metric-val">R$ {total:.2f}</div><div class="admin-metric-lbl">Faturamento Total</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="admin-metric"><div class="admin-metric-val">{qtd}</div><div class="admin-metric-lbl">Total de Pedidos</div></div>', unsafe_allow_html=True)

        st.subheader("📅 Faturamento Diário")
        df_v["Data_F"] = pd.to_datetime(df_v["data"], dayfirst=True).dt.date
        st.line_chart(df_v.groupby("Data_F")["total"].sum())

        st.subheader("🏆 Top 5 Produtos")
        todos_itens = df_v["itens"].str.split(", ").explode()
        st.bar_chart(todos_itens.value_counts().head(5))

        st.subheader("📋 Histórico de Pedidos")
        st.dataframe(df_v.sort_values("id", ascending=False), use_container_width=True)

        csv = df_v.sort_values("id", ascending=False).to_csv(index=False, sep=";", decimal=",", encoding="utf-8-sig")
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
