import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse

# --- ⚙️ 1. CONFIGURAÇÕES E BANCO DE DADOS ---
PRECOS_COMBOS = {"🍫 Laka Oreo (500ml)": 28.00, "🍓 Clássico Morango (500ml)": 27.00, "⭐ Nutella Premium (500ml)": 34.00}
PRECOS_GARRAFAS = {"🥤 Tradicional": 10.00, "🥤 Leite em Pó": 13.00, "🥤 Morango": 13.00, "🥤 Maracujá": 13.00}
PRECOS_COPOS = {"300ml": 13.0, "500ml": 18.0, "700ml": 23.0, "1 Litro": 32.0}
VALOR_ADICIONAL = 3.00
SENHA_DONO = "jubileu123"

# Imagens conforme seus arquivos
NOME_IMAGEM_LOGO = "logo3d.jpg.png"
NOME_IMAGEM_MONTE = "download (1).jpg"

ARQUIVO_FIDELIDADE = "database_fidelidade.csv"
ARQUIVO_VENDAS = "historico_vendas.csv"
ARQUIVO_STATUS = "status_loja.txt"

# --- 🛠️ 2. FUNÇÕES DE SUPORTE ---
def verificar_loja_aberta():
    if not os.path.exists(ARQUIVO_STATUS): return True
    with open(ARQUIVO_STATUS, "r") as f:
        return f.read().strip() == "ABERTA"

def alternar_loja(status):
    with open(ARQUIVO_STATUS, "w") as f:
        f.write(status)

def registrar_venda(nome, total, itens):
    data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
    nova_venda = pd.DataFrame({'Data': [data_hoje], 'Cliente': [nome], 'Total': [total], 'Itens': [itens]})
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

# --- 🎨 3. CSS E ESTILO ---
st.set_page_config(page_title="Jubileu Açaí", page_icon="🍧")
LOJA_ABERTA = verificar_loja_aberta()

