import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse

# --- ⚙️ 1. GERENCIADOR DE PREÇOS (Atualize aqui conforme seus fornecedores) ---
PRECOS_COMBOS = {"🍫 Laka Oreo (500ml)": 28.00, "🍓 Clássico Morango (500ml)": 27.00, "⭐ Nutella Premium (500ml)": 34.00}
PRECOS_GARRAFAS = {"🥤 Tradicional": 10.00, "🥤 Leite em Pó": 13.00, "🥤 Morango": 13.00, "🥤 Maracujá": 13.00}
PRECOS_COPOS = {"300ml": 13.0, "500ml": 18.0, "700ml": 23.0, "1 Litro": 32.0}
VALOR_ADICIONAL = 3.00
SENHA_DONO = "jubileu123" 

# --- 📁 2. BANCOS DE DADOS ---
ARQUIVO_FIDELIDADE = "database_fidelidade.csv"
ARQUIVO_VENDAS = "historico_vendas.csv"
LINK_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQA1CUqaVNElv3-c_Ylb1XKH3_z1h5h1dbH66HkKRIafoh6lheQ5z-MY6oKMSkkqGnsxUXryigtPm3N/pub?output=csv"

# --- 🛠️ 3. FUNÇÕES ---
def registrar_venda(nome, total, itens):
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    nova_venda = pd.DataFrame({'Data': [data_hoje], 'Cliente': [nome], 'Total': [total], 'Itens': [itens]})
    if not os.path.exists(ARQUIVO_VENDAS): nova_venda.to_csv(ARQUIVO_VENDAS, index=False)
    else: nova_venda.to_csv(ARQUIVO_VENDAS, mode='a', header=False, index=False)

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

