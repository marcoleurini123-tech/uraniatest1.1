import streamlit as st
import os
import hmac

# -----------------------------------------------------------------------------
# 1. CONFIGURAZIONE GENERALE STREAMLIT
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="URANIA QUANTITATIVE TERMINAL",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. GESTIONE AUTENTICAZIONE E SICUREZZA (ANTI-CRASH)
# -----------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
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

    with col_center:
        st.markdown(
            """
            <div class="login-card">
                <div style="font-size: 48px; margin-bottom: 8px;">🛡️</div>
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
            try:
                expected_password = st.secrets["APP_PASSWORD"]
                if hmac.compare_digest(pwd, expected_password):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Credenziali non valide.")
            except KeyError:
                st.error("Errore critico: 'APP_PASSWORD' mancante nel vault st.secrets.")
            except Exception as e:
                st.error(دا=f"Errore imprevisto di sistema: {str(e)}")
    st.stop()

# -----------------------------------------------------------------------------
# 3. SIDEBAR DI NAVIGAZIONE
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛡️ URANIA SYSTEM")
    st.caption("Macro Quantitative Terminal • EOD Engine")
    
    nav = st.radio(
        "Navigazione Moduli:",
        [
            "1. Macro Intelligence & Fed Liquidity",
            "2. Z-Score & COT Lab (CFTC)",
            "3. Quant Lab (Studi Storici Rea)",
            "4. POC Scanner & Telegram (Rea Radar)"
        ]
    )
    
    st.markdown("---")
    st.markdown("● **Pipeline Status:** `EOD Ready` ✅")
    
    if st.button("🔒 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# -----------------------------------------------------------------------------
# 4. ROUTER DINAMICO PROTETTO
# -----------------------------------------------------------------------------
if nav == "1. Macro Intelligence & Fed Liquidity":
    try:
        from pages_modules.page1_macro import render_page1
        render_page1()
    except Exception as e:
        st.error(f"Errore di esecuzione in Pagina 1: {str(e)}")

elif nav == "2. Z-Score & COT Lab (CFTC)":
    try:
        from pages_modules.page2_zscore_cot import render_page2
        render_page2()
    except Exception as e:
        st.error(f"Errore di esecuzione in Pagina 2: {str(e)}")

elif nav == "3. Quant Lab (Studi Storici Rea)":
    st.info("Modulo 3 in fase di sviluppo strutturato.")

elif nav == "4. POC Scanner & Telegram (Rea Radar)":
    st.info("Modulo 4 in fase di sviluppo strutturato.")
