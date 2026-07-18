import streamlit as st

def render_aurora_landing_page(auth_url: str) -> None:
    # --- CSS Injection ---
    st.markdown("""
        <style>
        .landing-wrapper { width: 100%; max-width: 100%; margin: 0 auto; padding: 40px 2%; }
        .glass-card { background: rgba(10, 15, 30, 0.55); backdrop-filter: blur(24px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 20px; padding: 5rem; margin-bottom: 4rem; width: 100%; }
        .card-title { font-size: 3.5rem; font-weight: 800; color: #90e0ef; border-bottom: 2px solid rgba(255,255,255,0.15); padding-bottom: 1rem; margin-bottom: 2rem; }
        p { font-size: 2.2rem !important; line-height: 1.9; color: #ffffff; }
        .hero-section { text-align: center; margin-bottom: 6rem; }
        .google-btn { display: inline-block; padding: 25px 60px; background: rgba(255, 255, 255, 0.15); color: white; border-radius: 15px; font-size: 2.2rem; text-decoration: none; }
        </style>
    """, unsafe_allow_html=True)

    # --- HTML Structure ---
    st.markdown(f"""
        <div class="landing-wrapper">
            <div class="hero-section">
                <h1>Chief of Staff AI</h1>
                <p>Intelligent Triage & Autonomous Scheduling for your Inbox.</p>
                <a href="{auth_url}" target="_top" class="google-btn">🔑 Sign in with Google</a>
            </div>
            <div class="glass-card">
                <div class="card-title">Who I Am</div>
                <p>I'm <strong>V Sree Kirthana</strong>, an AI specialist...</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
