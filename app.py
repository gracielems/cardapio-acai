import streamlit as st
import urllib.parse
import pandas as pd
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Jubileu Açaí", page_icon="🍧")

# --- LIMPEZA TOTAL DA INTERFACE (REMOVE FORK, MENU E RODAPÉ) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    [data-testid="stToolbar"] {display: none;}
    .stApp { background-color: #ffffff; }
    .secao { color: #4B0082; font-weight: bold; border-bottom: 2px solid #4B0082; padding-bottom: 5px; margin-top: 30px; margin-bottom: 15px; }
    .btn-whats {
        display: inline-block; padding: 15px 25px; background-color: #25D366; color: white !important;
        text-align: center; text-decoration: none; font-size: 18px; font-weight: bold;
        border-radius: 15px; width: 100%; border: none; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS FIDELIDADE ---
ARQUIVO_CLIENTES = "database_fidelidade.csv"

def carregar_dados_cliente(nome):
    nome = nome.strip().upper()
    if os.path.exists(ARQUIVO_CLIENTES):
        df = pd.read_csv(ARQUIVO_CLIENTES)
        cliente = df[df['nome'] == nome]
        if not cliente.empty: return int(cliente.iloc[0]['pedidos'])
    return 0

def atualizar_pedido_cliente(nome, ganhou_brinde):
    nome = nome.strip().upper()
    df = pd.read_csv(ARQUIVO_CLIENTES) if os.path.exists(ARQUIVO_CLIENTES) else pd.DataFrame(columns=['nome', 'pedidos'])
    if nome in df['nome'].values:
        df.loc[df['nome'] == nome, 'pedidos'] = 0 if ganhou_brinde else df.loc[df['nome'] == nome, 'pedidos'] + 1
    else:
        df = pd.concat([df, pd.DataFrame({'nome': [nome], 'pedidos': [1]})], ignore_index=True)
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

# --- PEDIDO ---
itens_pedido = []
valor_total = 0.0

tab1, tab2 = st.tabs(["🔥 Combos", "Monte o Seu"])

with tab1:
    combos = {
        "🍫 Laka Oreo (500ml)": 28.00,
        "🍓 Clássico Morango (500ml)": 27.00,
        "⭐ Nutella Premium (500ml)": 34.00
    }
    for nome, preco in combos.items():
        if st.checkbox(f"{nome} - R$ {preco:.2f}"):
            itens_pedido.append(nome); valor_total += preco

with tab2:
    st.markdown('<div class="secao">1. TAMANHO</div>', unsafe_allow_html=True)
    tamanhos = {"300ml": 13.0, "500ml": 18.0, "700ml": 23.0, "1 Litro": 32.0}
    esc = st.selectbox("Copo:", list(tamanhos.keys()), index=None)
    if esc:
        valor_total += tamanhos[esc]; itens_pedido.append(f"Copo {esc}")
        st.markdown('<div class="secao">2. ADICIONAIS (R$ 3,00)</div>', unsafe_allow_html=True)
        extras = ["Banana", "Bis", "Leite em Pó", "Paçoca", "Nutella", "Chantilly"]
        for item in extras:
            if st.checkbox(item): itens_pedido.append(f"Add {item}"); valor_total += 3.0

# --- RESUMO E FINALIZAÇÃO ---
if valor_total > 0:
    st.success(f"### Total: R$ {valor_total:.2f}")

st.markdown('<div class="secao">DADOS DO CLIENTE</div>', unsafe_allow_html=True)
nome_cli = st.text_input("Seu Nome:")
ganhou_brinde = False
if nome_cli:
    qtd = carregar_dados_cliente(nome_cli)
    if qtd == 9:
        ganhou_brinde = True
        st.balloons()
        st.info("🎁 Você ganhou um Brinde de 300ml!")
    else: st.write(f"Faltam {9-qtd} pedidos para seu brinde! 💜")

end_cli = st.text_input("Endereço:")
pag_cli = st.selectbox("Pagamento:", ["Pix", "Cartão", "Dinheiro"])

if st.button("✅ GERAR PEDIDO PARA O WHATSAPP"):
    if not LOJA_ABERTA: st.error("LOJA FECHADA!")
    elif valor_total == 0 or not nome_cli or not end_cli: st.warning("Preencha tudo!")
    else:
        atualizar_pedido_cliente(nome_cli, ganhou_brinde)
        resumo = "\n".join(itens_pedido)
        msg = f"*PEDIDO JUBILEU*\n\n*Cliente:* {nome_cli}\n*Itens:*\n{resumo}\n\n*TOTAL: R$ {valor_total:.2f}*"
        link = f"https://wa.me/5537991031933?text={urllib.parse.quote(msg)}"
        st.markdown(f'<a href="{link}" target="_blank" class="btn-whats">🚀 ENVIAR AGORA</a>', unsafe_allow_html=True)
