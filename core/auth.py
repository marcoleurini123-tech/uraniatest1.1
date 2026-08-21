import streamlit as st
import os

def check_authentication() -> bool:
    """Verifica e gestisce la sessione di accesso con interfaccia protetta."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    # Styling Dark & Responsive Container
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #030712 !important;
            background-image: radial-gradient(circle at 50% 30%, #0f172a 0%, #030712 100%) !important;
        }
        .login-card {
            background: rgba(15, 23, 42, 0.95);
            border: 1px solid rgba(212, 175, 55, 0.35);
            border-radius: 16px;
            padding: 30px 25px;
            text-align: center;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7);
            margin-bottom: 20px;
        }
        .brand-title {
            font-size: 32px;
            font-weight: 900;
            letter-spacing: 5px;
            color: #f8fafc;
            margin: 5px 0 0 0;
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

    with col_center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        if os.path.exists("urania_logo.png"):
            st.image("urania_logo.png", width=180)
        else:
            st.markdown('<div style="font-size: 48px; margin-bottom: 8px;">🛡️</div>', unsafe_allow_html=True)

        st.markdown(
            """
            <div class="brand-title">URANIA</div>
            <div class="brand-motto">PRECISION. CONSISTENCY. GROWTH.</div>
            <p style="color: #94a3b8; font-size: 13px; margin: 0;">
                Macro Quantitative Terminal • EOD Engine
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
