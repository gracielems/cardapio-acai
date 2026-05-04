import streamlit as st
import urllib.parse
import pandas as pd
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

# --- CONEXÃO COM A PLANILHA (CONTROLE DE HORÁRIO) ---
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
    .stButton>button { 
        width: 100%; background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        color: white !important; border-radius: 15px; font-weight: bold; height: 3.5em; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TOPO (IMAGEM LOGO COM BUSCA AMPLIADA) ---
logo_encontrada = False
# Lista de possíveis nomes que você usou
nomes_logo = ["logo3d.jpg.png", "logo3d.png", "logo3d.jpg", "logo3d.jpeg"]

for nome_arquivo in nomes_logo:
    if os.path.exists(nome_arquivo):
        st.image(nome_arquivo, use_container_width=True)
        logo_encontrada = True
        break

if not logo_encontrada:
    st.title("🍧 Jubileu Açaí")

# --- ESTADO DO PEDIDO ---
itens_pedido = []
valor_total = 0.0

# --- ABAS ---
tab1, tab2 = st.tabs(["🔥 Combos Prontos", "Monte o Seu"])

with tab1:
    st.markdown("### Escolha um de nossos favoritos:")
    combos = {
        "🍫 Laka Oreo (500ml)": {"preco": 28.00, "desc": "Capa de Laka Oreo, Oreo crocante e leite em pó."},
        "🍓 Clássico Morango (500ml)": {"preco": 27.00, "desc": "Morangos, leite em pó e leite condensado."},
        "⭐ Nutella Premium (500ml)": {"preco": 34.00, "desc": "Nutella original, morangos e leite Ninho."}
    }
    for nome, info in combos.items():
        if st.checkbox(f"{nome} - R$ {info['preco']:.2f}", key=f"c_{nome}"):
            itens_pedido.append(f"Combo: {nome}")
            valor_total += info['preco']
        st.caption(info['desc'])
        st.markdown("---")

with tab2:
    # Imagem do "Monte o Seu"
    if os.path.exists("download (1).jpg"):
        col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
        with col_img2:
            st.image("download (1).jpg", width=180)
    
    st.markdown('<div style="text-align: center; color: #4B0082; font-weight: bold; font-size: 22px;">🍧 Monte o Seu</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="secao">1. ESCOLHA O TAMANHO</div>', unsafe_allow_html=True)
    tamanhos = {"300ml": 13.00, "500ml": 18.00, "700ml": 23.00, "1 Litro": 32.00}
    
    escolha = st.selectbox("Selecione o copo:", options=list(tamanhos.keys()), index=None, placeholder="Clique para escolher...")
    
    if escolha:
        valor_total += tamanhos[escolha]
        itens_pedido.append(f"Copo {escolha}")

        st.markdown('<div class="secao">2. ADICIONAIS (R$ 3,00 cada)</div>', unsafe_allow_html=True)
        extras = ["Banana", "Bis Branco", "Bis Preto", "Leite em Pó", "Paçoca", "Amendoim", "Granola", "Coco Ralado", "Gotas de Chocolate", "Oreo", "Disquete", "Chocoboll", "Leite Condensado", "Cobertura Chocolate", "Cobertura Morango", "Chantilly"]
        
        c1, c2 = st.columns(2)
        for i, item in enumerate(extras):
            col = c1 if i % 2 == 0 else c2
            if col.checkbox(item, key=f"add_{item}"):
                itens_pedido.append(f"Add: {item}")
                valor_total += 3.00

# --- EXIBIÇÃO DO TOTAL EM TEMPO REAL ---
if valor_total > 0:
    st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 15px; border: 1px solid #4B0082; margin-top: 20px; margin-bottom: 20px;">
            <h4 style="margin: 0; color: #4B0082;">🛒 Resumo do Pedido</h4>
            <p style="margin: 5px 0; font-size: 14px;">{', '.join(itens_pedido)}</p>
            <h3 style="margin: 0; color: #25D366;">Total: R$ {valor_total:.2f}</h3>
        </div>
    """, unsafe_allow_html=True)

# --- FINALIZAÇÃO E FIDELIDADE ---
st.markdown('<div class="secao">DADOS DO CLIENTE</div>', unsafe_allow_html=True)
nome_cli = st.text_input("Seu Nome:")

ganhou_brinde = False
if nome_cli:
    qtd = carregar_dados_cliente(nome_cli)
    if qtd == 9:
        ganhou_brinde = True
        st.markdown(f"""
            <div style="background-color: #f3e5f5; border-left: 5px solid #4B0082; padding: 20px; border-radius: 15px; margin-bottom: 20px;">
                <h3 style="color: #4B0082; margin-top: 0;">🎁 PARABÉNS, {nome_cli.upper()}! 🥳</h3>
                <p style="color: #333; font-size: 16px;"><i>"Para nós, você é visto, é querido e sempre lembrado."</i><br><br>
                Este é seu 10º pedido! <b>Você ganhou um Açaí de 300ml de brinde!</b></p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"Olá {nome_cli}! Faltam {9 - qtd} pedidos para seu brinde especial! 💜")

end_cli = st.text_input("Endereço de Entrega:")
pag_cli = st.selectbox("Forma de Pagamento:", ["Pix", "Cartão", "Dinheiro"])

# --- BOTÃO FINAL ---
if st.button("✅ FINALIZAR E ENVIAR PEDIDO"):
    if not LOJA_ABERTA:
        st.error("❌ A LOJA ESTÁ FECHADA AGORA!")
    elif valor_total == 0:
        st.warning("Seu carrinho está vazio!")
    elif not nome_cli or not end_cli:
        st.warning("Preencha nome e endereço!")
    else:
        atualizar_pedido_cliente(nome_cli, ganhou_brinde)
        resumo = "\n".join(itens_pedido)
        brinde_texto = "\n\n🎁 *BRINDE: 1 AÇAÍ 300ML RESGATADO!*" if ganhou_brinde else ""
        
        msg = (
            f"🍧 *NOVO PEDIDO JUBILEU AÇAÍ*\n"
            f"--------------------------\n"
            f"*Cliente:* {nome_cli}\n"
            f"*Endereço:* {end_cli}\n"
            f"--------------------------\n"
            f"*Itens:*\n{resumo}{brinde_texto}\n\n"
            f"*Pagamento:* {pag_cli}\n"
            f"*TOTAL: R$ {valor_total:.2f}*"
        )
        
        link = f"https://wa.me/5537991031933?text={urllib.parse.quote(msg)}"
        st.markdown(f'<meta http-equiv="refresh" content="0;URL={link}">', unsafe_allow_html=True)
        st.success("Pedido enviado! Abrindo WhatsApp...")
