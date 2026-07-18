import streamlit as st
import streamlit.components.v1 as components

def render_aurora_landing_page(auth_url: str) -> None:
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ 
                margin: 0; padding: 0; font-family: 'Inter', sans-serif;
                background: linear-gradient(160deg, #020b26, #0056b3, #99ddff, #ff80ab);
                min-height: 100vh;
            }}
            .landing-wrapper {{ width: 100%; max-width: 100%; padding: 40px 2%; box-sizing: border-box; }}
            .glass-card {{ 
                background: rgba(10, 15, 30, 0.55); backdrop-filter: blur(24px); 
                border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 20px; 
                padding: 4rem; margin-bottom: 4rem; width: 100%;
            }}
            .card-title {{ font-size: 3.5rem; font-weight: 800; color: #90e0ef; border-bottom: 2px solid rgba(255,255,255,0.15); padding-bottom: 1rem; margin-bottom: 2rem; }}
            p, li {{ font-size: 2.2rem; line-height: 1.8; color: #ffffff; margin-bottom: 1.5rem; }}
            .hero-section {{ text-align: center; margin-bottom: 6rem; padding-top: 3rem; }}
            .hero-title {{ font-size: 7rem; font-weight: 900; color: white; margin-bottom: 1rem; }}
            .hero-subtitle {{ font-size: 2.8rem; color: #cbd5e1; margin-bottom: 3rem; }}
            .google-btn {{ display: inline-block; padding: 25px 60px; background: rgba(255, 255, 255, 0.15); color: white; border-radius: 15px; font-size: 2.2rem; text-decoration: none; font-weight: bold; }}
            .footer-links a {{ color: #a5b4fc; font-size: 1.8rem; margin-right: 2rem; }}
        </style>
    </head>
    <body>
        <div class="landing-wrapper">
            <div class="hero-section">
                <div class="hero-title">Chief of Staff AI</div>
                <div class="hero-subtitle">Intelligent Triage & Autonomous Scheduling for your Inbox.</div>
                <a href="{auth_url}" target="_top" class="google-btn">🔑 Sign in with Google</a>
            </div>
            <div class="glass-card">
                <div class="card-title">Who I Am</div>
                <p>I'm <strong>V Sree Kirthana</strong>, an AI specialist, full-stack developer...</p>
            </div>
            <!-- Add other cards here -->
        </div>
    </body>
    </html>
    """
    components.html(html_content, height=2500)