st.markdown("""
<style>
    .secao { color: #4B0082 !important; font-weight: bold; border-bottom: 2px solid #4B0082; padding-bottom: 5px; margin-top: 20px; }
    .btn-whats { background: linear-gradient(90deg, #25D366 0%, #128C7E 100%); color: white !important; padding: 15px; text-align: center; border-radius: 12px; font-weight: bold; text-decoration: none; display: block; margin-top: 10px; }
    .check-out { background-color: #f9f9f9; padding: 15px; border-radius: 10px; border: 1px solid #ddd; margin-top: 15px; }
    .status-badge { padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

if "admin_logado" not in st.session_state: st.session_state.admin_logado = False

# --- 🍧 4. ÁREA DO CLIENTE ---
if not st.session_state.admin_logado:
    if os.path.exists(NOME_IMAGEM_LOGO): 
        st.image(NOME_IMAGEM_LOGO, use_container_width=True)
    
    if not LOJA_ABERTA:
        st.markdown('<div class="status-badge" style="background-color: #ffcccc; color: #cc0000;">🔴 FECHADO NO MOMENTO</div>', unsafe_allow_html=True)
        st.info("Você pode ver o cardápio, mas o botão de enviar pedido está desativado.")
    else:
        st.markdown('<div class="status-badge" style="background-color: #ccffcc; color: #006600;">🟢 ESTAMOS ABERTOS!</div>', unsafe_allow_html=True)

    itens_pedido = []; total_itens = 0.0
    tab1, tab2, tab3 = st.tabs(["🔥 Combos", "🥤 Na Garrafa", "🍧 Monte o Seu"])

    with tab1:
        for n, p in PRECOS_COMBOS.items():
            if st.checkbox(f"{n} - R$ {p:.2f}", key=f"c_{n}"):
                itens_pedido.append(n); total_itens += p
    
    with tab2:
        st.markdown('<div class="secao">GARRAFAS GELADAS</div>', unsafe_allow_html=True)
        for n, p in PRECOS_GARRAFAS.items():
            if st.checkbox(f"{n} - R$ {p:.2f}", key=f"g_{n}"):
                itens_pedido.append(n); total_itens += p
                
    with tab3:
        if os.path.exists(NOME_IMAGEM_MONTE):
            st.image(NOME_IMAGEM_MONTE, width=180)
        
        st.markdown('<div class="secao">1. TAMANHO</div>', unsafe_allow_html=True)
        esc = st.selectbox("Escolha o Copo:", list(PRECOS_COPOS.keys()), index=None, placeholder="Clique aqui...")
        if esc:
            total_itens += PRECOS_COPOS[esc]; itens_pedido.append(f"Copo {esc}")
            st.markdown('<div class="secao">2. ADICIONAIS (R$ 3,00)</div>', unsafe_allow_html=True)
            for e in ["Banana", "Morango", "Leite em Pó", "Paçoca", "Nutella", "Chantilly", "Granola", "Oreo"]:
                if st.checkbox(e, key=f"e_{e}"):
                    itens_pedido.append(f"Add {e}"); total_itens += VALOR_ADICIONAL

    st.markdown('<div class="secao">DADOS PARA ENTREGA (Frete Grátis)</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    np = c1.text_input("Nome:").strip()
    sp = c2.text_input("Sobrenome:").strip()
    nome_completo = f"{np} {sp}".upper().strip()

    brinde_ativo = False
    if np and sp:
        q = carregar_pedidos(nome_completo)
        if q >= 9:
            st.success("🎁 OBA! Você ganhou um BRINDE por sua fidelidade!"); brinde_ativo = True
        else:
            st.write(f"Seu progresso de fidelidade: **{q}/10**")
            st.progress(q/10)

    col_rua, col_num = st.columns([3, 1])
    rua = col_rua.text_input("Rua/Avenida:")
    numero = col_num.text_input("Nº:")
    bairro = st.text_input("Bairro:")
    
    st.markdown('<div class="secao">PAGAMENTO</div>', unsafe_allow_html=True)
    pag = st.selectbox("Forma de Pagamento:", ["Pix", "Cartão", "Dinheiro"])
    troco_msg = ""
    if pag == "Dinheiro":
        if st.radio("Precisa de troco?", ["Não", "Sim"], horizontal=True) == "Sim":
            v = st.text_input("Troco para quanto?")
            troco_msg = f" (Troco para {v})"

    # --- 🛒 CHECK-OUT ---
    total_final = 0.00 if brinde_ativo else total_itens

    if total_itens > 0:
        st.markdown('<div class="check-out">', unsafe_allow_html=True)
        st.subheader("📋 Resumo do Pedido")
        for item in itens_pedido: st.write(f"• {item}")
        if brinde_ativo: st.write("🎁 **DESCONTO: Brinde Aplicado!**")
        st.write(f"**TOTAL A PAGAR: R$ {total_final:.2f}**")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("✅ FINALIZAR PEDIDO", disabled=not LOJA_ABERTA):
            if not (np and rua and bairro): 
                st.warning("Por favor, preencha nome e endereço completo!")
            else:
                registrar_venda(nome_completo, total_final, ", ".join(itens_pedido))
                atualizar_fidelidade(nome_completo, brinde_ativo)
                
                msg = (f"*NOVO PEDIDO JUBILEU AÇAÍ*\n"
                       f"------------------\n"
                       f"*Cliente:* {nome_completo}\n"
                       f"*Endereço:* {rua}, {numero} - {bairro}\n"
                       f"------------------\n"
                       f"*Itens:* {', '.join(itens_pedido)}\n"
                       f"*Pagamento:* {pag}{troco_msg}\n"
                       f"*ENTREGA:* Grátis\n"
                       f"*TOTAL: R$ {total_final:.2f}*")
                
                link = f"https://wa.me/5537991031933?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{link}" target="_blank" class="btn-whats">🚀 ENVIAR PARA O WHATSAPP</a>', unsafe_allow_html=True)

    st.markdown("---")
    if st.button("v1.5", help="Admin"):
        st.session_state.admin_logado = "solicitar_senha"; st.rerun()

# --- 🔐 5. PAINEL DO DONO ---
if st.session_state.admin_logado == "solicitar_senha":
    senha = st.text_input("Senha Admin:", type="password")
    if st.button("Acessar"):
        if senha == SENHA_DONO: st.session_state.admin_logado = True; st.rerun()
        else: st.error("Senha incorreta!")
    if st.button("Voltar"): st.session_state.admin_logado = False; st.rerun()

if st.session_state.admin_logado is True:
    st.title("📊 Painel Jubileu")
    
    # 🟢 Botões de Abrir/Fechar Loja
    col_st1, col_st2 = st.columns(2)
    if col_st1.button("🟢 ABRIR LOJA"): 
        alternar_loja("ABERTA"); st.rerun()
    if col_st2.button("🔴 FECHAR LOJA"): 
        alternar_loja("FECHADA"); st.rerun()
    
    if os.path.exists(ARQUIVO_VENDAS):
        df_v = pd.read_csv(ARQUIVO_VENDAS)
        st.metric("Faturamento Total", f"R$ {df_v['Total'].sum():.2f}")
        
        st.subheader("📋 Histórico Completo")
        st.dataframe(df_v, use_container_width=True)
        
        if st.button("Limpar Histórico de Vendas"):
            os.remove(ARQUIVO_VENDAS); st.rerun()
    else:
        st.info("Nenhuma venda registrada.")

    if st.button("⬅️ Sair"): st.session_state.admin_logado = False; st.rerun()
