import streamlit as st

def render_aurora_landing_page(auth_url: str) -> None:
    # --- CSS Injection ---
    st.markdown(
        """
        <style>
        /* VIBRANT GRADIENT BACKGROUND: Dark Blue -> Light Blue -> Very Light Blue -> Pink */
        .stApp {
            background: linear-gradient(160deg, #020b26 0%, #0056b3 35%, #99ddff 70%, #ff80ab 100%) !important;
            background-attachment: fixed !important;
            color: #FAFAFA;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* EXTRA GLITTER */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: 
                radial-gradient(2.5px 2.5px at 20px 30px, #ffffff, rgba(0,0,0,0)),
                radial-gradient(3px 3px at 40px 70px, rgba(255,255,255,0.9), rgba(0,0,0,0)),
                radial-gradient(2px 2px at 80px 160px, rgba(255,255,255,0.8), rgba(0,0,0,0)),
                radial-gradient(2.5px 2.5px at 150px 40px, #ffffff, rgba(0,0,0,0)),
                radial-gradient(3px 3px at 200px 90px, rgba(255,255,255,0.9), rgba(0,0,0,0)),
                radial-gradient(2px 2px at 250px 140px, rgba(255,255,255,0.8), rgba(0,0,0,0)),
                radial-gradient(3px 3px at 300px 30px, #ffffff, rgba(0,0,0,0)),
                radial-gradient(2px 2px at 350px 180px, rgba(255,255,255,0.9), rgba(0,0,0,0));
            background-repeat: repeat;
            background-size: 250px 250px;
            opacity: 0.85; 
            z-index: 0;
            pointer-events: none;
        }

        #MainMenu, header, footer {visibility: hidden;}

        /* FULL WIDTH BLOCKS */
        .landing-wrapper {
            position: relative;
            z-index: 1;
            width: 100%; 
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            box-sizing: border-box;
        }

        /* PREMIUM WHITE GLASS CARD (TRUE GLASSMORPHISM) */
        .glass-card {
            background: rgba(255, 255, 255, 0.07);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.25);
            border-radius: 24px;
            padding: 3.5rem; 
            margin-bottom: 3.5rem;
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            width: 100%;
            box-sizing: border-box;
        }

        .glass-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 16px 48px rgba(0, 0, 0, 0.35);
        }

        /* FOUR PILLARS MINI CARDS */
        .pillar-card {
            background: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            margin: 10px 0;
        }
        .pillar-title {
            font-size: 1.4rem;
            font-weight: 700;
            margin-top: 0.5rem;
            color: #ffffff;
        }

        /* TYPOGRAPHY HIERARCHY */
        .card-title {
            font-size: 2.5rem; 
            font-weight: 800;
            margin-bottom: 1.8rem;
            color: #ffffff; 
            border-bottom: 2px solid rgba(255,255,255,0.2);
            padding-bottom: 0.8rem;
        }

        .hero-section {
            text-align: center;
            margin-bottom: 5rem;
            margin-top: 4rem;
        }
        .hero-title {
            font-size: clamp(3.5rem, 7vw, 5.5rem); 
            font-weight: 900;
            background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1.5rem;
            line-height: 1.15;
            letter-spacing: -0.03em;
        }
        .hero-subtitle {
            font-size: 1.75rem; 
            color: #e2e8f0;
            margin-bottom: 3.5rem;
            font-weight: 400;
        }

        /* HIGHLY VISIBLE BODY TEXT */
        p, li {
            line-height: 1.75;
            color: #f8fafc; 
            font-size: 1.2rem;
        }
        ul {
            margin-left: 2rem;
            margin-bottom: 1.5rem;
        }
        li { margin-bottom: 1rem; }
        strong { color: #ffffff; font-weight: 700; }

        /* INTUITIVE TAGS FOR INFO BLOCKS */
        .tech-pill {
            display: inline-block;
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.25);
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.95rem;
            font-weight: 600;
            margin: 5px;
            color: #ffffff;
        }

        /* HIGH VISIBILITY CTAS */
        .google-btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 16px 42px;
            background: #ffffff;
            color: #020b26 !important;
            border: none;
            border-radius: 14px;
            text-decoration: none;
            font-weight: 700;
            font-size: 1.3rem; 
            box-shadow: 0 8px 24px rgba(255, 255, 255, 0.25);
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }
        
        .google-btn:hover {
            background: #f1f5f9;
            transform: translateY(-3px);
            box-shadow: 0 12px 32px rgba(255, 255, 255, 0.4);
        }

        .footer-links a {
            color: #cbd5e1;
            text-decoration: none;
            margin-right: 2rem;
            font-weight: 600;
            font-size: 1.1rem;
            transition: color 0.2s ease;
        }
        .footer-links a:hover {
            color: #ffffff;
            text-decoration: underline;
        }
        .disclaimer {
            font-size: 0.95rem;
            color: #94a3b8;
            margin-top: 3.5rem;
            font-style: italic;
            border-top: 1px solid rgba(255,255,255,0.15);
            padding-top: 1.2rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # --- Structural Layout Layout ---
    st.markdown('<div class="landing-wrapper">', unsafe_allow_html=True)

    # 1. HERO SECTION (CHIEF OF STAFF COMES FIRST)
    st.markdown(
        f"""
        <div class="hero-section">
            <h1 class="hero-title">Chief of Staff AI</h1>
            <p class="hero-subtitle">Intelligent Triage & Autonomous Scheduling for your Inbox.</p>
            <a href="{auth_url}" target="_self" class="google-btn">
                 Sign in with Google
            </a>
        </div>
        """, 
        unsafe_allow_html=True
    )

    # 2. WHAT THIS IS SECTION
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">What This Is</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <p>Meet your new fully functional AI agent. <strong>Chief of Staff AI</strong> acts as a ruthless gatekeeper for your attention. 
        It connects securely to your Google account and automatically classifies your incoming emails into four specialized buckets. 
        You only give your energy to what actually matters, while the AI handles the heavy lifting of routing, sorting, and drafting.</p>
        <p style="margin-top: 1.5rem; margin-bottom: 2rem;">Want to skip the manual steps? Hit the <em>Run Full Pipeline</em> button to instantly fetch your emails, triage them, generate all necessary drafts, and jump straight to the Approval Gate.</p>
        """,
        unsafe_allow_html=True
    )
    
    # 4-Pillars Visual Cards Grid Injection
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="pillar-card">🚨<div class="pillar-title">Urgent</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="pillar-card">💬<div class="pillar-title">Needs Reply</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="pillar-card">📌<div class="pillar-title">FYI</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="pillar-card">🗑️<div class="pillar-title">Ignore</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. INSIDE THE ENGINE SECTION
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Inside the Engine: The Four Phases</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <p>The application operates on a strict, transparent four-stage pipeline:</p>
        <ul>
            <li><strong>Phase 1: Inbox & Triage</strong> — The agent pulls your latest unread emails and evaluates their context, content, and urgency footprint, assigning them straight to their priority matrix.</li>
            <li><strong>Phase 2: Draft Generation</strong> — For emails flagged as Urgent or Needs Reply, the business logic generates contextual, highly tailored markdown response drafts.</li>
            <li><strong>Phase 3: Approval Gate (Human-In-The-Loop)</strong> — Crucial Guardrails. No automation context is sent back without your thumbs up. Review, tweak, and instantly track the text vectors before hitting dispatch.</li>
            <li><strong>Phase 4: Dispatch Pipeline</strong> — Once you approve, the system dispatches the drafts securely back to the thread, clearing out clutter and moving you straight to Inbox Zero.</li>
        </ul>
        """,
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. WHO I AM SECTION (MOVED TO BOTTOM)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Who I Am</div>', unsafe_allow_html=True)
    st.markdown(
        """
    I'm Sree Kirthana, an AI specialist, full-stack developer, and automation engineer. My core focus is bridging the gap between raw datasets and production-ready machine learning architectures.I engineer automated, self-sustaining AI workflows and the infrastructure required to support them. Whether I am integrating generative AI tools, optimizing data pipelines, or writing core Python logic, I don't just write code—I architect intelligent solutions that solve real-world bottlenecks.""",unsafe_allow_html=True)# Modern Skills Accent Pillsst.markdown("""PythonAI / MLLLM OpsStreamlitFull-Stack Automation""",unsafe_allow_html=True)st.markdown('', unsafe_allow_html=True)st.markdown('', unsafe_allow_html=True) # End landing-wrapper
