import streamlit as st
import urllib.parse

# Configurações de Página
st.set_page_config(page_title="Forever Açaí", page_icon="🍧", layout="centered")

# Estilização Profissional (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #fcfaff; }
    .main-title { color: #4B0082; text-align: center; font-size: 42px; font-weight: bold; margin-bottom: 5px; }
    .section-header { 
        background-color: #4B0082; 
        color: white; 
        padding: 12px; 
        border-radius: 8px; 
        margin-top: 25px; 
        margin-bottom: 15px;
        font-weight: bold;
        text-align: center;
    }
    /* Estilo para os cards de produtos */
    .product-box {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 10px;
        border: 1px solid #eee;
    }
    .stButton>button { 
        width: 100%; 
        background-color: #25D366; 
        color: white; 
        border-radius: 30px; 
        font-weight: bold; 
        height: 4em; 
        border: none;
        font-size: 18px;
        box-shadow: 0 4px 15px rgba(37, 211, 102, 0.3);
    }
    .stButton>button:hover {
        background-color: #128C7E;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Título Principal
st.markdown('<div class="main-title">🍧 Forever Açaí</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Monte seu copo ou escolha nossas combinações especiais!</p>", unsafe_allow_html=True)

# --- SEÇÃO 1: COPOS MONTADOS ---
st.markdown('<div class="section-header">🔥 NOSSOS COMBOS MAIS PEDIDOS</div>', unsafe_allow_html=True)

copos_prontos = {
    "Açaí Laka Oreo (500ml)": {"preco": 28.00, "desc": "Capa de Laka Oreo, Oreo crocante, leite em pó e muito açaí."},
    "Clássico com Morango (500ml)": {"preco": 27.00, "desc": "Morangos frescos selecionados, leite em pó e leite condensado."},
    "Açaí Sensação (700ml)": {"preco": 29.99, "desc": "Bombom Sonho de Valsa picado, banana fatiada e calda de morango."},
    "Açaí Nutella Premium (500ml)": {"preco": 34.00, "desc": "Muita Nutella original, morango e leite em pó ninho."}
}

selecao_prontos = []
for nome, info in copos_prontos.items():
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.checkbox(f"**{nome}**", key=nome):
                selecao_prontos.append((nome, info['preco']))
            st.caption(info['desc'])
        with col2:
            st.markdown(f"**R$ {info['preco']:.2f}**")
        st.markdown("---")

# --- SEÇÃO 2: MONTE DO SEU JEITO ---
st.markdown('<div class="section-header">🛠️ MONTE SEU COPO (PERSONALIZADO)</div>', unsafe_allow_html=True)

tamanhos = {"500ml": 18.00, "700ml": 23.00, "1 Litro": 32.00}
escolha_tamanho = st.selectbox("Escolha o tamanho para montar:", ["Nenhum (Vou de Combo)"] + list(tamanhos.keys()))

preco_base_monte = 0.0
selecionados_gratis = []
selecionados_pagos = []
valor_adicionais = 0.0

if "Nenhum" not in escolha_tamanho:
    preco_base_monte = tamanhos[escolha_tamanho]
    
    st.markdown("#### 🍓 Escolha 3 Acompanhamentos Grátis")
    itens_gratis = ["Leite em Pó", "Granola", "Paçoca", "Banana", "Leite Condensado", "Farinha Láctea", "Confeti"]
    selecionados_gratis = st.multiselect("Selecione até 3:", itens_gratis)
    
    st.markdown("#### 🍫 Adicionais Extras (Opcional)")
    adicionais = {"Morango 🍓": 4.00, "Nutella 🍫": 6.00, "Creme de Ninho 🥛": 5.00, "Mousse de Maracujá 🟡": 3.50}
    
    col_a, col_b = st.columns(2)
    for i, (item, preco) in enumerate(adicionais.items()):
        target_col = col_a if i % 2 == 0 else col_b
        if target_col.checkbox(f"{item} (+R${preco:.2f})", key=f"add_{item}"):
            selecionados_pagos.append(item)
            valor_adicionais += preco

# --- SEÇÃO 3: FINALIZAÇÃO ---
st.markdown('<div class="section-header">📍 DADOS DE ENTREGA</div>', unsafe_allow_html=True)

col_n, col_p = st.columns(2)
nome = col_n.text_input("Seu Nome:")
pagamento = col_p.selectbox("Pagamento:", ["Pix", "Cartão", "Dinheiro"])

endereco = st.text_area("Endereço (Rua, Número, Bairro e Referência):")

troco = ""
if pagamento == "Dinheiro":
    troco = st.text_input("Troco para quanto?")

# Cálculo Final
valor_total = sum(p for n, p in selecao_prontos) + preco_base_monte + valor_adicionais

st.markdown(f"<div style='background-color: #eee; padding: 20px; border-radius: 10px; text-align: center; margin-top: 20px;'>"
            f"<h2 style='margin:0; color: #4B0082;'>Total do Pedido: R$ {valor_total:.2f}</h2>"
            f"</div>", unsafe_allow_html=True)

if st.button("✅ FINALIZAR E ENVIAR PEDIDO"):
    if not nome or not endereco:
        st.error("⚠️ Por favor, preencha o Nome e o Endereço para entrega.")
    elif valor_total == 0:
        st.warning("⚠️ Seu carrinho está vazio! Selecione um item antes.")
    else:
        # Formatação para o WhatsApp
        itens_texto = ""
        for n, p in selecao_prontos:
            itens_texto += f"• {n} (R$ {p:.2f})\n"
        
        if "Nenhum" not in escolha_tamanho:
            itens_texto += f"• Monte seu Açaí {escolha_tamanho}\n"
            if selecionados_gratis: itens_texto += f"   - Inclusos: {', '.join(selecionados_gratis)}\n"
            if selecionados_pagos: itens_texto += f"   - Extras: {', '.join(selecionados_pagos)}\n"

        msg = (
            f"🍧 *PEDIDO - FOREVER AÇAÍ*\n\n"
            f"👤 *Cliente:* {nome}\n"
            f"📍 *Endereço:* {endereco}\n"
            f"💳 *Pagamento:* {pagamento} {'(Troco p/ ' + troco + ')' if troco else ''}\n"
            f"---------------------------\n"
            f"{itens_texto}"
            f"---------------------------\n"
            f"💰 *VALOR TOTAL: R$ {valor_total:.2f}*"
        )
        
        # SEU NÚMERO CONFIGURADO
        meu_zap = "5537991031933" 
        link = f"https://wa.me/{meu_zap}?text={urllib.parse.quote(msg)}"
        
        st.success("Tudo pronto! Redirecionando para o WhatsApp...")
        st.markdown(f'<meta http-equiv="refresh" content="0;URL={link}">', unsafe_allow_html=True)
