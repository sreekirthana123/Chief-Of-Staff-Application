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
            max-width: 100%;
            margin: 0 auto;
            padding: 40px 2%;
            box-sizing: border-box;
        }

        /* DARKER GLASS CARD FOR CONTRAST */
        .glass-card {
            background: rgba(10, 15, 30, 0.55);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 5rem; 
            margin-bottom: 4rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            transition: transform 0.3s ease;
            width: 100%;
        }

        .glass-card:hover {
            transform: translateY(-5px);
        }

        /* EVEN BIGGER HEADINGS */
        .card-title {
            font-size: 3.5rem; 
            font-weight: 800;
            margin-bottom: 2rem;
            color: #90e0ef; 
            border-bottom: 2px solid rgba(255,255,255,0.15);
            padding-bottom: 1rem;
        }

        .hero-section {
            text-align: center;
            margin-bottom: 6rem;
            margin-top: 3rem;
        }
        .hero-title {
            font-size: clamp(5rem, 10vw, 8rem); 
            font-weight: 900;
            background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
            line-height: 1.2;
        }
        .hero-subtitle {
            font-size: 2.8rem; 
            color: #cbd5e1;
            margin-bottom: 4rem;
        }

        /* EXTRA LARGE BODY TEXT */
        p, li {
            line-height: 1.9;
            color: #ffffff; 
            font-size: 2rem;
        }
        ul {
            margin-left: 3.5rem;
            margin-bottom: 2rem;
        }
        li { margin-bottom: 1.5rem; }
        strong { color: #90e0ef; font-weight: 700; }

        /* BIGGER LINKS */
        .footer-links a {
            color: #a5b4fc;
            text-decoration: none;
            margin-right: 2.5rem;
            font-weight: 600;
            font-size: 1.8rem;
            transition: color 0.2s ease;
        }
        .footer-links a:hover {
            color: #ffffff;
            text-decoration: underline;
        }
        .disclaimer {
            font-size: 1.4rem;
            color: #cbd5e1;
            margin-top: 4rem;
            font-style: italic;
            border-top: 1px solid rgba(255,255,255,0.1);
            padding-top: 1.5rem;
        }

        /* MASSIVE BUTTON */
        .google-btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 25px 60px;
            background: rgba(255, 255, 255, 0.15);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.5);
            border-radius: 15px;
            text-decoration: none;
            font-weight: 700;
            font-size: 2.2rem; 
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }
        
        .google-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            border: 2px solid #ffffff; 
            transform: translateY(-5px);
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # --- Structural Layout Layout ---
    st.markdown('<div class="landing-wrapper">', unsafe_allow_html=True)

    # CHANGE 1: HERO SECTION MOVED TO THE ABSOLUTE TOP
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

    # WHAT THIS IS SECTION
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">What This Is</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <p>Meet your new fully functional AI agent. <strong>Chief of Staff AI</strong> acts as a ruthless gatekeeper for your attention. It connects securely to your Google account and automatically classifies your incoming emails into four buckets: <strong>Urgent, Needs Reply, FYI, and Ignore</strong>. You only give your energy to what actually matters, while the AI handles the heavy lifting of routing, sorting, and drafting.</p>
        <p>Want to skip the manual steps? Hit the <em>Run Full Pipeline</em> button to instantly fetch your emails, triage them, generate all necessary drafts, and jump straight to the Approval Gate.</p>
        """,
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # INSIDE THE ENGINE SECTION
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

    # WHO I AM SECTION MOVED TO THE BOTTOM
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Who I Am</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <p>I'm Sree Kirthana, an AI specialist, full-stack developer, and automation engineer based in Hyderabad, India. Currently pursuing my B.Tech in Computer Science with a specialization in Artificial Intelligence and Machine Learning (AI/ML), my core focus is bridging the gap between raw datasets and production-ready machine learning architectures.</p>
        <p>I engineer automated, self-sustaining AI workflows and the full-stack systems required to support them. My practical experience includes processing analytical data and building predictive algorithms as a Data Science Intern at CozSclt, alongside building robust web frameworks during my Full-Stack Development stint at Cognifyz Technologies. I've also advanced my capabilities in prompt engineering and next-gen autonomous systems through the Outskli GenAI Mastermind Program. Whether I am integrating generative AI tools, optimizing data pipelines, or writing core Python logic, I don't just write code—I architect intelligent solutions that solve real-world bottlenecks.</p>
        """,
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # End landing-wrapper
