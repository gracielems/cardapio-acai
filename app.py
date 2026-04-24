import streamlit as st
import urllib.parse

# Configurações de Página
st.set_page_config(page_title="Cardápio Jubilu", page_icon="🍧", layout="centered")

# CSS AVANÇADO
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
        font-size: 20px;
        font-weight: bold;
        border-bottom: 2px solid #4B0082;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    /* Estilo para os cards de combos */
    .combo-info {
        background-color: #f8f4ff;
        padding: 10px;
        border-radius: 10px;
        border-left: 5px solid #4B0082;
        margin-bottom: 5px;
        font-size: 14px;
    }

    .stButton>button { 
        width: 100%; 
        background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        color: white !important; 
        border-radius: 15px; 
        font-weight: bold; 
        height: 3.5em; 
        border: none;
        box-shadow: 0px 4px 10px rgba(37, 211, 102, 0.4);
    }
    
    label { font-weight: bold !important; color: #4B0082 !important; }
    </style>
    """, unsafe_allow_html=True)

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

# Aqui está o segredo: Um multiselect que já mostra os nomes e preços
escolhidos = st.multiselect("Clique abaixo para selecionar seus combos:", list(copos_prontos.keys()))

# Mostrar a descrição apenas do que foi selecionado para não poluir a tela
valor_combos = 0.0
if escolhidos:
    st.write("📋 **Detalhes dos itens selecionados:**")
    for item in escolhidos:
        info = copos_prontos[item]
        st.markdown(f"""<div class="combo-info"><b>{item}</b><br>{info['desc']}</div>""", unsafe_allow_html=True)
        valor_combos += info['preco']

# --- SEÇÃO 2: MONTE SEU COPO ---
st.markdown('<div class="section-header">🛠️ 2. OU MONTE DO SEU JEITO</div>', unsafe_allow_html=True)

tamanhos = {"500ml": 18.00, "700ml": 23.00, "1 Litro": 32.00}
escolha_tamanho = st.selectbox("Selecione um tamanho base:", ["Não vou montar um agora"] + list(tamanhos.keys()))

preco_base_monte = 0.0
selecionados_gratis = []
selecionados_pagos = []
valor_adicionais = 0.0

if escolha_tamanho != "Não vou montar um agora":
    preco_base_monte = tamanhos[escolha_tamanho]
    
    st.write("✨ **Escolha 3 Acompanhamentos Grátis:**")
    itens_gratis = ["Leite em Pó", "Granola", "Paçoca", "Banana", "Leite Condensado", "Confeti"]
    selecionados_gratis = st.multiselect("Itens grátis:", itens_gratis)
    
    st.write("🍫 **Adicionais Extras (Opcional):**")
    adicionais = {"Morango 🍓": 4.00, "Nutella 🍫": 6.00, "Creme de Ninho 🥛": 5.00}
    
    col_a, col_b = st.columns(2)
    for i, (item, preco) in enumerate(adicionais.items()):
        target_col = col_a if i % 2 == 0 else col_b
        if target_col.checkbox(f"{item} (+R${preco:.2f})"):
            selecionados_pagos.append(item)
            valor_adicionais += preco

# --- SEÇÃO 3: FINALIZAÇÃO ---
st.markdown('<div class="section-header">📍 3. ENTREGA E PAGAMENTO</div>', unsafe_allow_html=True)

nome = st.text_input("Seu Nome:")
endereco = st.text_area("Endereço Completo:")
pagamento = st.selectbox("Forma de Pagamento:", ["Pix", "Cartão", "Dinheiro"])

troco = ""
if pagamento == "Dinheiro":
    troco = st.text_input("Troco para quanto?")

# Cálculo Final
valor_total = valor_combos + preco_base_monte + valor_adicionais

st.markdown(f"""
    <div style="background-color: #4B0082; padding: 20px; border-radius: 15px; text-align: center; margin-top: 20px;">
        <h3 style="margin:0; color: white !important;">Total do Pedido</h3>
        <h2 style="margin:0; color: #25D366 !important;">R$ {valor_total:.2f}</h2>
    </div>
    <br>
""", unsafe_allow_html=True)

if st.button("🚀 FINALIZAR PEDIDO NO WHATSAPP"):
    if not nome or not endereco:
        st.error("⚠️ Preencha o nome e o endereço!")
    elif valor_total == 0:
        st.warning("⚠️ Seu carrinho está vazio!")
    else:
        resumo = ""
        for item in escolhidos: resumo += f"• {item}\n"
        if escolha_tamanho != "Não vou montar um agora":
            resumo += f"• Monte seu {escolha_tamanho}\n  Grátis: {', '.join(selecionados_gratis)}\n  Extras: {', '.join(selecionados_pagos)}\n"

        msg = (
            f"🍧 *PEDIDO - JUBILU DELIVERY*\n\n"
            f"👤 *Cliente:* {nome}\n"
            f"📍 *Endereço:* {endereco}\n"
            f"💳 *Pagamento:* {pagamento} {'(Troco: ' + troco + ')' if troco else ''}\n"
            f"---------------------------\n"
            f"{resumo}"
            f"---------------------------\n"
            f"💰 *VALOR TOTAL: R$ {valor_total:.2f}*"
        )
        
        meu_zap = "5537991031933" 
        link = f"https://wa.me/{meu_zap}?text={urllib.parse.quote(msg)}"
        st.markdown(f'<meta http-equiv="refresh" content="0;URL={link}">', unsafe_allow_html=True)
