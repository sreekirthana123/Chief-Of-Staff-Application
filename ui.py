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

    # --- Structural Layout ---
    st.markdown('<div class="landing-wrapper">', unsafe_allow_html=True)

    # 1. HERO SECTION (CHIEF OF STAFF AT TOP)
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
 # 2. WHO I AM SECTION (MOVED TO BOTTOM)
    st.markdown(
        """
        <div class="glass-card">
            <div class="card-title">Who I Am</div>
            <p>I’m <strong>V Sree Kirthana</strong>, an AI specialist, full-stack developer, and automation engineer based in Hyderabad, India. Currently pursuing my B.Tech in Computer Science with a specialization in Artificial Intelligence and Machine Learning (AIML), my core focus is bridging the gap between raw datasets and production-ready machine learning architectures.</p>
            <p style="margin-top: 1.5rem;">I engineer automated, self-sustaining AI workflows and the full-stack systems required to support them. My practical experience includes processing analytical data and building predictive algorithms as a Data Science Intern at <strong>CodSoft</strong>, alongside building robust web frameworks during my Full-Stack Development stint at <strong>Cognifyz Technologies</strong>. I've also advanced my capabilities in prompt engineering and next-gen autonomous systems through the <strong>Outskill GenAI Mastermind Program</strong>. Whether I am integrating generative AI tools, optimizing data pipelines, or writing core Python logic, I don't just write code—I architect intelligent solutions that solve real-world bottlenecks.</p>
            </div>
            """,
        unsafe_allow_html=True
    )
    # 3. WHAT THIS IS SECTION
    st.markdown(
        """
        <div class="glass-card">
            <div class="card-title">What This Is</div>
            <p>Meet your new fully functional AI agent. <strong>Chief of Staff AI</strong> acts as a ruthless gatekeeper for your attention. It connects securely to your Google account and automatically classifies your incoming emails into four buckets: <strong>Urgent, Needs Reply, FYI, and Ignore</strong>. You only give your energy to what actually matters, while the AI handles the heavy lifting of reading, sorting, and drafting.</p>
            <p style="margin-top: 1.5rem;">Want to skip the manual steps? Hit the <em>Run Full Pipeline</em> button to instantly fetch your emails, triage them, generate all necessary drafts, and jump straight to the Approval Gate.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 4. INSIDE THE ENGINE SECTION
    st.markdown(
        """
        <div class="glass-card">
            <div class="card-title">Inside the Engine: The Four Phases</div>
            <p>This application operates on a strict, transparent four-step pipeline:</p>
            <ul>
                <li><strong>Phase 1: Inbox & Triage</strong> — The agent pulls your live email threads and uses AI to analyze the context, intent, and urgency of every message, assigning a strict priority level to each one.</li>
                <li><strong>Phase 2: Draft Generation</strong> — For any email flagged as Urgent or Needs Reply, the AI instantly generates a highly contextual, professional draft response.</li>
                <li><strong>Phase 3: Approval Gate (Human-in-the-Loop)</strong> — Total Control. The AI generates the responses, but it never sends an email without your explicit permission. You are in the driver's seat with three options for every draft:
                    <ul>
                        <li><strong>Regenerate:</strong> Don't like the AI's first attempt? Click this to generate a brand new response.</li>
                        <li><strong>Edit:</strong> Jump in and manually tweak the text exactly how you want it.</li>
                        <li><strong>Approve:</strong> Once the draft is perfect, approve it.</li>
                    </ul>
                    Only after you hit Approve will the Send button appear, allowing you to dispatch the email directly from the app. Mistakes do not make it to your outbox.
                </li>
                <li><strong>Phase 4: Export Proof</strong> — A complete audit trail of the AI's work. Once your triage is complete, you can download a full Proof of Work report as a cleanly formatted Markdown or HTML file.</li>
            </ul>
            <p style="margin-top: 2rem;"><strong>Smart Calendar Scheduling</strong><br>
            More than just an email drafter, this agent understands time. If an incoming email asks for a meeting or proposes a time, the AI parses the request, checks your availability, and finds a free slot. Upon your approval, it automatically schedules the event and bookmarks it directly onto your Google Calendar.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    # 5. THE TOOLS I USED SECTION
    st.markdown(
        """
        <div class="glass-card">
            <div class="card-title">The Tools I Used</div>
            <p>This agent is powered by a robust, modern tech stack designed for speed and security:</p>
            <ul>
                <li><strong>Core Logic:</strong> Python</li>
                <li><strong>Frontend UI:</strong> Streamlit (Custom Aurora Glassmorphism)</li>
                <li><strong>AI Engine:</strong> Google Gemini 2.5 Flash</li>
                <li><strong>Cloud Infrastructure:</strong> Google Cloud Platform (OAuth 2.0 Web Flow)</li>
                <li><strong>Integrations:</strong> Gmail API, Google Calendar API</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
        # 6. BUILD TIMELINE SECTION
    st.markdown(
        """
        <div class="glass-card">
            <div class="card-title">The Build Timeline</div>
            <p>I architected, built, and deployed this entire system from the ground up in [Insert Time - e.g., 2 Weeks].</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    # 8. LEGAL FOOTER AND DISCLAIMER
    st.markdown(
        """
        <div class="glass-card">
            <p class="footer-links" style="text-align: center; margin-bottom: 2rem;">
                <a href="https://github.com" target="_blank">Privacy Policy</a> | 
                <a href="https://github.com" target="_blank">Terms & Conditions</a>
            </p>
            <div class="disclaimer">
                <strong>Note:</strong> This application currently runs on a free-tier API. If you encounter an "API limit reached" error, I apologize for the inconvenience! A future update is coming soon to upgrade the model to a paid version for uninterrupted access.
            <p style="margin-top: 2.5rem;" class="footer-links">
                <strong>Connect with me:</strong><br>
                <a href="https://github.com" target="_blank">Bento.me / GitHub</a> | 
                <a href="https://linkedin.com" target="_blank">LinkedIn</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True) # End landing-wrapper
