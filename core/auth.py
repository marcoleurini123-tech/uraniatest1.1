import streamlit as st
from pathlib import Path

def check_authentication() -> bool:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.markdown(
        """
        <style>
        .stApp {
            background-color: #030712 !important;
            background-image: radial-gradient(circle at 50% 35%, #0f172a 0%, #030712 100%) !important;
        }
        .login-card {
            background: rgba(15, 23, 42, 0.95);
            border: 1px solid rgba(212, 175, 55, 0.35);
            border-radius: 16px;
            padding: 30px 20px;
            text-align: center;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7);
        }
        .brand-title {
            font-size: 30px;
            font-weight: 900;
            letter-spacing: 4px;
            color: #f8fafc;
            margin-top: 10px;
            margin-bottom: 2px;
        }
        .brand-motto {
            font-size: 11px;
            letter-spacing: 3px;
            color: #d4af37;
            font-weight: 700;
            margin-bottom: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 1.3, 1])

    # Percorso assoluto robusto per Streamlit Cloud
    root_dir = Path(__file__).resolve().parent.parent
    logo_path = root_dir / "urania_logo.png"
    if not logo_path.exists():
        logo_path = root_dir / "urania.png"

    with col_center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        else:
            st.markdown('<div style="font-size: 48px; margin-bottom: 8px;">🛡️</div>', unsafe_allow_html=True)

        st.markdown(
            """
            <div class="brand-title">URANIA</div>
            <div class="brand-motto">PRECISION. CONSISTENCY. GROWTH.</div>
            <p style="color: #94a3b8; font-size: 13px; margin: 0 0 10px 0;">
                Macro Quantitative Terminal • EOD Execution Engine
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)
        pwd = st.text_input("Password di Accesso:", type="password", placeholder="••••••••••••")
        
        if st.button("SBLOCCA TERMINALE", use_container_width=True):
            if pwd == "Serafino12?#":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Credenziali errate.")

    return False
