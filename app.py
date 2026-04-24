import streamlit as st
import urllib.parse

# Configurações de Página
st.set_page_config(page_title="Cardápio Jubilu", page_icon="🍧", layout="centered")

# CSS PERSONALIZADO (Corrigindo cores e sombras)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #31333F; }
    .banner {
        background: linear-gradient(90deg, #4B0082 0%, #8A2BE2 100%);
        padding: 30px;
        border-radius: 0px 0px 30px 30px;
        color: white !important;
        text-align: center;
        margin: -60px -20px 30px -20px;
    }
    .section-header { 
        color: #4B0082 !important; 
        font-size: 20px; font-weight: bold;
        border-bottom: 2px solid #4B0082;
        margin-top: 25px; margin-bottom: 15px;
    }
    .combo-info {
        background-color: #f8f4ff; padding: 10px;
        border-radius: 10px; border-left: 5px solid #4B0082;
        margin-bottom: 5px; font-size: 14px;
    }
    .stButton>button { 
        width: 100%; background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        color: white !important; border-radius: 15px; font-weight: bold; height: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE MEMÓRIA (CADASTRO LOCAL) ---
# O Streamlit usa o session_state para manter dados enquanto a aba está aberta
if 'nome_cliente' not in st.session_state:
    st.session_state.nome_cliente = ""
if 'endereco_cliente' not in st.session_state:
    st.session_state.endereco_cliente = ""

# --- TOPO ---
st.markdown("""
    <div class="banner">
        <h1 style="color: white !important; margin:0;">🍧 Jubilu Delivery</h1>
        <p style="color: white !important; opacity: 0.9;">O Açaí mais amado de Nova Serrana!</p>
    </div>
    """, unsafe_allow_html=True)

# --- SEÇÃO 1: COMBOS ---
st.markdown('<div class="section-header">🔥 1. ESCOLHA SEUS COMBOS</div>', unsafe_allow_html=True)

copos_prontos = {
    "🍫 Açaí Laka Oreo (500ml) - R$ 28.00": {"preco": 28.00, "desc": "Capa de Laka Oreo, Oreo crocante e leite em pó."},
    "🍓 Clássico Morango (500ml) - R$ 27.00": {"preco": 27.00, "desc": "Morangos frescos, leite em pó e leite condensado."},
    "💣 Açaí Sensação (700ml) - R$ 29.99": {"preco": 29.99, "desc": "Sonho de Valsa, banana fatiada e calda de morango."},
    "⭐ Nutella Premium (500ml) - R$ 34.00": {"preco": 34.00, "desc": "Muita Nutella original, morango e leite Ninho."}
}

escolhidos = st.multiselect("Selecione seus combos:", list(copos_prontos.keys()))

valor_combos = 0.0
if escolhidos:
    for item in escolhidos:
        info = copos_prontos[item]
        st.markdown(f"""<div class="combo-info"><b>{item}</b><br>{info['desc']}</div>""", unsafe_allow_html=True)
        valor_combos += info['preco']

# --- SEÇÃO 2: MONTE SEU COPO ---
st.markdown('<div class="section-header">🛠️ 2. MONTE DO SEU JEITO</div>', unsafe_allow_html=True)
tamanhos = {"500ml": 18.00, "700ml": 23.00, "1 Litro": 32.00}
escolha_tamanho = st.selectbox("Tamanho base:", ["Não vou montar um agora"] + list(tamanhos.keys()))

preco_base_monte = 0.0
selecionados_gratis = []
selecionados_pagos = []
valor_adicionais = 0.0

if escolha_tamanho != "Não vou montar um agora":
    preco_base_monte = tamanhos[escolha_tamanho]
    itens_gratis = ["Leite em Pó", "Granola", "Paçoca", "Banana", "Leite Condensado"]
    selecionados_gratis = st.multiselect("Grátis (Até 3):", itens_gratis)
    adicionais = {"Morango 🍓": 4.00, "Nutella 🍫": 6.00, "Creme de Ninho 🥛": 5.00}
    for item, preco in adicionais.items():
        if st.checkbox(f"{item} (+R${preco:.2f})"):
            selecionados_pagos.append(item)
            valor_adicionais += preco

# --- SEÇÃO 3: CADASTRO E ENTREGA ---
st.markdown('<div class="section-header">📍 3. SEUS DADOS</div>', unsafe_allow_html=True)

# Tenta recuperar o que o cliente digitou antes para não repetir
nome = st.text_input("Nome:", value=st.session_state.nome_cliente)
endereco = st.text_area("Endereço Completo:", value=st.session_state.endereco_cliente)
pagamento = st.selectbox("Pagamento:", ["Pix", "Cartão", "Dinheiro"])

# Salva na memória do navegador para a próxima vez
st.session_state.nome_cliente = nome
st.session_state.endereco_cliente = endereco

# Cálculo de Pedidos (Simulado por sessão)
if 'total_pedidos_cliente' not in st.session_state:
    st.session_state.total_pedidos_cliente = 0

# --- FINALIZAÇÃO ---
valor_total = valor_combos + preco_base_monte + valor_adicionais
st.markdown(f"""<div style="background-color: #4B0082; padding: 20px; border-radius: 15px; text-align: center;">
    <h2 style="margin:0; color: #25D366 !important;">Total: R$ {valor_total:.2f}</h2>
    <p style="color: white; margin:0;">Este é seu pedido nº {st.session_state.total_pedidos_cliente + 1}</p>
</div>""", unsafe_allow_html=True)

if st.button("🚀 FINALIZAR E SALVAR DADOS"):
    if not nome or not endereco:
        st.error("⚠️ Preencha nome e endereço!")
    elif valor_total == 0:
        st.warning("⚠️ Carrinho vazio!")
    else:
        # Aumenta o contador de pedidos
        st.session_state.total_pedidos_cliente += 1
        
        resumo = ""
        for item in escolhidos: resumo += f"• {item}\n"
        if escolha_tamanho != "Não vou montar um agora":
            resumo += f"• Monte seu {escolha_tamanho}\n"

        msg = (
            f"🍧 *JUBILU DELIVERY - PEDIDO #{st.session_state.total_pedidos_cliente}*\n\n"
            f"👤 *Cliente:* {nome}\n"
            f"📍 *Endereço:* {endereco}\n"
            f"💳 *Pagamento:* {pagamento}\n"
            f"---------------------------\n"
            f"{resumo}"
            f"💰 *TOTAL: R$ {valor_total:.2f}*"
        )
        
        # Seu número de Nova Serrana
        meu_zap = "5537991031933"
        link = f"https://wa.me/{meu_zap}?text={urllib.parse.quote(msg)}"
        st.markdown(f'<meta http-equiv="refresh" content="0;URL={link}">', unsafe_allow_html=True)
