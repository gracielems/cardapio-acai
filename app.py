import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse

# --- ⚙️ 1. GERENCIADOR DE PREÇOS (Facilita sua cotação futura) ---
PRECOS_COMBOS = {
    "🍫 Laka Oreo (500ml)": 28.00,
    "🍓 Clássico Morango (500ml)": 27.00,
    "⭐ Nutella Premium (500ml)": 34.00
}

PRECOS_GARRAFAS = {
    "🥤 Açaí Tradicional": 10.00,
    "🥤 Açaí com Leite em Pó": 13.00,
    "🥤 Açaí com Creme de Morango": 13.00,
    "🥤 Açaí com Creme de Maracujá": 13.00
}

PRECOS_COPOS = {"300ml": 13.0, "500ml": 18.0, "700ml": 23.0, "1 Litro": 32.0}
VALOR_ADICIONAL = 3.00
SENHA_DONO = "jubileu123"  # <--- Altere sua senha aqui!

# --- 📁 2. BANCOS DE DADOS LOCAIS ---
ARQUIVO_FIDELIDADE = "database_fidelidade.csv"
ARQUIVO_VENDAS = "historico_vendas.csv"
LINK_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQA1CUqaVNElv3-c_Ylb1XKH3_z1h5h1dbH66HkKRIafoh6lheQ5z-MY6oKMSkkqGnsxUXryigtPm3N/pub?output=csv"

# --- 🛠️ 3. FUNÇÕES DE SISTEMA ---
def registrar_venda(nome, total, itens):
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    nova_venda = pd.DataFrame({'Data': [data_hora], 'Cliente': [nome], 'Total': [total], 'Itens': [itens]})
    if not os.path.exists(ARQUIVO_VENDAS):
        nova_venda.to_csv(ARQUIVO_VENDAS, index=False)
    else:
        nova_venda.to_csv(ARQUIVO_VENDAS, mode='a', header=False, index=False)

def carregar_pedidos(nome):
    nome = nome.strip().upper()
    if os.path.exists(ARQUIVO_FIDELIDADE):
        df = pd.read_csv(ARQUIVO_FIDELIDADE)
        res = df[df['nome'] == nome]
        return int(res.iloc[0]['pedidos']) if not res.empty else 0
    return 0

def atualizar_fidelidade(nome, brinde):
    nome = nome.strip().upper()
    df = pd.read_csv(ARQUIVO_FIDELIDADE) if os.path.exists(ARQUIVO_FIDELIDADE) else pd.DataFrame(columns=['nome', 'pedidos'])
    if nome in df['nome'].values:
        df.loc[df['nome'] == nome, 'pedidos'] = 0 if brinde else df.loc[df['nome'] == nome, 'pedidos'] + 1
    else:
        df = pd.concat([df, pd.DataFrame({'nome': [nome], 'pedidos': [1]})], ignore_index=True)
    df.to_csv(ARQUIVO_FIDELIDADE, index=False)

def check_loja():
    try:
        df = pd.read_csv(LINK_PLANILHA)
        return "SIM" in str(df.columns[0]).strip().upper()
    except: return True

