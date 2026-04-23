import streamlit as st
import urllib.parse

# Configurações de Estilo
st.set_page_config(page_title="Cardápio Digital - Açaí", page_icon="🍧")

st.markdown("""
    <style>
    .stButton>button { width: 100%; background-color: #4B0082; color: white; border-radius: 10px; font-weight: bold; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

st.title("🍧 Seu Delivery de Açaí")
st.write("Monte seu pedido de forma rápida!")
st.markdown("---")

# 1. TAMANHO
st.subheader("1. Escolha o Tamanho")
tamanhos = {
    "500ml 🥤": 18.00,
    "700ml 🥤": 23.00,
    "1 Litro 🍧": 32.00
}
escolha_tamanho = st.radio("Selecione uma opção:", list(tamanhos.keys()))
preco_base = tamanhos[escolha_tamanho]

# 2. COMPLEMENTOS GRÁTIS
with st.expander("🍓 Acompanhamentos Grátis (Escolha seus favoritos)"):
    itens_gratis = ["Leite em Pó", "Granola", "Paçoca", "Banana", "Leite Condensado", "Farinha Láctea"]
    selecionados_gratis = st.multiselect("Selecione:", itens_gratis)

# 3. ADICIONAIS PAGOS
with st.expander("🍫 Adicionais Extras (Opcional)"):
    adicionais = {
        "Morango 🍓": 4.00,
        "Nutella 🍫": 6.00,
        "Mousse de Morango 🍓": 3.50,
        "Creme de Ninho 🥛": 5.00
    }
    selecionados_pagos = []
    valor_adicionais = 0.0
    for item, preco in adicionais.items():
        if st.checkbox(f"{item} (+ R$ {preco:.2f})"):
            selecionados_pagos.append(item)
            valor_adicionais += preco

# 4. ENTREGA E PAGAMENTO
st.markdown("---")
st.subheader("📍 Entrega e Pagamento")
nome = st.text_input("Seu Nome:")
endereco = st.text_area("Endereço Completo:")
pagamento = st.selectbox("Forma de Pagamento:", ["Pix", "Cartão", "Dinheiro"])

troco = ""
if pagamento == "Dinheiro":
    troco = st.text_input("Troco para quanto?")

# FINALIZAÇÃO
valor_total = preco_base + valor_adicionais
st.markdown("---")
st.write(f"### Total: R$ {valor_total:.2f}")

if st.button("🚀 ENVIAR PEDIDO PELO WHATSAPP"):
    if not nome or not endereco:
        st.error("⚠️ Por favor, preencha o nome e o endereço.")
    else:
        msg = (
            f"🔔 *NOVO PEDIDO*\n\n"
            f"👤 *Cliente:* {nome}\n"
            f"📍 *Endereço:* {endereco}\n"
            f"💳 *Pagamento:* {pagamento} {'(Troco: ' + troco + ')' if troco else ''}\n"
            f"----------------------------\n"
            f"🥤 *Item:* {escolha_tamanho}\n"
            f"✅ *Inclusos:* {', '.join(selecionados_gratis)}\n"
            f"➕ *Adicionais:* {', '.join(selecionados_pagos)}\n"
            f"----------------------------\n"
            f"💰 *TOTAL: R$ {valor_total:.2f}*"
        )
        # Substitua o número abaixo pelo seu número real com DDD
        link = f"https://wa.me/5537991031933?text={urllib.parse.quote(msg)}"
        st.success("Pedido gerado! Clique abaixo:")
        st.markdown(f'<a href="{link}" target="_blank" style="background-color: #25D366; color: white; padding: 10px; text-align: center; border-radius: 5px; display: block; text-decoration: none; font-weight: bold;">ENVIAR WHATSAPP</a>', unsafe_allow_html=True)