# --- 🎨 4. DESIGN ---
st.set_page_config(page_title="Jubileu Açaí", page_icon="🍧")
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #ffffff; }
    .secao { color: #4B0082 !important; font-weight: bold; border-bottom: 2px solid #4B0082; padding-bottom: 5px; margin-top: 20px; }
    button[data-baseweb="tab"] p { font-size: 19px !important; font-weight: bold !important; color: #4B0082 !important; }
    .btn-whats { background-color: #25D366; color: white !important; padding: 15px; text-align: center; border-radius: 10px; font-weight: bold; text-decoration: none; display: block; margin-top: 10px; }
    .check-out { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #dee2e6; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

if "admin_logado" not in st.session_state: st.session_state.admin_logado = False

# --- 🍧 5. CARDÁPIO (CLIENTE) ---
if not st.session_state.admin_logado:
    if os.path.exists("logo3d.png"): st.image("logo3d.png", use_container_width=True)

    itens_pedido = []; total_final = 0.0
    tab1, tab2, tab3 = st.tabs(["🔥 Combos", "🥤 Na Garrafa", "🍧 Monte o Seu"])

    with tab1:
        for n, p in PRECOS_COMBOS.items():
            if st.checkbox(f"{n} - R$ {p:.2f}", key=f"c_{n}"):
                itens_pedido.append(n); total_final += p
    with tab2:
        st.markdown('<div class="secao">🥤 GARRAFAS PRONTAS</div>', unsafe_allow_html=True)
        for n, p in PRECOS_GARRAFAS.items():
            if st.checkbox(f"{n} - R$ {p:.2f}", key=f"g_{n}"):
                itens_pedido.append(n); total_final += p
    with tab3:
        st.markdown('<div class="secao">1. TAMANHO</div>', unsafe_allow_html=True)
        esc = st.selectbox("Copo:", list(PRECOS_COPOS.keys()), index=None, placeholder="Selecione o tamanho...")
        if esc:
            total_final += PRECOS_COPOS[esc]; itens_pedido.append(f"Copo {esc}")
            st.markdown('<div class="secao">2. ADICIONAIS</div>', unsafe_allow_html=True)
            for e in ["Banana", "Bis", "Leite em Pó", "Paçoca", "Nutella", "Chantilly"]:
                if st.checkbox(e, key=f"e_{e}"):
                    itens_pedido.append(f"Add {e}"); total_final += VALOR_ADICIONAL

    st.markdown('<div class="secao">DADOS DO PEDIDO</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    np = c1.text_input("Nome:").strip()
    sp = c2.text_input("Sobrenome:").strip()
    nome_completo = f"{np} {sp}".upper().strip()

    brinde_ativo = False
    if np and sp:
        q = carregar_pedidos(nome_completo)
        if q == 9:
            st.success("🎁 PARABÉNS! Seu pedido hoje é um BRINDE!"); brinde_ativo = True; total_final = 0.0
        else:
            st.write(f"Fidelidade: **{q}/10**"); st.progress(q/10)

    rua = st.text_input("Endereço Completo (Rua, Nº, Bairro):")
    pag = st.selectbox("Pagamento:", ["Pix", "Cartão", "Dinheiro"])
    troco = ""
    if pag == "Dinheiro":
        t_op = st.radio("Precisa de troco?", ["Não", "Sim"], horizontal=True)
        if t_op == "Sim": troco = f" (Troco para {st.text_input('Valor para troco:')})"

    # --- 🛒 CONFIRMAÇÃO DE ITENS (CHECK-OUT) ---
    if total_final > 0 or brinde_ativo:
        st.markdown('<div class="check-out">', unsafe_allow_html=True)
        st.subheader("📋 Resumo do Pedido")
        for item in itens_pedido:
            st.write(f"• {item}")
        st.write(f"**Total a Pagar: R$ {total_final:.2f}**")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("✅ FINALIZAR E ENVIAR"):
            if not (np and rua): st.warning("Preencha seu nome e endereço!")
            else:
                registrar_venda(nome_completo, total_final, ", ".join(itens_pedido))
                atualizar_fidelidade(nome_completo, brinde_ativo)
                msg = (f"*PEDIDO JUBILEU*\n*Cliente:* {nome_completo}\n*Endereço:* {rua}\n*Itens:* {', '.join(itens_pedido)}\n*Pagamento:* {pag}{troco}\n*TOTAL:* R$ {total_final:.2f}")
                st.markdown(f'<a href="https://wa.me/5537991031933?text={urllib.parse.quote(msg)}" target="_blank" class="btn-whats">🚀 CLIQUE AQUI PARA ENVIAR WHATSAPP</a>', unsafe_allow_html=True)

    st.markdown('<p style="color:#eee; font-size:10px; text-align:center; margin-top:50px;">v1.2</p>', unsafe_allow_html=True)
    if st.button("Admin", help="Acesso restrito"):
        st.session_state.admin_logado = "solicitar_senha"; st.rerun()

# --- 🔐 6. PAINEL DO DONO ---
if st.session_state.admin_logado == "solicitar_senha":
    senha = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        if senha == SENHA_DONO: st.session_state.admin_logado = True; st.rerun()
        else: st.error("Senha incorreta")
    if st.button("Sair"): st.session_state.admin_logado = False; st.rerun()

if st.session_state.admin_logado is True:
    st.title("📊 Painel de Gestão")
    if st.button("⬅️ Sair"): st.session_state.admin_logado = False; st.rerun()

    if os.path.exists(ARQUIVO_VENDAS):
        df_v = pd.read_csv(ARQUIVO_VENDAS)
        
        # Métrica Geral
        c1, c2 = st.columns(2)
        c1.metric("Faturamento Total", f"R$ {df_v['Total'].sum():.2f}")
        c2.metric("Nº de Pedidos", len(df_v))

        # Gráfico 1: Faturamento Diário
        st.subheader("📈 Faturamento por Dia")
        fat_diario = df_v.groupby('Data')['Total'].sum()
        st.bar_chart(fat_diario)

        # Gráfico 2: Produtos mais vendidos
        st.subheader("🏆 Itens mais Pedidos")
        todos_itens = df_v['Itens'].str.split(', ').explode()
        st.bar_chart(todos_itens.value_counts().head(5))

        st.subheader("📋 Histórico Completo")
        st.dataframe(df_v, use_container_width=True)
    else:
        st.info("Nenhuma venda registrada ainda.")
