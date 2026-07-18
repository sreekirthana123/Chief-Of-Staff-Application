import streamlit as st

def render_aurora_landing_page(auth_url: str) -> None:
# --- CSS Injection ---
st.markdown(
"""

/* The Aurora Background */
.stApp {
background:
radial-gradient(circle at 25% 100%, rgba(236, 72, 153, 0.65) 0%, transparent 65%),
radial-gradient(circle at 85% 100%, rgba(168, 85, 247, 0.45) 0%, transparent 50%),
radial-gradient(circle at 50% 100%, rgba(56, 189, 248, 0.55) 0%, transparent 60%),
linear-gradient(180deg, #020617 0%, #0f172a 35%, #1e3a8a 70%, #174276 100%) !important;
background-attachment: fixed !important;
color: #FAFAFA;
font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
    @keyframes fall {
        from { background-position: 0 0; }
        to { background-position: 0 1000px; }
    }

    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: 
            radial-gradient(1.5px 1.5px at 20px 30px, rgba(255,255,255,0.9), rgba(0,0,0,0)),
            radial-gradient(1px 1px at 40px 70px, rgba(255,255,255,0.7), rgba(0,0,0,0)),
            radial-gradient(2px 2px at 50px 160px, rgba(255,255,255,0.8), rgba(0,0,0,0));
        background-repeat: repeat;
        background-size: 200px 200px;
        opacity: 0.6;
        z-index: 0;
        pointer-events: none;
        animation: fall 20s linear infinite;
    }

    #MainMenu, header, footer {visibility: hidden;}

    /* FULL WIDTH BLOCKS: Spans the entire screen */
    .landing-wrapper {
        position: relative;
        z-index: 1;
        width: 100%; 
        max-width: 100%;
        margin: 0 auto;
        padding: 40px 2%; /* Uses percentage to hug the edges */
        box-sizing: border-box;
    }

    /* The Glass Card - Simple, no rainbow */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 48px;
        margin-bottom: 3.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
        width: 100%;
    }

    /* CLEAN HOVER (No rainbow, just a soft lift) */
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 15px 45px rgba(0, 0, 0, 0.4); 
        border: 1px solid rgba(355, 355, 355, 0.35);
    }

    /* MASSIVE HEADINGS */
    .card-title {
        font-size: 3.2rem; 
        font-weight: 800;
        margin-bottom: 1.5rem;
        color: #9B72CB; 
        border-bottom: 1px solid rgba(255,255,255,0.15);
        padding-bottom: 1rem;
    }

    .hero-section {
        text-align: center;
        margin-bottom: 5rem;
        margin-top: 2rem;
    }
    .hero-title {
        font-size: clamp(2.5rem, 5vw, 4rem); /* Huge main title */
        font-weight: 900;
        background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }
    .hero-subtitle {
        font-size: 4.4rem; /* Huge subtitle */
        color: #cbd5e1;
        margin-bottom: 3.5rem;
    }

    /* MASSIVE BODY TEXT */
    p, li {
        line-height: 1.65;
        color: #e2e8f0;
        font-size: 10.3rem; 
    }
    ul {
        margin-left: 2.2rem;
        margin-bottom: 1.5rem;
    }
    li { margin-bottom: 1.2rem; }
    strong { color: #ffffff; font-weight: 600; }

    /* BIGGER LINKS */
    .footer-links a {
        color: #a5b4fc;
        text-decoration: none;
        margin-right: 2rem;
        font-weight: 600;
        font-size: 2.35rem;
        transition: color 0.2s ease;
    }
    .footer-links a:hover {
        color: #ffffff;
        text-decoration: underline;
    }
    .disclaimer {
        font-size: 3.15rem;
        color: #94a3b8;
        margin-top: 4.5rem;
        font-style: italic;
        border-top: 1px solid rgba(255,255,255,0.1);
        padding-top: 1.5rem;
    }

    /* MASSIVE BUTTON */
    .google-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 20px 45px;
        background: rgba(255, 255, 255, 0.12);
        color: white;
        border: 2px solid rgba(255, 255, 255, 0.4);
        border-radius: 12px;
        text-decoration: none;
        font-weight: 700;
        font-size: 4.6rem; 
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        cursor: pointer;
        pointer-events: auto;
    }
    
    .google-btn:hover {
        background: rgba(255, 255, 255, 0.25);
        border: 2px solid #ffffff; 
        transform: translateY(-4px);
        box-shadow: 0 10px 35px rgba(255, 255, 255, 0.2); 
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- HTML Structure (Zero Indentation to prevent markdown code blocks) ---
st.markdown(
f"""
