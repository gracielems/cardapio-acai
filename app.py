import streamlit as st
import urllib.parse
import pd as pd
import os

# --- ARQUIVO DE BANCO DE DADOS LOCAL (FIDELIDADE) ---
ARQUIVO_CLIENTES = "database_fidelidade.csv"

def carregar_dados_cliente(nome):
    nome = nome.strip().upper()
    if os.path.exists(ARQUIVO_CLIENTES):
        df = pd.read_csv(ARQUIVO_CLIENTES)
        cliente = df[df['nome'] == nome]
        if not cliente.empty:
            return int(cliente.iloc[0]['pedidos'])
    return 0

def atualizar_pedido_cliente(nome, ganhou_brinde):
    nome = nome.strip().upper()
    if os.path.exists(ARQUIVO_CLIENTES):
        df = pd.read_csv(ARQUIVO_CLIENTES)
    else:
        df = pd.DataFrame(columns=['nome', 'pedidos'])

    if nome in df['nome'].values:
        if ganhou_brinde:
            df.loc[df['nome'] == nome, 'pedidos'] = 0
        else:
            df.loc[df['nome'] == nome, 'pedidos'] += 1
    else:
        nova_linha = pd.DataFrame({'nome': [nome], 'pedidos': [1]})
        df = pd.concat([df, nova_linha], ignore_index=True)
    
    df.to_csv(ARQUIVO_CLIENTES, index=False)

# --- CONEXÃO COM A PLANILHA (HORÁRIO) ---
LINK_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQA1CUqaVNElv3-c_Ylb1XKH3_z1h5h1dbH66HkKRIafoh6lheQ5z-MY6oKMSkkqGnsxUXryigtPm3N/pub?output=csv"

def verificar_loja_aberta():
    try:
        df = pd.read_csv(LINK_PLANILHA)
        status = str(df.columns[0]).strip().upper()
        return "SIM" in status
    except:
        return True

LOJA_ABERTA = verificar_loja_aberta()

# --- CONFIGURAÇÃO DE DESIGN ---
st.set_page_config(page_title="Jubileu Açaí", page_icon="🍧")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .secao { color: #4B0082; font-weight: bold; border-bottom: 2px solid #4B0082; padding-bottom: 5px; margin-top: 30px; margin-bottom: 15px; }
    .valor-total { 
        position: fixed; bottom: 20px; right: 20px; background-color: #4B0082; 
        color: white; padding: 15px; border-radius: 50px; font-weight: bold; 
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3); z-index: 1000;
    }
    .stButton>button { 
        width: 100%; background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        color: white !important; border-radius: 15px; font-weight: bold; height: 3.5em; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO ---
if os.path.exists("logo3d.png"):
    st.image("logo3d.png", use_container_width=True)
else:
    st.title("🍧 Jubileu Açaí")

# --- INICIALIZAÇÃO DE VARIÁVEIS DE PEDIDO ---
itens_pedido = []
valor_total = 0.0

tab1, tab2 = st.tabs(["🔥 Combos Prontos", "Monte o Seu"])

with tab1:
    st.markdown("### Nossos Favoritos")
    combos = {
        "🍫 Laka Oreo (500ml)": {"preco": 28.0, "desc": "Capa de Laka Oreo, Oreo crocante e leite em pó."},
        "🍓 Clássico Morango (500ml)": {"preco": 27.0, "desc": "Morangos, leite em pó e leite condensado."},
        "⭐ Nutella Premium (500ml)": {"preco": 34.0, "desc": "Nutella original, morangos e leite Ninho."}
    }
    for nome, info in combos.items():
        if st.checkbox(f"{nome} - R$ {info['preco']:.2f}", key=f"c_{nome}"):
            itens_pedido.append(f"Combo: {nome}")
            valor_total += info['preco']
        st.caption(info['desc'])
        st.markdown("---")

with tab2:
    st.markdown('<div class="secao">1. TAMANHO</div>', unsafe_allow_html=True)
    tamanhos = {"300ml": 13.0, "500ml": 18.0, "700ml": 23.0, "1 Litro": 32.0}
    escolha = st.selectbox("Escolha seu copo:", options=list(tamanhos.keys()), index=None, placeholder="Clique aqui...")
    
    if escolha:
        valor_total += tamanhos[escolha]
        itens_pedido.append(f"Copo {escolha}")

        st.markdown('<div class="secao">2. ADICIONAIS (R$ 3,00 cada)</div>', unsafe_allow_html=True)
        extras = ["Banana", "Bis", "Leite em Pó", "Paçoca", "Granola", "Oreo", "Leite Condensado", "Nutella", "M&Ms"]
        
        c1, c2 = st.columns(2)
        for i, item in enumerate(extras):
            col = c1 if i % 2 == 0 else c2
            if col.checkbox(item, key=f"add_{item}"):
                itens_pedido.append(f"Add: {item}")
                valor_total += 3.0

# --- EXIBIÇÃO DO TOTAL EM TEMPO REAL ---
if valor_total > 0:
    st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #4B0082; margin-top: 20px;">
            <h4 style="margin: 0; color: #4B0082;">🛒 Resumo do Pedido</h4>
            <p style="margin: 5px 0;">{", ".join(itens_pedido)}</p>
            <h3 style="margin: 0; color: #25D366;">Total: R$ {valor_total:.2f}</h3>
        </div>
    """, unsafe_allow_html=True)

# --- FINALIZAÇÃO E FIDELIDADE ---
st.markdown('<div class="secao">DADOS DE ENTREGA</div>', unsafe_allow_html=True)
nome_cli = st.text_input("Seu Nome:")

ganhou_brinde = False
if nome_cli:
    qtd = carregar_dados_cliente(nome_cli)
    if qtd == 9:
        ganhou_brinde = True
        st.markdown(f"""
            <div style="background-color: #f3e5f5; border-left: 5px solid #4B0082; padding: 15px; border-radius: 10px;">
                <p><b>🎁 PARABÉNS, {nome_cli.upper()}!</b><br>
                "Você é visto e sempre lembrado." Por ser seu 10º pedido, <b>ganhou um Açaí 300ml de brinde!</b></p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"Faltam {9-qtd} pedidos para seu brinde! 💜")

end_cli = st.text_input("Endereço:")
pag_cli = st.selectbox("Pagamento:", ["Pix", "Cartão", "Dinheiro"])

if st.button("✅ FINALIZAR NO WHATSAPP"):
    if not LOJA_ABERTA:
        st.error("Loja Fechada!")
    elif valor_total == 0 or not nome_cli or not end_cli:
        st.warning("Preencha tudo!")
    else:
        atualizar_pedido_cliente(nome_cli, ganhou_brinde)
        resumo = "\n".join(itens_pedido)
        brinde_msg = "\n🎁 *BRINDE RESGATADO!*" if ganhou_brinde else ""
        msg = f"🍧 *PEDIDO JUBILEU*\n\n*Cliente:* {nome_cli}\n*Itens:*\n{resumo}{brinde_msg}\n\n*TOTAL: R$ {valor_total:.2f}*"
        link = f"https://wa.me/5537991031933?text={urllib.parse.quote(msg)}"
        st.markdown(f'<meta http-equiv="refresh" content="0;URL={link}">', unsafe_allow_html=True)
