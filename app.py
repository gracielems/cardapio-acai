import streamlit as st
import urllib.parse

# Configurações de Página
st.set_page_config(page_title="Forever Açaí", page_icon="🍧", layout="centered")

# Estilização para corrigir o erro do Modo Escuro e melhorar o visual
st.markdown("""
    <style>
    /* Força o fundo claro e texto escuro em tudo */
    .stApp { background-color: #ffffff; color: #31333F; }
    
    /* Garante que títulos e textos fiquem visíveis */
    h1, h2, h3, p, span, label { color: #31333F !important; }
    
    .main-title { color: #4B0082 !important; text-align: center; font-size: 32px; font-weight: bold; margin-bottom: 5px; }
    
    .section-header { 
        background-color: #4B0082; 
        color: white !important; 
        padding: 10px; 
        border-radius: 8px; 
        margin-top: 20px; 
        margin-bottom: 15px;
        font-weight: bold;
        text-align: center;
    }

    /* Estilo dos campos de texto e caixas de seleção */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        color: #31333F !important;
        background-color: #f0f2f6 !important;
    }
    
    /* Botão Principal */
    .stButton>button { 
        width: 100%; 
        background-color: #25D366; 
        color: white !important; 
        border-radius: 25px; 
        font-weight: bold; 
        height: 3.5em; 
        border: none;
    }
    
    /* Remove a margem do topo para mobile */
    .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# Título Principal
st.markdown('<div class="main-title">🍧 Forever Açaí</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-weight: bold;'>O melhor de Nova Serrana direto na sua casa!</p>", unsafe_allow_html=True)

# --- SEÇÃO 1: COPOS MONTADOS ---
st.markdown('<div class="section-header">🔥 COMBOS MAIS PEDIDOS</div>', unsafe_allow_html=True)

copos_prontos = {
    "Açaí Laka Oreo (500ml)": {"preco": 28.00, "desc": "Capa de Laka Oreo, Oreo crocante, leite em pó e açaí."},
    "Clássico com Morango (500ml)": {"preco": 27.00, "desc": "Morangos frescos, leite em pó e leite condensado."},
    "Açaí Sensação (700ml)": {"preco": 29.99, "desc": "Bombom Sonho de Valsa, banana e calda de morango."},
    "Açaí Nutella Premium (500ml)": {"preco": 34.00, "desc": "Nutella original, morango e leite em pó ninho."}
}

selecao_prontos = []
for nome, info in copos_prontos.items():
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.checkbox(f"**{nome}**", key=nome):
            selecao_prontos.append((nome, info['preco']))
        st.write(f"<small>{info['desc']}</small>", unsafe_allow_html=True)
    with col2:
        st.write(f"**R$ {info['preco']:.2f}**")
    st.markdown("---")

# --- SEÇÃO 2: MONTE DO SEU JEITO ---
st.markdown('<div class="section-header">🛠️ MONTE SEU COPO</div>', unsafe_allow_html=True)

tamanhos = {"500ml": 18.00, "700ml": 23.00, "1 Litro": 32.00}
escolha_tamanho = st.selectbox("Escolha o tamanho:", ["Vou de Combo"] + list(tamanhos.keys()))

preco_base_monte = 0.0
selecionados_gratis = []
selecionados_pagos = []
valor_adicionais = 0.0

if escolha_tamanho != "Vou de Combo":
    preco_base_monte = tamanhos[escolha_tamanho]
    
    st.write("**Inclusos (Até 3):**")
    itens_gratis = ["Leite em Pó", "Granola", "Paçoca", "Banana", "Leite Condensado", "Confeti"]
    selecionados_gratis = st.multiselect("Selecione os grátis:", itens_gratis)
    
    st.write("**Adicionais (+R$):**")
    adicionais = {"Morango 🍓": 4.00, "Nutella 🍫": 6.00, "Creme de Ninho 🥛": 5.00}
    for item, preco in adicionais.items():
        if st.checkbox(f"{item} (+R${preco:.2f})"):
            selecionados_pagos.append(item)
            valor_adicionais += preco

# --- SEÇÃO 3: FINALIZAÇÃO ---
st.markdown('<div class="section-header">📍 ENTREGA</div>', unsafe_allow_html=True)

nome = st.text_input("Seu Nome:")
endereco = st.text_area("Endereço e Referência:")
pagamento = st.selectbox("Pagamento:", ["Pix", "Cartão", "Dinheiro"])

troco = ""
if pagamento == "Dinheiro":
    troco = st.text_input("Troco para quanto?")

# Cálculo Final
valor_total = sum(p for n, p in selecao_prontos) + preco_base_monte + valor_adicionais

st.markdown(f"<div style='background-color: #f0f2f6; padding: 15px; border-radius: 10px; text-align: center;'>"
            f"<h2 style='margin:0; color: #4B0082;'>Total: R$ {valor_total:.2f}</h2>"
            f"</div>", unsafe_allow_html=True)

if st.button("✅ FINALIZAR NO WHATSAPP"):
    if not nome or not endereco:
        st.error("Preencha o nome e o endereço!")
    elif valor_total == 0:
        st.warning("Carrinho vazio!")
    else:
        # Texto para o Zap
        resumo = ""
        for n, p in selecao_prontos: resumo += f"• {n}\n"
        if escolha_tamanho != "Vou de Combo":
            resumo += f"• Monte seu {escolha_tamanho}\n  Grátis: {', '.join(selecionados_gratis)}\n  Extras: {', '.join(selecionados_pagos)}\n"

        msg = (
            f"🍧 *PEDIDO - FOREVER AÇAÍ*\n\n"
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
