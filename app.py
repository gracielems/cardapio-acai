import streamlit as st
import urllib.parse
import pandas as pd
import os

# --- CONEXÃO COM A PLANILHA ---
LINK_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQA1CUqaVNElv3-c_Ylb1XKH3_z1h5h1dbH66HkKRIafoh6lheQ5z-MY6oKMSkkqGnsxUXryigtPm3N/pub?output=csv"

def verificar_loja_aberta():
    try:
        df = pd.read_csv(LINK_PLANILHA)
        status = str(df.columns[0]).strip().upper()
        return "SIM" in status
    except:
        return True # Se falhar, mantém aberta para não perder venda

LOJA_ABERTA = verificar_loja_aberta()

# --- CONFIGURAÇÃO DE DESIGN ---
st.set_page_config(page_title="Jubileu Açaí", page_icon="🍧", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .secao { color: #4B0082; font-weight: bold; border-bottom: 2px solid #4B0082; padding-bottom: 5px; margin-top: 20px; margin-bottom: 15px; }
    div.stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        color: white !important;
        border-radius: 10px;
        font-weight: bold;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO ---
# Simplifiquei a busca pela imagem
logo_files = ["logo3d.jpg.png", "logo3d.png", "logo3d.jpg"]
logo_found = False
for logo in logo_files:
    if os.path.exists(logo):
        st.image(logo, use_container_width=True)
        logo_found = True
        break
if not logo_found:
    st.title("🍧 Jubileu Açaí")

# --- ESTADO DO PEDIDO ---
itens_pedido = []
valor_total = 0.0

# --- ABAS ---
tab1, tab2 = st.tabs(["🔥 Combos Prontos", "Monte o Seu"])

with tab1:
    combos = {
        "🍫 Laka Oreo (500ml)": {"preco": 28.00, "desc": "Capa de Laka Oreo, Oreo crocante e leite em pó."},
        "🍓 Clássico Morango (500ml)": {"preco": 27.00, "desc": "Morangos, leite em pó e leite condensado."},
        "⭐ Nutella Premium (500ml)": {"preco": 34.00, "desc": "Nutella original, morangos e leite Ninho."}
    }
    for nome, info in combos.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{nome}**")
            st.caption(info['desc'])
            st.markdown(f"**R$ {info['preco']:.2f}**")
        with col2:
            if st.checkbox("Adicionar", key=f"c_{nome}"):
                itens_pedido.append(f"- {nome}")
                valor_total += info['preco']
        st.markdown("---")

with tab2:
    st.markdown('<div class="secao">1. ESCOLHA O TAMANHO</div>', unsafe_allow_html=True)
    tamanhos = {
        "300ml": 13.00,
        "500ml": 18.00,
        "700ml": 23.00,
        "1 Litro": 32.00
    }
    escolha = st.radio("Selecione o copo:", ["Nenhum"] + list(tamanhos.keys()), horizontal=True)
    
    if escolha != "Nenhum":
        valor_total += tamanhos[escolha]
        itens_pedido.append(f"- Copo {escolha} (Base)")

        st.markdown('<div class="secao">2. ADICIONAIS (R$ 3,00 cada)</div>', unsafe_allow_html=True)
        extras = ["Banana", "Bis Branco", "Leite em Pó", "Paçoca", "Granola", "Oreo", "Leite Condensado", "Nutella (Extra)"]
        
        c1, c2 = st.columns(2)
        for i, item in enumerate(extras):
            col = c1 if i % 2 == 0 else c2
            if col.checkbox(item, key=f"add_{item}"):
                itens_pedido.append(f"  + Add: {item}")
                valor_total += 3.00

# --- FECHAMENTO ---
st.markdown('<div class="secao">FINALIZAR PEDIDO</div>', unsafe_allow_html=True)
st.markdown(f"### Total: R$ {valor_total:.2f}")

nome_cli = st.text_input("Seu Nome:")
end_cli = st.text_input("Endereço e Bairro:")
pag_cli = st.selectbox("Forma de Pagamento:", ["Pix", "Cartão (Levar maquininha)", "Dinheiro"])

if st.button("✅ ENVIAR PEDIDO PARA O WHATSAPP"):
    if not LOJA_ABERTA:
        st.error("❌ Desculpe, a loja está fechada no momento!")
    elif valor_total == 0:
        st.warning("Seu carrinho está vazio!")
    elif not nome_cli or not end_cli:
        st.warning("Por favor, preencha seu nome e endereço!")
    else:
        resumo = "\n".join(itens_pedido)
        # Construção da mensagem com todos os dados
        msg = (
            f"🍧 *NOVO PEDIDO - JUBILEU AÇAÍ*\n"
            f"------------------------------\n"
            f"*Cliente:* {nome_cli}\n"
            f"*Endereço:* {end_cli}\n"
            f"------------------------------\n"
            f"*Itens:*\n{resumo}\n"
            f"------------------------------\n"
            f"*Pagamento:* {pag_cli}\n"
            f"*TOTAL: R$ {valor_total:.2f}*"
        )
        
        # Link para o WhatsApp
        whatsapp_link = f"https://wa.me/5537991031933?text={urllib.parse.quote(msg)}"
        
        # Script para abrir em nova aba (mais confiável que o meta refresh)
        st.markdown(f'<a href="{whatsapp_link}" target="_blank" style="text-decoration: none;"><button style="width: 100%; background-color: #25D366; color: white; border: none; padding: 15px; border-radius: 10px; font-weight: bold; cursor: pointer;">TUDO PRONTO! CLIQUE AQUI PARA ENVIAR</button></a>', unsafe_allow_html=True)
