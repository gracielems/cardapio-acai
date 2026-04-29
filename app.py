import streamlit as st
import urllib.parse
from datetime import datetime
import pytz

# Configurações de Página
st.set_page_config(page_title="Jubilu Açaí - Premium", page_icon="🍧", layout="centered")

# --- LÓGICA DE HORÁRIO DE FUNCIONAMENTO ---
fuso_horario = pytz.timezone('America/Sao_Paulo')
agora = datetime.now(fuso_horario)
hora_atual = agora.hour
aberto = 14 <= hora_atual < 23  # Exemplo: Aberto das 14h às 23h

# CSS PERSONALIZADO
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #31333F; }
    .banner {
        background: linear-gradient(90deg, #4B0082 0%, #8A2BE2 100%);
        padding: 30px; border-radius: 0px 0px 30px 30px;
        color: white !important; text-align: center; margin: -60px -20px 30px -20px;
    }
    .fidelidade-card {
        background-color: #f0e6ff; padding: 15px; border-radius: 15px;
        border: 2px dashed #4B0082; text-align: center; margin-bottom: 20px;
    }
    .section-header { 
        color: #4B0082 !important; font-size: 20px; font-weight: bold;
        border-bottom: 2px solid #4B0082; margin-top: 25px; margin-bottom: 15px;
    }
    .mais-pedido {
        background-color: #FFD700; color: #000 !important;
        padding: 2px 8px; border-radius: 5px; font-size: 10px; font-weight: bold;
    }
    .stButton>button { 
        width: 100%; background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        color: white !important; border-radius: 15px; font-weight: bold; height: 3.5em;
    }
    .status-badge {
        padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TOPO E STATUS ---
st.markdown("""
    <div class="banner">
        <h1 style="color: white !important; margin:0;">🍧 Jubilu Delivery</h1>
        <p style="color: white !important; opacity: 0.9;">Qualidade e sabor em cada colherada!</p>
    </div>
    """, unsafe_allow_html=True)

col_status, col_insta = st.columns([1, 1])
with col_status:
    if aberto:
        st.markdown('<span class="status-badge" style="background:#d4edda; color:#155724;">● ABERTO AGORA</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge" style="background:#f8d7da; color:#721c24;">● FECHADO (Abre às 14h)</span>', unsafe_allow_html=True)

with col_insta:
    st.markdown("[📸 Siga nosso Instagram](https://instagram.com)", unsafe_allow_html=True)

# --- CARTÃO FIDELIDADE (SIMULADO) ---
if 'pedidos' not in st.session_state: st.session_state.pedidos = 0

st.markdown('<div class="section-header">🎁 SEU CARTÃO FIDELIDADE</div>', unsafe_allow_html=True)
with st.container():
    progresso = st.session_state.pedidos % 10
    st.markdown(f"""
    <div class="fidelidade-card">
        <b>Você já fez {st.session_state.pedidos} pedidos conosco!</b><br>
        Faltam {10 - progresso} pedidos para você ganhar 1 Açaí de 500ml Grátis!
    </div>
    """, unsafe_allow_html=True)
    st.progress(progresso / 10)

# --- MENU DE COMBOS ---
st.markdown('<div class="section-header">🔥 COMBOS EM DESTAQUE</div>', unsafe_allow_html=True)

copos = {
    "🍫 Laka Oreo (500ml)": {"preco": 28.00, "popular": True, "img": "https://via.placeholder.com/150"},
    "🍓 Clássico Morango (500ml)": {"preco": 27.00, "popular": False, "img": "https://via.placeholder.com/150"},
    "⭐ Nutella Premium (500ml)": {"preco": 34.00, "popular": True, "img": "https://via.placeholder.com/150"}
}

escolhidos = []
for nome, info in copos.items():
    c1, c2 = st.columns([1, 2])
    with c1:
        st.image(info['img'], use_container_width=True) # Troque o link da imagem pela sua foto
    with c2:
        tag = '<span class="mais-pedido">🔥 MAIS PEDIDO</span>' if info['popular'] else ""
        st.markdown(f"**{nome}** {tag}<br>R$ {info['preco']:.2f}", unsafe_allow_html=True)
        if st.checkbox(f"Adicionar", key=nome):
            escolhidos.append((nome, info['preco']))

# --- UPSELL (SUGESTÃO ADICIONAL) ---
st.markdown('<div class="section-header">🤤 QUE TAL UM EXTRA?</div>', unsafe_allow_html=True)
upsell = st.checkbox("🍫 Adicionar Nutella Extra por apenas +R$ 6,00?")

# --- DADOS DE ENTREGA ---
st.markdown('<div class="section-header">📍 FINALIZAR PEDIDO</div>', unsafe_allow_html=True)

if 'nome' not in st.session_state: st.session_state.nome = ""
if 'end' not in st.session_state: st.session_state.end = ""

nome = st.text_input("Seu Nome:", value=st.session_state.nome)
endereco = st.text_area("Seu Endereço em Nova Serrana:", value=st.session_state.end)
st.session_state.nome, st.session_state.end = nome, endereco

pagamento = st.selectbox("Forma de Pagamento:", ["Pix", "Cartão", "Dinheiro"])
st.info("🚚 Frete Grátis para toda a cidade!")

# --- CÁLCULO E FECHAMENTO ---
total = sum(p for n, p in escolhidos)
if upsell: total += 6.00

st.markdown(f"""
    <div style="background-color: #4B0082; padding: 20px; border-radius: 15px; text-align: center; margin-top: 20px;">
        <h2 style="margin:0; color: #25D366 !important;">Total: R$ {total:.2f}</h2>
    </div>
    <br>
""", unsafe_allow_html=True)

if st.button("✅ ENVIAR PEDIDO"):
    if not nome or not endereco:
        st.error("Por favor, preencha seus dados.")
    elif total == 0:
        st.warning("Seu carrinho está vazio.")
    elif not aberto:
        st.error("Desculpe, estamos fechados no momento. Atendemos a partir das 14h!")
    else:
        st.session_state.pedidos += 1
        resumo = "".join([f"• {n}\n" for n, p in escolhidos])
        if upsell: resumo += "• EXTRA: Nutella\n"
        
        msg = (
            f"🍧 *JUBILU AÇAÍ - NOVO PEDIDO*\n\n"
            f"👤 *Cliente:* {nome}\n"
            f"📍 *Endereço:* {endereco}\n"
            f"💳 *Pagamento:* {pagamento}\n"
            f"---------------------------\n"
            f"{resumo}"
            f"💰 *TOTAL: R$ {total:.2f}*\n"
            f"🚀 *Pedido nº {st.session_state.pedidos} deste cliente!*"
        )
        
        link = f"https://wa.me/5537991031933?text={urllib.parse.quote(msg)}"
        st.markdown(f'<meta http-equiv="refresh" content="0;URL={link}">', unsafe_allow_html=True)
