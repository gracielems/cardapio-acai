# --- TOPO COM A IMAGEM 3D GIGANTE (SISTEMA ULTRA INTELIGENTE) ---
# Agora incluímos o nome com erro que o sistema criou
if os.path.exists("logo3d.jpg.png"):
    st.image("logo3d.jpg.png", use_container_width=True)
elif os.path.exists("logo3d.png"):
    st.image("logo3d.png", use_container_width=True)
elif os.path.exists("logo3d.jpg"):
    st.image("logo3d.jpg", use_container_width=True)
elif os.path.exists("logo3d.jpeg"):
    st.image("logo3d.jpeg", use_container_width=True)
elif os.path.exists("logo3d.webp"):
    st.image("logo3d.webp", use_container_width=True)
else:
    # Se não achar nada, mostra o banner padrão
    st.markdown("""
    <div style="background: linear-gradient(90deg, #4B0082 0%, #8A2BE2 100%); padding: 25px; border-radius: 0px 0px 30px 30px; color: white !important; text-align: center; margin: -60px -20px 20px -20px;">
        <h1 style="margin-bottom: 0;">🍧 Jubileu Açaí</h1>
        <p style="margin-top: 0;">Nova Serrana - O melhor açaí da região!</p>
    </div>
    """, unsafe_allow_html=True)
