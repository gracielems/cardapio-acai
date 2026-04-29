import streamlit as st
import urllib.parse
import pandas as pd

# =========================================================
# 🎮 CONTROLE REMOTO VIA GOOGLE SHEETS
# =========================================================
LINK_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQA1CUqaVNElv3-c_Ylb1XKH3_z1h5h1dbH66HkKRIafoh6lheQ5z-MY6oKMSkkqGnsxUXryigtPm3N/pub?output=csv"

def verificar_loja_aberta():
    try:
        # Lê a planilha e verifica se a primeira célula é SIM ou NÃO
        df = pd.read_csv(LINK_PLANILHA)
        # Verifica o conteúdo da primeira célula (coluna 0, linha 0)
        status = str(df.columns[0]).strip().upper()
        return True if "SIM" in status else False
    except Exception:
        # Se houver erro na leitura, mantém aberta por segurança
        return True

LOJA_ABERTA = verificar_loja_aberta()

# =========================================================
# 🎨 CONFIGURAÇÕES VISUAIS E CSS
# =========================================================
st.set_page_config(page_title="Jubilu Açaí - Delivery", page_icon="🍧", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #31333F; }
    
    .banner {
        background: linear-gradient(90deg, #4B0082 0%, #8A2BE2 100%);
        padding: 30px; border-radius: 0px 0px 30px 30px;
        color: white !important; text-align: center; margin: -60px -20px 20px -20px;
    }
    
    .status-badge {
        padding: 8px 20px; border-radius: 20px; font-weight: bold; font-size: 14px;
        display: inline-block; margin-bottom: 20px;
    }

    .fidelidade-card {
        background-color: #f0e6ff; padding: 15px; border-radius: 15px;
        border: 2px dashed #4B0082; text-align: center; margin-bottom: 20px;
    }

    .section-header { 
        color: #4B0082 !important; font-size: 20px; font-weight: bold;
        border-bottom: 2px solid #4B0082; margin-top: 25px; margin-bottom: 15px;
    }

    /* Estilo dos cards de produtos */
    .produto-card {
        background-color: #f8f9fa; padding: 15px; border-radius: 12px;
        border: 1px solid #eee; margin-bottom: 10px; transition: 0.3s;
    }
    
    .tag-popular {
        background-color: #FFD700; color: #000; padding: 2px 8px;
        border-radius: 5px; font-size: 11px; font-weight: bold;
    }

    .stButton>button { 
        width: 100%; background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        color: white !important; border-radius: 15px; font-weight: bold; 
        height: 3.8em; border: none; font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
st.markdown("""
    <div class="banner">
        <h1 style="color: white !important; margin:0;">🍧 Jubilu Delivery</h1>
        <p style="color: white !important; opacity: 0.9;">O melhor açaí de Nova Serrana!</p>
    </div>
    """, unsafe_allow_html=True)

# --- STATUS DA LOJA (LIDO DA PLANILHA) ---
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
if LOJA_ABERTA:
    st.markdown('<span class="status-badge" style="background:#d4edda; color:#155724;">● ABERTO AGORA</span>', unsafe_allow_html=True)
else:
    st.markdown('<span class="status-badge" style="background:#f8d7da; color:#721c24;">● FECHADO NO MOMENTO</span>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- SISTEMA DE FIDELIDADE E CADASTRO (MEMÓRIA) ---
if 'historico_pedidos' not in st.session_state: st.session_state.historico_pedidos = 0
if 'nome_cli' not in st.session_state: st.session_state.nome_cli = ""
if 'end_cli' not in st.session_state: st.session_state.end_cli = ""

st.markdown('<div class="section-header">🎁 SEU CARTÃO FIDELIDADE</div>', unsafe_allow_html=True)
progresso = st.session_state.historico_pedidos % 10
st.markdown(f"""
    <div class="fidelidade-card">
        <b>Olá! Este é seu pedido nº {st.session_state.historico_pedidos + 1}</b><br>
        Complete 10 pedidos e ganhe um brinde especial! 🥳
    </div>
    """, unsafe_allow_html=True)
st.progress(progresso / 10)

# --- SELEÇÃO DE COMBOS ---
st.markdown('<div class="section-header">🔥 ESCOLHA SEU AÇAÍ</div>', unsafe_allow_html=True)

menu = {
    "🍫 Laka Oreo (500ml)": {"preco": 28.00, "popular": True, "desc": "Capa de Laka Oreo, Oreo crocante e leite em pó."},
    "🍓 Clássico Morango (500ml)": {"preco": 27.00, "popular": False, "desc": "Morangos, leite em pó e leite condensado."},
    "⭐ Nutella Premium (500ml)": {"preco": 34.00, "popular": True, "desc": "Nutella original, morangos e leite Ninho."}
}

itens_selecionados = []
for nome, info in menu.items():
    with st.container():
        # Criando o card visual
        tag = '<span class="tag-popular">🔥 MAIS PEDIDO</span>' if info['popular'] else ""
        st.markdown(f"""
            <div class="produto-card">
                <div style="display: flex; justify-content: space-between;">
                    <b>{nome}</b>
                    {tag}
                </div>
                <small>{info['desc']}</small><br>
                <b style="color: #4B0082;">R$ {info['preco']:.2f}</b>
            </div>
        """, unsafe_allow_html=True)
        
        # Botão de seleção logo abaixo do card
        if st.checkbox(f"Selecionar {nome}", key=nome):
            itens_selecionados.append((nome, info['preco']))

# --- SUGESTÃO DE VENDA (UPSELL) ---
st.markdown('<div class="section-header">🤤 DESEJA ADICIONAR?</div>', unsafe_allow_html=True)
add_nutella = st.checkbox("🍫 Adicionar Nutella Extra por apenas +R$ 6,00?")

# --- DADOS DE ENTREGA ---
st.markdown('<div class="section-header">📍 ONDE ENTREGAMOS?</div>', unsafe_allow_html=True)

nome_cliente = st.text_input("Seu Nome:", value=st.session_state.nome_cli)
endereco_cliente = st.text_area("Seu Endereço Completo:", value=st.session_state.end_cli)
pagamento = st.selectbox("Forma de Pagamento:", ["Pix", "Cartão", "Dinheiro (Troco na msg)"])

# Salva na memória do navegador para a próxima vez
st.session_state.nome_cli = nome_cliente
st.session_state.end_cli = endereco_cliente

st.success("🚚 **Frete Grátis** para toda Nova Serrana!")

# --- CÁLCULO FINAL ---
valor_total = sum(p for n, p in itens_selecionados)
if add_nutella: valor_total += 6.00

st.markdown(f"""
    <div style="background-color: #4B0082; padding: 20px; border-radius: 15px; text-align: center; margin-top: 20px;">
        <h2 style="margin:0; color: #25D366 !important;">Total: R$ {valor_total:.2f}</h2>
    </div>
    <br>
""", unsafe_allow_html=True)

# --- FINALIZAÇÃO ---
if st.button("🚀 ENVIAR PEDIDO PARA O WHATSAPP"):
    if not LOJA_ABERTA:
        st.error("❌ A loja está fechada agora! Por favor, tente novamente mais tarde.")
    elif valor_total == 0:
        st.warning("🛒 Seu carrinho está vazio!")
    elif not nome_cliente or not endereco_cliente:
        st.error("⚠️ Preencha seu nome e endereço!")
    else:
        # Incrementa contador de fidelidade
        st.session_state.historico_pedidos += 1
        
        resumo_pedido = ""
        for n, p in itens_selecionados: resumo_pedido += f"• {n}\n"
        if add_nutella: resumo_pedido += "• ADICIONAL: Nutella Extra\n"
        
        msg_whatsapp = (
            f"🍧 *JUBILU AÇAÍ - PEDIDO #{st.session_state.historico_pedidos}*\n\n"
            f"👤 *Cliente:* {nome_cliente}\n"
            f"📍 *Endereço:* {endereco_cliente}\n"
            f"💳 *Pagamento:* {pagamento}\n"
            f"---------------------------\n"
            f"{resumo_pedido}"
            f"---------------------------\n"
            f"💰 *TOTAL: R$ {valor_total:.2f}*"
        )
        
        # Gera o link para o seu WhatsApp
        link_zap = f"https://wa.me/5537991031933?text={urllib.parse.quote(msg_whatsapp)}"
        st.markdown(f'<meta http-equiv="refresh" content="0;URL={link_zap}">', unsafe_allow_html=True)
