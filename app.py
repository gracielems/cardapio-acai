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
st.set_page_config(page_title="Jubilu Açaí - Monte o Seu", page_icon="🍧")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .banner {
        background: linear-gradient(90deg, #4B0082 0%, #8A2BE2 100%);
        padding: 25px; border-radius: 0px 0px 30px 30px;
        color: white !important; text-align: center; margin: -60px -20px 20px -20px;
    }
    .secao { 
        color: #4B0082; font-weight: bold; border-bottom: 2px solid #4B0082;
        padding-bottom: 5px; margin-top: 30px; margin-bottom: 15px;
    }
    .total-card {
        background-color: #4B0082; padding: 20px; border-radius: 15px;
        text-align: center; color: white !important;
    }
    .stButton>button { 
        width: 100%; background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        color: white !important; border-radius: 15px; font-weight: bold; height: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TOPO ---
st.markdown('<div class="banner"><h1>🍧 Jubilu Delivery</h1><p>Nova Serrana - O açaí do seu jeito!</p></div>', unsafe_allow_html=True)

if not LOJA_ABERTA:
    st.error("🚫 Estamos fechados agora. Você pode simular seu pedido, mas não conseguirá enviar para o WhatsApp.")

# --- PASSO 1: TAMANHOS ---
st.markdown('<div class="secao">1. ESCOLHA O TAMANHO DO COPO</div>', unsafe_allow_html=True)
tamanhos = {
    "Copo 300ml": 13.00,
    "Copo 500ml": 18.00,
    "Copo 700ml": 23.00,
    "Copo 1 Litro": 32.00
}
escolha_tamanho = st.selectbox("Selecione o tamanho:", list(tamanhos.keys()))
preco_base = tamanhos[escolha_tamanho]

# --- PASSO 2: ADICIONAIS ---
st.markdown('<div class="secao">2. ADICIONAIS (Monte como quiser)</div>', unsafe_allow_html=True)

# Lista de R$ 3,00
extras_3 = [
    "Banana", "Bis Branco", "Bis Preto", "Leite em Pó", "Paçoca", "Amendoim", 
    "Granola", "Coco Ralado", "Gotas de Chocolate", "Oreo", "Disquete", 
    "Chocoboll", "Leite Condensado", "Cobertura de Chocolate", 
    "Cobertura de Morango", "Chantilly"
]

# Lista de R$ 6,00 e R$ 8,00
extras_premium = {
    "Creme de Avelã": 6.00,
    "Creme Laka Oreo": 6.00,
    "Nutella": 8.00
}

selecionados = []
valor_adicionais = 0.0

st.write("**Itens de R$ 3,00 cada:**")
# Organizando em colunas para o celular
col1, col2 = st.columns(2)
for i, item in enumerate(extras_3):
    col_alvo = col1 if i % 2 == 0 else col2
    if col_alvo.checkbox(item):
        selecionados.append(item)
        valor_adicionais += 3.00

st.write("**Premium:**")
for item, preco in extras_premium.items():
    if st.checkbox(f"{item} (+R$ {preco:.2f})"):
        selecionados.append(item)
        valor_adicionais += preco

# --- RESUMO E DADOS ---
total_final = preco_base + valor_adicionais

st.markdown(f"""
    <div class="total-card">
        <h3 style="margin:0;">Total do seu Pedido</h3>
        <h1 style="margin:0; color: #25D366 !important;">R$ {total_final:.2f}</h1>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="secao">3. ENTREGA E PAGAMENTO</div>', unsafe_allow_html=True)

# Recuperação de memória do cliente
if 'nome_salvo' not in st.session_state: st.session_state.nome_salvo = ""
if 'end_salvo' not in st.session_state: st.session_state.end_salvo = ""
if 'pedidos_count' not in st.session_state: st.session_state.pedidos_count = 0

nome = st.text_input("Seu Nome:", value=st.session_state.nome_salvo)
endereco = st.text_area("Endereço Completo:", value=st.session_state.end_salvo)
pagamento = st.selectbox("Forma de Pagamento:", ["Pix", "Cartão", "Dinheiro"])

# Salva na memória
st.session_state.nome_salvo = nome
st.session_state.end_salvo = endereco

st.success("🚚 Frete Grátis em Nova Serrana!")

# --- BOTÃO FINALIZAR ---
if st.button("🚀 ENVIAR PEDIDO"):
    if not LOJA_ABERTA:
        st.error("Loja fechada! Não podemos receber pedidos agora.")
    elif not nome or not endereco:
        st.warning("Preencha seu nome e endereço!")
    else:
        st.session_state.pedidos_count += 1
        lista_final = ", ".join(selecionados) if selecionados else "Sem adicionais"
        
        msg = (
            f"🍧 *JUBILU AÇAÍ - NOVO PEDIDO*\n\n"
            f"👤 *Cliente:* {nome}\n"
            f"📍 *Endereço:* {endereco}\n"
            f"💳 *Pagamento:* {pagamento}\n"
            f"---------------------------\n"
            f"📦 *Tamanho:* {escolha_tamanho}\n"
            f"✨ *Adicionais:* {lista_final}\n"
            f"---------------------------\n"
            f"💰 *TOTAL: R$ {total_final:.2f}*\n"
            f"🚀 *Este é o pedido nº {st.session_state.pedidos_count} deste cliente!*"
        )
        
        link = f"https://wa.me/5537991031933?text={urllib.parse.quote(msg)}"
        st.markdown(f'<meta http-equiv="refresh" content="0;URL={link}">', unsafe_allow_html=True)
