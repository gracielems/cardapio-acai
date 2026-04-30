import streamlit as st
import urllib.parse
import pandas as pd

# --- CONEXÃO COM A PLANILHA (CONTROLE DE HORÁRIO) ---
LINK_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQA1CUqaVNElv3-c_Ylb1XKH3_z1h5h1dbH66HkKRIafoh6lheQ5z-MY6oKMSkkqGnsxUXryigtPm3N/pub?output=csv"

def verificar_loja_aberta():
    try:
        df = pd.read_csv(LINK_PLANILHA)
        status = str(df.columns[0]).strip().upper()
        return True if "SIM" in status else False
    except:
        return True

LOJA_ABERTA = verificar_loja_aberta()

# --- CONFIGURAÇÃO DE DESIGN ---
st.set_page_config(page_title="Jubilu Açaí", page_icon="🍧")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .banner {
        background: linear-gradient(90deg, #4B0082 0%, #8A2BE2 100%);
        padding: 25px; border-radius: 0px 0px 30px 30px;
        color: white !important; text-align: center; margin: -60px -20px 20px -20px;
    }
    .produto-card {
        border: 1px solid #eee; padding: 10px; border-radius: 15px;
        margin-bottom: 10px; background-color: #fcfcfc;
    }
    .stButton>button { 
        width: 100%; background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        color: white !important; border-radius: 15px; font-weight: bold; height: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TOPO ---
st.markdown('<div class="banner"><h1>🍧 Jubilu Delivery</h1><p>Nova Serrana - O melhor açaí da região!</p></div>', unsafe_allow_html=True)

if not LOJA_ABERTA:
    st.error("🚨 Estamos FECHADOS agora. Você pode olhar o cardápio, mas não conseguirá enviar o pedido.")

# --- MEMÓRIA DO CLIENTE ---
if 'nome_salvo' not in st.session_state: st.session_state.nome_salvo = ""
if 'end_salvo' not in st.session_state: st.session_state.end_salvo = ""

# --- ORGANIZAÇÃO POR ABAS ---
tab1, tab2 = st.tabs(["🔥 Combos Prontos", "🛠️ Monte o Seu"])

itens_pedido = []
valor_total = 0.0

# --- ABA 1: COMBOS PRONTOS ---
with tab1:
    st.markdown("### Escolha um de nossos favoritos:")
    combos = {
        "🍫 Laka Oreo (500ml)": {"preco": 28.00, "desc": "Capa de Laka Oreo, Oreo crocante e leite em pó."},
        "🍓 Clássico Morango (500ml)": {"preco": 27.00, "desc": "Morangos, leite em pó e leite condensado."},
        "⭐ Nutella Premium (500ml)": {"preco": 34.00, "desc": "Nutella original, morangos e leite Ninho."}
    }
    
    for nome, info in combos.items():
        with st.container():
            st.markdown(f"**{nome}** - R$ {info['preco']:.2f}")
            st.caption(info['desc'])
            if st.checkbox("Selecionar Combo", key=f"combo_{nome}"):
                itens_pedido.append(f"Combo: {nome}")
                valor_total += info['preco']
            st.markdown("---")

# --- ABA 2: MONTE O SEU ---
with tab2:
    st.markdown("### Monte do seu jeito:")
    
    # Tamanhos
    tamanhos = {"300ml": 13.00, "500ml": 18.00, "700ml": 23.00, "1 Litro": 32.00}
    tamanho_escolhido = st.selectbox("1. Escolha o tamanho:", ["Nenhum"] + list(tamanhos.keys()))
    
    if tamanho_escolhido != "Nenhum":
        itens_pedido.append(f"Copo personalizado ({tamanho_escolhido})")
        valor_total += tamanhos[tamanho_escolhido]
        
        # Adicionais R$ 3,00
        st.markdown("**2. Adicionais (R$ 3,00 cada):**")
        extras_3 = ["Banana", "Bis Branco", "Bis Preto", "Leite em Pó", "Paçoca", "Amendoim", "Granola", "Coco Ralado", "Gotas de Chocolate", "Oreo", "Disquete", "Chocoboll", "Leite Condensado", "Cobertura Chocolate", "Cobertura Morango", "Chantilly"]
        
        c1, c2 = st.columns(2)
        for i, item in enumerate(extras_3):
            col = c1 if i % 2 == 0 else c2
            if col.checkbox(item, key=f"add_{item}"):
                itens_pedido.append(f"Add: {item}")
                valor_total += 3.00
                
        # Adicionais Premium
        st.markdown("**3. Adicionais Premium:**")
        if st.checkbox("Creme de Avelã (+R$ 6,00)"):
            itens_pedido.append("Add: Creme de Avelã")
            valor_total += 6.00
        if st.checkbox("Creme Laka Oreo (+R$ 6,00)"):
            itens_pedido.append("Add: Creme Laka Oreo")
            valor_total += 6.00
        if st.checkbox("Nutella Original (+R$ 8,00)"):
            itens_pedido.append("Add: Nutella")
            valor_total += 8.00

# --- FINALIZAÇÃO (Sempre visível no final) ---
st.markdown("---")
st.markdown(f"## Total do Pedido: R$ {valor_total:.2f}")

nome = st.text_input("Seu Nome:", value=st.session_state.nome_salvo)
endereco = st.text_area("Endereço de Entrega:", value=st.session_state.end_salvo)
pagamento = st.selectbox("Forma de Pagamento:", ["Pix", "Cartão", "Dinheiro"])

st.session_state.nome_salvo, st.session_state.end_salvo = nome, endereco

if st.button("✅ ENVIAR PEDIDO PARA O WHATSAPP"):
    if not LOJA_ABERTA:
        st.error("Estamos fechados agora!")
    elif valor_total == 0:
        st.warning("Seu carrinho está vazio!")
    elif not nome or not endereco:
        st.warning("Preencha nome e endereço!")
    else:
        resumo_itens = "\n".join(itens_pedido)
        msg = (
            f"🍧 *JUBILU AÇAÍ - NOVO PEDIDO*\n\n"
            f"👤 *Cliente:* {nome}\n"
            f"📍 *Endereço:* {endereco}\n"
            f"💳 *Pagamento:* {pagamento}\n"
            f"---------------------------\n"
            f"{resumo_itens}\n"
            f"---------------------------\n"
            f"💰 *TOTAL: R$ {valor_total:.2f}*"
        )
        link = f"https://wa.me/5537991031933?text={urllib.parse.quote(msg)}"
        st.markdown(f'<meta http-equiv="refresh" content="0;URL={link}">', unsafe_allow_html=True)