# --- 🎨 4. DESIGN E INTERFACE ---
st.set_page_config(page_title="Jubileu Açaí", page_icon="🍧")
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background-color: #ffffff; }
    .secao { color: #4B0082 !important; font-weight: bold; border-bottom: 2px solid #4B0082; padding-bottom: 5px; margin-top: 20px; }
    button[data-baseweb="tab"] p { font-size: 20px !important; font-weight: bold !important; color: #4B0082 !important; }
    .btn-whats { background-color: #25D366; color: white !important; padding: 15px; text-align: center; border-radius: 10px; font-weight: bold; text-decoration: none; display: block; }
</style>
""", unsafe_allow_html=True)

# --- 🔐 5. PÁGINA DO DONO (ESCONDIDA NA LATERAL) ---
with st.sidebar:
    st.title("🛡️ Admin")
    acesso = st.text_input("Senha de Acesso:", type="password")

if acesso == SENHA_DONO:
    st.title("📊 Painel de Controle - Jubileu Açaí")
    
    if os.path.exists(ARQUIVO_VENDAS):
        df_v = pd.read_csv(ARQUIVO_VENDAS)
        col1, col2 = st.columns(2)
        col1.metric("Faturamento Total", f"R$ {df_v['Total'].sum():.2f}")
        col2.metric("Total de Pedidos", len(df_v))
        
        st.subheader("📋 Últimas Vendas")
        st.dataframe(df_v.sort_values(by='Data', ascending=False), use_container_width=True)
    else:
        st.info("Aguardando a primeira venda...")

    if os.path.exists(ARQUIVO_FIDELIDADE):
        st.subheader("👥 Ranking de Clientes")
        st.dataframe(pd.read_csv(ARQUIVO_FIDELIDADE), use_container_width=True)
    
    if st.button("Voltar ao Cardápio"): st.rerun()
    st.stop() # Bloqueia o restante para não mostrar o cardápio ao dono

# --- 🍧 6. INTERFACE DO CLIENTE ---
if os.path.exists("logo3d.png"): st.image("logo3d.png", use_container_width=True)

itens_pedido = []; total = 0.0
tab1, tab2, tab3 = st.tabs(["🔥 Combos", "🥤 Na Garrafa", "🍧 Monte o Seu"])

with tab1:
    for n, p in PRECOS_COMBOS.items():
        if st.checkbox(f"{n} - R$ {p:.2f}", key=f"c_{n}"):
            itens_pedido.append(n); total += p

with tab2:
    st.markdown('<div class="secao">🥤 GARRAFAS PRONTAS (300ml)</div>', unsafe_allow_html=True)
    for n, p in PRECOS_GARRAFAS.items():
        if st.checkbox(f"{n} - R$ {p:.2f}", key=f"g_{n}"):
            itens_pedido.append(n); total += p

with tab3:
    st.markdown('<div class="secao">1. TAMANHO</div>', unsafe_allow_html=True)
    esc = st.selectbox("Copo:", list(PRECOS_COPOS.keys()), index=None, placeholder="Selecione o tamanho...")
    if esc:
        total += PRECOS_COPOS[esc]; itens_pedido.append(f"Copo {esc}")
        st.markdown('<div class="secao">2. ADICIONAIS (R$ 3,00)</div>', unsafe_allow_html=True)
        extras = ["Banana", "Bis", "Leite em Pó", "Paçoca", "Nutella", "Chantilly"]
        for e in extras:
            if st.checkbox(e, key=f"e_{e}"):
                itens_pedido.append(f"Add {e}"); total += VALOR_ADICIONAL

st.markdown('<div class="secao">DADOS DO CLIENTE</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
np, sp = c1.text_input("Nome:").strip(), c2.text_input("Sobrenome:").strip()
nome_completo = f"{np} {sp}".upper().strip()

brinde = False
if np and sp:
    q = carregar_pedidos(nome_completo)
    if q == 9:
        brinde = True
        st.balloons(); st.success("🎁 PARABÉNS! Seu próximo pedido é um BRINDE!")
    else:
        st.write(f"Sua Fidelidade: **{q}/10**")
        st.progress(q/10)

st.markdown('<div class="secao">ENTREGA E PAGAMENTO</div>', unsafe_allow_html=True)
rua = st.text_input("Endereço Completo:")
pag = st.selectbox("Forma de Pagamento:", ["Pix", "Cartão", "Dinheiro"])
troco_msg = ""
if pag == "Dinheiro":
    if st.radio("Precisa de troco?", ["Não", "Sim"]) == "Sim":
        v = st.text_input("Troco para quanto?")
        troco_msg = f"\n*Troco:* Para R$ {v}"

if st.button("✅ FINALIZAR PEDIDO"):
    if not check_loja(): st.error("LOJA FECHADA!")
    elif total == 0: st.warning("Carrinho vazio!")
    elif not (np and rua): st.warning("Preencha nome e endereço!")
    else:
        atualizar_fidelidade(nome_completo, brinde)
        registrar_venda(nome_completo, total, ", ".join(itens_pedido))
        
        msg = (f"*PEDIDO JUBILEU AÇAÍ*\n"
               f"------------------\n"
               f"*Cliente:* {nome_completo}\n"
               f"*Endereço:* {rua}\n"
               f"------------------\n"
               f"*Itens:* {', '.join(itens_pedido)}\n"
               f"{'🎁 *BRINDE RESGATADO!*' if brinde else ''}\n"
               f"*Pagamento:* {pag}{troco_msg}\n"
               f"*TOTAL: R$ {total:.2f}*")
        
        link = f"https://wa.me/5537991031933?text={urllib.parse.quote(msg)}"
        st.markdown(f'<a href="{link}" target="_blank" class="btn-whats">🚀 ENVIAR PARA O WHATSAPP</a>', unsafe_allow_html=True)
