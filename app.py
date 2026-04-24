import streamlit as st
import urllib.parse

# Configurações de Página
st.set_page_config(page_title="Cardápio Jubilu", page_icon="🍧", layout="centered")

# CSS AVANÇADO PARA VISUAL PREMIUM
st.markdown("""
    <style>
    /* Fundo e Fonte Geral */
    .stApp { background-color: #ffffff; color: #31333F; }
    
    /* Banner do Topo */
    .banner {
        background: linear-gradient(90deg, #4B0082 0%, #8A2BE2 100%);
        padding: 30px;
        border-radius: 0px 0px 30px 30px;
        color: white !important;
        text-align: center;
        margin: -60px -20px 30px -20px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
    }
    
    .main-title { font-size: 38px; font-weight: bold; margin: 0; color: white !important; }
    .sub-title { font-size: 16px; opacity: 0.9; color: white !important; }

    /* Estilo dos Cabeçalhos de Seção */
    .section-header { 
        color: #4B0082 !important; 
        font-size: 22px;
        font-weight: bold;
        border-bottom: 3px solid #4B0082;
        padding-bottom: 5px;
        margin-top: 30px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
    }

    /* Cards de Produtos */
    .product-card {
        background-color: #fcfaff;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #e0d5f5;
        margin-bottom: 15px;
    }

    /* Inputs e Selects mais elegantes */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        border-radius: 10px !important;
        border: 1px solid #d1d1d1 !important;
        background-color: #fcfaff !important;
        color: #31333F !important;
    }

    /* Botão de Enviar Estilizado */
    .stButton>button { 
        width: 100%; 
        background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        color: white !important; 
        border-radius: 15px; 
        font-weight: bold; 
        height: 4em; 
        border: none;
        font-size: 18px;
        transition: 0.3s;
        box-shadow: 0px 4px 10px rgba(37, 211, 102, 0.4);
    }
    
    /* Texto de Ajuda/Legenda */
    small { color: #666 !important; }
    label { font-weight: bold !important; color: #4B0082 !important; }
    
    </style>
    """, unsafe_allow_html=True)

# --- TOPO PERSONALIZADO ---
st.markdown("""
    <div class="banner">
        <h1 class="main-title">🍧 Jubilu Delivery</h1>
        <p class="sub-title">O Açaí mais amado de Nova Serrana!</p>
    </div>
    """, unsafe_allow_html=True)

# --- SEÇÃO 1: COMBOS ---
st.markdown('<div class="section-header">🔥 NOSSOS COMBOS MAIS VENDIDOS</div>', unsafe_allow_html=True)

copos_prontos = {
    "🍫 Açaí Laka Oreo (500ml)": {"preco": 28.00, "desc": "Capa de Laka Oreo, Oreo crocante, leite em pó e muito açaí."},
    "🍓 Clássico Morango (500ml)": {"preco": 27.00, "desc": "Morangos frescos, leite em pó e leite condensado."},
    "💣 Açaí Sensação (700ml)": {"preco": 29.99, "desc": "Sonho de Valsa, banana fatiada e calda de morango."},
    "⭐ Nutella Premium (500ml)": {"preco": 34.00, "desc": "Muita Nutella original, morango e leite Ninho."}
}

selecao_prontos = []
for nome, info in copos_prontos.items():
    with st.container():
        st.markdown(f"""
            <div class="product-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; font-size: 18px; color: #31333F;">{nome}</span>
                    <span style="color: #4B0082; font-weight: bold;">R$ {info['preco']:.2f}</span>
                </div>
                <p style="margin: 5px 0; font-size: 14px; color: #555;">{info['desc']}</p>
            </div>
        """, unsafe_allow_html=True)
        if st.checkbox(f"Adicionar {nome}", key=nome):
            selecao_prontos.append((nome, info['preco']))
    st.markdown("<br>", unsafe_allow_html=True)

# --- SEÇÃO 2: MONTE SEU COPO ---
st.markdown('<div class="section-header">🛠️ MONTE SEU COPO DO ZERO</div>', unsafe_allow_html=True)

tamanhos = {"500ml": 18.00, "700ml": 23.00, "1 Litro": 32.00}
escolha_tamanho = st.selectbox("1. Escolha o tamanho base:", ["Clique para selecionar..."] + list(tamanhos.keys()))

preco_base_monte = 0.0
selecionados_gratis = []
selecionados_pagos = []
valor_adicionais = 0.0

if escolha_tamanho != "Clique para selecionar...":
    preco_base_monte = tamanhos[escolha_tamanho]
    
    st.markdown("---")
    st.write("✨ **2. Escolha 3 Acompanhamentos Grátis:**")
    itens_gratis = ["Leite em Pó", "Granola", "Paçoca", "Banana", "Leite Condensado", "Confeti"]
    selecionados_gratis = st.multiselect("Selecione até 3 itens:", itens_gratis)
    
    st.markdown("---")
    st.write("🍫 **3. Adicionais Extras (Opcional):**")
    adicionais = {"Morango 🍓": 4.00, "Nutella 🍫": 6.00, "Creme de Ninho 🥛": 5.00}
    
    col_a, col_b = st.columns(2)
    for i, (item, preco) in enumerate(adicionais.items()):
        target_col = col_a if i % 2 == 0 else col_b
        if target_col.checkbox(f"{item} (+R${preco:.2f})"):
            selecionados_pagos.append(item)
            valor_adicionais += preco

# --- SEÇÃO 3: FINALIZAÇÃO ---
st.markdown('<div class="section-header">📍 INFORMAÇÕES DE ENTREGA</div>', unsafe_allow_html=True)

nome = st.text_input("Nome do Cliente:")
endereco = st.text_area("Endereço completo (Rua, Nº, Bairro):")

col_pag, col_troco = st.columns(2)
with col_pag:
    pagamento = st.selectbox("Forma de Pagamento:", ["Pix", "Cartão", "Dinheiro"])
with col_troco:
    troco = ""
    if pagamento == "Dinheiro":
        troco = st.text_input("Troco para quanto?")

# Cálculo Final
valor_total = sum(p for n, p in selecao_prontos) + preco_base_monte + valor_adicionais

st.markdown(f"""
    <div style="background-color: #4B0082; padding: 20px; border-radius: 15px; text-align: center; margin-top: 30px;">
        <h3 style="margin:0; color: white !important;">Resumo do Pedido</h3>
        <h2 style="margin:0; color: #25D366 !important;">Total: R$ {valor_total:.2f}</h2>
    </div>
    <br>
""", unsafe_allow_html=True)

if st.button("✅ ENVIAR PEDIDO AGORA"):
    if not nome or not endereco:
        st.error("⚠️ Preencha seu nome e endereço!")
    elif valor_total == 0:
        st.warning("⚠️ Adicione algum item ao carrinho!")
    else:
        # Formatação para o WhatsApp
        resumo = ""
        for n, p in selecao_prontos: resumo += f"• {n}\n"
        if escolha_tamanho != "Clique para selecionar...":
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

st.markdown("<br><p style='text-align: center; color: #999;'>🚀 Desenvolvido por Jubilu Açaí</p>", unsafe_allow_html=True)
