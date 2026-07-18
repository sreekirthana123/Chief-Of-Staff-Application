import streamlit as st
import streamlit.components.v1 as components

def render_aurora_landing_page(auth_url: str) -> None:
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; padding: 0; font-family: 'Inter', sans-serif; }}
            .landing-wrapper {{ width: 100%; padding: 40px 2%; box-sizing: border-box; }}
            .glass-card {{ background: rgba(10, 15, 30, 0.55); backdrop-filter: blur(24px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 20px; padding: 4rem; margin-bottom: 4rem; width: 100%; }}
            .card-title {{ font-size: 3.5rem; font-weight: 800; color: #90e0ef; border-bottom: 2px solid rgba(255,255,255,0.15); padding-bottom: 1rem; margin-bottom: 2rem; }}
            p {{ font-size: 2.2rem; color: #ffffff; margin-bottom: 1.5rem; }}
        </style>
    </head>
    <body>
        <div class="landing-wrapper">
            <div class="glass-card">
                <div class="card-title">Who I Am</div>
                <p>I'm <strong>V Sree Kirthana</strong>, an AI specialist...</p>
            </div>
            <div class="glass-card">
                <div class="card-title">What This Is</div>
                <p>Meet your new fully functional AI agent. <strong>Chief of Staff AI</strong>...</p>
            </div>
        </div>
    </body>
    </html>
    """
    # This guarantees the browser renders the HTML correctly
    components.html(html_code, height=1200)
