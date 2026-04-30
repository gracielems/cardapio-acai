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
    .secao { color: #4B0082; font-weight: bold; border-bottom: 2px solid #4B0082; padding-bottom: 5px; margin-top: 30px; }
    .stButton>button { 
        width: 100%; background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        color: white !important; border-radius: 15px; font-weight: bold; height: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="banner"><h1>🍧 Jubilu Delivery</h1><p>Nova Serrana - O melhor açaí da região!</p></div>', unsafe_allow_html=True)

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

# --- ABA 2: MONTE O SEU (COM AS SUAS FOTOS WEBP) ---
with tab2:
    st.markdown('<div class="secao">1. ESCOLHA O TAMANHO</div>', unsafe_allow_html=True)
    
    # ⚠️ MUDE A PALAVRA 'SEU_USUARIO' PARA O SEU NOME DO GITHUB ⚠️
    tamanhos = {
        "300ml": {
            "preco": 13.00, 
            "foto": "https://raw.githubusercontent.com/SEU_USUARIO/cardapio-acai/main/copo300.webp"
        },
        "500ml": {
            "preco": 18.00, 
            "foto": "https://raw.githubusercontent.com/SEU_USUARIO/cardapio-acai/main/copo500.webp"
        },
        "700ml": {
            "preco": 23.00, 
            "foto": "https://raw.githubusercontent.com/SEU_USUARIO/cardapio-acai/main/copo700.webp"
        },
        "1 Litro": {
            "preco": 32.00, 
            "foto": "https://raw.githubusercontent.com/SEU_USUARIO/cardapio-acai/main/copo1l.webp"
        }
    }
    
    escolha = st.selectbox("Selecione o copo:", ["Nenhum"] + list(tamanhos.keys()))
    
    if escolha != "Nenhum":
        # Mostra a foto do copo selecionado
        st.image(tamanhos[escolha]["foto"], width=250)
        valor_total += tamanhos[escolha]["preco"]
        itens_pedido.append(f"Copo {escolha}")

        # --- ADICIONAIS ---
        st.markdown('<div class="secao">2. ADICIONAIS (R$ 3,00 cada)</div>', unsafe_allow_html=True)
        extras_3 = ["Banana", "Bis Branco", "Bis Preto", "Leite em Pó", "Paçoca", "Amendoim", "Granola", "Coco Ralado", "Gotas de Chocolate", "Oreo", "Disquete", "Chocoboll", "Leite Condensado", "Cobertura Chocolate", "Cobertura Morango", "Chantilly"]
        
        c1, c2 = st.columns(2)
        for i, item in enumerate(extras_3):
            col = c1 if i % 2 == 0 else c2
            if col.checkbox(item):
                itens_pedido.append(f"Add: {item}")
                valor_total += 3.00
                
        st.markdown('<div class="secao">3. PREMIUM</div>', unsafe_allow_html=True)
        if st.checkbox("Creme de Avelã (+R$ 6,00)"):
            itens_pedido.append("Add: Creme de Avelã"); valor_total += 6.00
        if st.checkbox("Creme Laka Oreo (+R$ 6,00)"):
            itens_pedido.append("Add: Creme Laka Oreo"); valor_total += 6.00
        if st.checkbox("Nutella Original (+R$ 8,00)"):
            itens_pedido.append("Add: Nutella"); valor_total += 8.00

# --- FINALIZAÇÃO ---
st.markdown("---")
st.markdown(f"### Total: R$ {valor_total:.2f}")

nome = st.text_input("Seu Nome:")
end = st.text_area("Endereço:")
pagamento = st.selectbox("Pagamento:", ["Pix", "Cartão", "Dinheiro"])

if st.button("✅ ENVIAR PEDIDO"):
    if not LOJA_ABERTA:
        st.error("Loja fechada!")
    elif valor_total == 0 or not nome or not end:
        st.warning("Preencha todos os campos e escolha seus itens!")
    else:
        resumo = "\n".join(itens_pedido)
        msg = f"🍧 *PEDIDO JUBILU*\n\n*Cliente:* {nome}\n*Endereço:* {end}\n*Pagamento:* {pagamento}\n\n*Itens:*\n{resumo}\n\n*TOTAL: R$ {valor_total:.2f}*"
        link = f"https://wa.me/5537991031933?text={urllib.parse.quote(msg)}"
        st.markdown(f'<meta http-equiv="refresh" content="0;URL={link}">', unsafe_allow_html=True)
