import streamlit as st
import urllib.parse

# Configurações de Página
st.set_page_config(page_title="Forever Açaí", page_icon="🍧", layout="centered")

# Estilização Profissional (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .main-title { color: #4B0082; text-align: center; font-size: 40px; font-weight: bold; margin-bottom: 10px; }
    .section-header { background-color: #4B0082; color: white; padding: 10px; border-radius: 5px; margin-top: 20px; margin-bottom: 15px; }
    .product-card { background-color: white; padding: 15px; border-radius: 10px; border-left: 5px solid #4B0082; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    .stButton>button { width: 100%; background-color: #25D366; color: white; border-radius: 20px; font-weight: bold; height: 3.5em; border: none; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">🍧 Forever Açaí</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>O melhor açaí de Nova Serrana direto na sua casa!</p>", unsafe_allow_html=True)

# --- SEÇÃO: COPOS JÁ MONTADOS (O queridinho do pessoal) ---
st.markdown('<div class="section-header">🔥 COPOS MONTADOS (MAIS PEDIDOS)</div>', unsafe_allow_html=True)

copos_prontos = {
    "Açaí Laka Oreo (500ml)": {"preco": 28.00, "desc": "Açaí, creme de Laka, Oreo picado e leite condensado."},
    "Clássico com Morango (500ml)": {"preco": 27.00, "desc": "Açaí, morango fresco, leite em pó e leite condensado."},
    "Açaí Sensação (700ml)": {"preco": 29.99, "desc": "Açaí, bombom Sonho de Valsa, banana e cobertura de morango."}
}

selecao_prontos = []
for nome, info in copos_prontos.items():
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.checkbox(f"**{nome}** \n\n _{info['desc']}_"):
            selecao_prontos.append((nome, info['preco']))
    with col2:
        st.write(f"R$ {info['preco']:.2f}")
    st.markdown("---")

# --- SEÇÃO: MONTE DO SEU JEITO ---
st.markdown('<div class="section-header">🛠️ MONTE SEU AÇAÍ</div>', unsafe_allow_html=True)

tamanhos = {"500ml": 18.00, "700ml": 23.00, "1 Litro": 32.00}
escolha_tamanho = st.selectbox("Escolha o tamanho base:", ["Nenhum"] + list(tamanhos.keys()))

preco_base = 0.0
if escolha_tamanho != "Nenhum":
    preco_base = tamanhos[escolha_tamanho]
    
    col_gratis, col_pagos = st.columns(2)
    with col_gratis:
        st.markdown("**Grátis (Até 3)**")
        itens_gratis = ["Leite em Pó", "Granola", "Paçoca", "Banana", "Leite Condensado"]
        selecionados_gratis = st.multiselect("Escolha:", itens_gratis)
    
    with col_pagos:
        st.markdown("**Adicionais (+R$)**")
        adicionais = {"Morango 🍓": 4.00, "Nutella 🍫": 6.00, "Creme Ninho 🥛": 5.00}
        selecionados_pagos = []
        valor_adicionais = 0.0
        for item, preco in adicionais.items():
            if st.checkbox(f"{item} (R$ {preco:.2f})"):
                selecionados_pagos.append(item)
                valor_adicionais += preco
    preco_base += valor_adicionais
else:
    selecionados_gratis = []
    selecionados_pagos = []

# --- TOTAL E DADOS ---
valor_total = preco_base + sum(p for n, p in selecao_prontos)

st.markdown('<div class="section-header">📍 FINALIZAR PEDIDO</div>', unsafe_allow_html=True)
nome = st.text_input("Seu Nome:")
endereco = st.text_area("Endereço (Rua, Número, Bairro):")
pagamento = st.selectbox("Forma de Pagamento:", ["Pix", "Cartão", "Dinheiro"])

st.markdown(f"<h2 style='text-align: center; color: #4B0082;'>Total: R$ {valor_total:.2f}</h2>", unsafe_allow_html=True)

if st.button("✅ ENVIAR PEDIDO PARA O WHATSAPP"):
    if not nome or not endereco:
        st.error("Por favor, preencha nome e endereço!")
    elif valor_total == 0:
        st.warning("Seu carrinho está vazio!")
    else:
        # Montagem da mensagem
        lista_itens = ""
        for n, p in selecao_prontos:
            lista_itens += f"- {n} (R$ {p:.2f})\n"
        if escolha_tamanho != "Nenhum":
            lista_itens += f"- Monte seu Açaí ({escolha_tamanho})\n  Inclusos: {', '.join(selecionados_gratis)}\n  Extras: {', '.join(selecionados_pagos)}\n"

        msg = (
            f"🍧 *FOREVER AÇAÍ - NOVO PEDIDO*\n\n"
            f"👤 *Cliente:* {nome}\n"
            f"📍 *Endereço:* {endereco}\n"
            f"💳 *Pagamento:* {pagamento}\n"
            f"----------------------------\n"
            f"{lista_itens}"
            f"----------------------------\n"
            f"💰 *VALOR TOTAL: R$ {valor_total:.2f}*"
        )
        # COLOQUE SEU NÚMERO ABAIXO
        meu_zap = "5537991031933" 
        link = f"https://wa.me/{meu_zap}?text={urllib.parse.quote(msg)}"
        st.markdown(f'<meta http-equiv="refresh" content="0;URL={link}">', unsafe_allow_html=True)
        st.success("Redirecionando para o WhatsApp...")
