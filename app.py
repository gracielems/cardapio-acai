import streamlit as st
import urllib.parse
import pandas as pd
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Jubileu Açaí", page_icon="🍧")

# --- LIMPEZA TOTAL DA INTERFACE E ESTILIZAÇÃO PERSONALIZADA ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    [data-testid="stToolbar"] {display: none;}
    .stDeployButton {display:none;}
    .stApp { background-color: #ffffff; }
    
    /* Cores de textos e labels */
    label, p, span, .stMarkdown {
        color: #1a1a1a !important;
        font-weight: 500;
    }
    
    /* Estilo dos Títulos de Seção */
    h1, h2, h3, .secao {
        color: #4B0082 !important;
    }
    .secao { 
        font-weight: bold; 
        border-bottom: 2px solid #4B0082; 
        padding-bottom: 5px; 
        margin-top: 30px; 
        margin-bottom: 15px; 
    }

    /* DESTAQUE NAS ABAS (TEXTO MAIOR) */
    button[data-baseweb="tab"] p {
        font-size: 20px !important;
        font-weight: bold !important;
        color: #4B0082 !important;
    }

    /* Estilo do Botão do WhatsApp */
    .btn-whats {
        display: inline-block; padding: 15px 25px; background-color: #25D366; color: white !important;
        text-align: center; text-decoration: none; font-size: 18px; font-weight: bold;
        border-radius: 15px; width: 100%; border: none; margin-top: 10px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS FIDELIDADE ---
ARQUIVO_CLIENTES = "database_fidelidade.csv"

def carregar_dados_cliente(nome_completo):
    nome_completo = nome_completo.strip().upper()
    if os.path.exists(ARQUIVO_CLIENTES):
        df = pd.read_csv(ARQUIVO_CLIENTES)
        cliente = df[df['nome'] == nome_completo]
        if not cliente.empty: return int(cliente.iloc[0]['pedidos'])
    return 0

def atualizar_pedido_cliente(nome_completo, ganhou_brinde):
    nome_completo = nome_completo.strip().upper()
    if os.path.exists(ARQUIVO_CLIENTES):
        df = pd.read_csv(ARQUIVO_CLIENTES)
    else:
        df = pd.DataFrame(columns=['nome', 'pedidos'])

    if nome_completo in df['nome'].values:
        if ganhou_brinde:
            df.loc[df['nome'] == nome_completo, 'pedidos'] = 0
        else:
            df.loc[df['nome'] == nome_completo, 'pedidos'] += 1
    else:
        df = pd.concat([df, pd.DataFrame({'nome': [nome_completo], 'pedidos': [1]})], ignore_index=True)
    df.to_csv(ARQUIVO_CLIENTES, index=False)

# --- CONTROLE DE HORÁRIO ---
LINK_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQA1CUqaVNElv3-c_Ylb1XKH3_z1h5h1dbH66HkKRIafoh6lheQ5z-MY6oKMSkkqGnsxUXryigtPm3N/pub?output=csv"
def verificar_loja_aberta():
    try:
        df = pd.read_csv(LINK_PLANILHA)
        return "SIM" in str(df.columns[0]).strip().upper()
    except: return True

LOJA_ABERTA = verificar_loja_aberta()

# --- EXIBIÇÃO DA LOGO ---
nomes_logo = ["logo3d.jpg.png", "logo3d.png", "logo3d.jpg", "logo3d.jpeg"]
for nome_arquivo in nomes_logo:
    if os.path.exists(nome_arquivo):
        st.image(nome_arquivo, use_container_width=True)
        break

# --- MONTAGEM DO PEDIDO ---
itens_pedido = []
valor_total = 0.0

tab1, tab2, tab3 = st.tabs(["🔥 Combos", "🥤 Açaí na Garrafa", "🍧 Monte o Seu"])

with tab1:
    combos = {
        "🍫 Laka Oreo (500ml)": 28.00,
        "🍓 Clássico Morango (500ml)": 27.00,
        "⭐ Nutella Premium (500ml)": 34.00
    }
    for nome, preco in combos.items():
        if st.checkbox(f"{nome} - R$ {preco:.2f}", key=f"cb_{nome}"):
            itens_pedido.append(nome)
            valor_total += preco

with tab2:
    st.markdown('<div class="secao">🥤 ESCOLHA SUA GARRAFA (300ml)</div>', unsafe_allow_html=True)
    garrafas = {
        "🥤 Açaí Tradicional": 10.00,
        "🥤 Açaí com Leite em Pó": 13.00,
        "🥤 Açaí com Creme de Morango": 13.00,
        "🥤 Açaí com Creme de Maracujá": 13.00
    }
    for nome, preco in garrafas.items():
        if st.checkbox(f"{nome} - R$ {preco:.2f}", key=f"ga_{nome}"):
            itens_pedido.append(nome)
            valor_total += preco

with tab3:
    st.markdown('<div class="secao">1. TAMANHO DO COPO</div>', unsafe_allow_html=True)
    tamanhos = {"300ml": 13.0, "500ml": 18.0, "700ml": 23.0, "1 Litro": 32.0}
    escolha = st.selectbox("Escolha:", list(tamanhos.keys()), index=None, placeholder="Selecione...")
    if escolha:
        valor_total += tamanhos[escolha]
        itens_pedido.append(f"Copo {escolha}")
        st.markdown('<div class="secao">2. ADICIONAIS (R$ 3,00)</div>', unsafe_allow_html=True)
        extras = ["Banana", "Bis", "Leite em Pó", "Paçoca", "Nutella", "Chantilly"]
        for item in extras:
            if st.checkbox(item, key=f"ex_{item}"):
                itens_pedido.append(f"Adicional {item}")
                valor_total += 3.0

# --- DADOS DO CLIENTE ---
st.markdown('<div class="secao">DADOS DO CLIENTE</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    nome_p = st.text_input("Primeiro Nome:").strip()
with col2:
    sobrenome_p = st.text_input("Sobrenome:").strip()

nome_completo = f"{nome_p} {sobrenome_p}".upper().strip()
ganhou_brinde = False

if nome_p and sobrenome_p:
    qtd = carregar_dados_cliente(nome_completo)
    if qtd == 9:
        ganhou_brinde = True
        st.balloons()
        st.success(f"🎁 PARABÉNS {nome_p.upper()}! Seu 10º pedido é um brinde!")
    else:
        st.info(f"Olá {nome_p.upper()}! Você tem {qtd} pedidos registrados. 💜")

# --- ENDEREÇO DETALHADO ---
st.markdown('<div class="secao">ENDEREÇO DE ENTREGA</div>', unsafe_allow_html=True)
rua = st.text_input("Rua/Avenida:")
col_end1, col_end2 = st.columns([1, 2])
with col_end1:
    numero = st.text_input("Número:")
with col_end2:
    bairro = st.text_input("Bairro:")
referencia = st.text_input("Ponto de Referência:")

# --- PAGAMENTO E TROCO ---
st.markdown('<div class="secao">PAGAMENTO</div>', unsafe_allow_html=True)
pag_cli = st.selectbox("Forma de Pagamento:", ["Pix", "Cartão", "Dinheiro"])

info_troco = ""
if pag_cli == "Dinheiro":
    precisa_troco = st.radio("Precisa de troco?", ["Não", "Sim"])
    if precisa_troco == "Sim":
        valor_troco = st.text_input("Troco para quanto? (Ex: 50)")
        info_troco = f"\n*Troco:* Sim, para R$ {valor_troco}"
    else:
        info_troco = f"\n*Troco:* Não necessário"

# --- FINALIZAÇÃO ---
if st.button("✅ GERAR PEDIDO PARA WHATSAPP"):
    campos_vazios = not (nome_p and sobrenome_p and rua and numero and bairro and referencia)
    
    if not LOJA_ABERTA:
        st.error("LOJA FECHADA!")
    elif valor_total == 0:
        st.warning("Selecione algum item no cardápio!")
    elif campos_vazios:
        st.warning("⚠️ Por favor, preencha TODOS os campos de endereço e nome.")
    else:
        atualizar_pedido_cliente(nome_completo, ganhou_brinde)
        resumo = "\n".join(itens_pedido)
        brinde_txt = "\n\n🎁 *ESTE PEDIDO É UM BRINDE!*" if ganhou_brinde else ""
        
        msg = (
            f"*PEDIDO JUBILEU AÇAÍ*\n"
            f"--------------------------\n"
            f"*Cliente:* {nome_completo}\n"
            f"*Endereço:* {rua}, {numero}\n"
            f"*Bairro:* {bairro}\n"
            f"*Referência:* {referencia}\n"
            f"--------------------------\n"
            f"*Itens:*\n{resumo}{brinde_txt}\n\n"
            f"*Pagamento:* {pag_cli}{info_troco}\n"
            f"*TOTAL: R$ {valor_total:.2f}*"
        )
        
        link = f"https://wa.me/5537991031933?text={urllib.parse.quote(msg)}"
        st.markdown(f'<a href="{link}" target="_blank" class="btn-whats">🚀 CLIQUE AQUI PARA ENVIAR</a>', unsafe_allow_html=True)
