import streamlit as st

def render_aurora_landing_page(auth_url: str) -> None:
    # --- CSS Injection ---
    st.markdown(
        """
        <style>
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
            opacity: 0.8;
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
<div class="landing-wrapper"><div class="hero-section"><div class="hero-title">Chief of Staff AI</div><div class="hero-subtitle">Intelligent Triage & Autonomous Scheduling for your Inbox.</div><a href="{auth_url}" target="_top" class="google-btn">🔑 Sign in with Google</a></div><div class="glass-card"><div class="card-title">What This Is</div><p>Meet your new fully functional AI agent. <strong>Chief of Staff AI</strong> acts as a ruthless gatekeeper for your attention. It connects securely to your Google account and automatically classifies your incoming emails into four buckets: <strong>Urgent</strong>, <strong>Needs Reply</strong>, <strong>FYI</strong>, and <strong>Ignore</strong>. You only give your energy to what actually matters, while the AI handles the heavy lifting of reading, sorting, and drafting.</p><p>Want to skip the manual steps? Hit the <strong>Run Full Pipeline</strong> button to instantly fetch your emails, triage them, generate all necessary drafts, and jump straight to the Approval Gate.</p></div><div class="glass-card"><div class="card-title">Inside the Engine: The Four Phases</div><p>This application operates on a strict, transparent four-step pipeline:</p><ul><li><strong>Phase 1: Inbox & Triage</strong><br>The agent pulls your live email threads and uses AI to analyze the context, intent, and urgency of every message, assigning a strict priority level to each one.</li><li><strong>Phase 2: Draft Generation</strong><br>For any email flagged as <em>Urgent</em> or <em>Needs Reply</em>, the AI instantly generates a highly contextual, professional draft response.</li><li><strong>Phase 3: Approval Gate (Human-in-the-Loop)</strong><br><strong>Total Control.</strong> The AI generates the responses, but it never sends an email without your explicit permission. You are in the driver's seat with three options for every draft:<ul><li><strong>Regenerate:</strong> Don't like the AI's first attempt? Click this to generate a brand new response.</li><li><strong>Edit:</strong> Jump in and manually tweak the text exactly how you want it.</li><li><strong>Approve:</strong> Once the draft is perfect, approve it.</li></ul>Only after you hit Approve will the <strong>Send</strong> button appear, allowing you to dispatch the email directly from the app. Mistakes do not make it to your outbox.</li><li><strong>Phase 4: Export Proof</strong><br>A complete audit trail of the AI's work. Once your triage is complete, you can download a full Proof of Work report as a cleanly formatted <strong>Markdown</strong> or <strong>HTML file</strong>.</li></ul></div><div class="glass-card"><div class="card-title">Smart Calendar Scheduling</div><p>More than just an email drafter, this agent understands time. If an incoming email asks for a meeting or proposes a time, the AI parses the request, checks your availability, and finds a free slot. Upon your approval, it automatically schedules the event and bookmarks it directly onto your <strong>Google Calendar</strong>.</p></div><div class="glass-card"><div class="card-title">Architecture & Timeline</div><p>This agent is powered by a robust, modern tech stack designed for speed and security:</p><ul><li><strong>Core Logic:</strong> Python</li><li><strong>Frontend UI:</strong> Streamlit (Custom Aurora Glassmorphism)</li><li><strong>AI Engine:</strong> Google Gemini 2.5 Flash</li><li><strong>Cloud Infrastructure:</strong> Google Cloud Platform (OAuth 2.0 Web Flow)</li><li><strong>Integrations:</strong> Gmail API, Google Calendar API</li></ul><p>I architected, built, and deployed this entire system from the ground up in <strong>2 Weeks</strong>.</p></div><div class="glass-card"><div class="card-title">Who I Am</div><p>I'm <strong>V Sree Kirthana</strong>, an AI specialist, full-stack developer, and automation engineer based in Hyderabad, India. Currently pursuing my B.Tech in Computer Science with a specialization in Artificial Intelligence and Machine Learning (AIML), my core focus is bridging the gap between raw datasets and production-ready machine learning architectures.</p><p>I engineer automated, self-sustaining AI workflows and the full-stack systems required to support them. My practical experience includes processing analytical data and building predictive algorithms as a Data Science Intern at CodSoft, alongside building robust web frameworks during my Full-Stack Development stint at Cognifyz Technologies. I've also advanced my capabilities in prompt engineering and next-gen autonomous systems through the Outskill GenAI Mastermind Program. Whether I am integrating generative AI tools, optimizing data pipelines, or writing core Python logic, I don't just write code—I architect intelligent solutions that solve real-world bottlenecks.</p></div><div class="glass-card"><div class="card-title">Connect With Me</div><div class="footer-links"><a href="https://bold.pro/" target="_blank">Bold.pro</a><a href="https://www.linkedin.com/in/v-sree-kirthana-565b4a367?utm_source=share_via&utm_content=profile&utm_medium=member_android" target="_blank">LinkedIn</a><a href="https://github.com/sreekirthana123/sreekirthana123" target="_blank">GitHub</a><br><br><a href="https://github.com/sreekirthana123/Chief-Of-Staff-Application/blob/master/PRIVACY.md" target="_blank" style="font-size:0.9em; font-weight:normal;">Privacy Policy</a><a href="https://github.com/sreekirthana123/Chief-Of-Staff-Application/blob/master/TERMS.md" target="_blank" style="font-size:0.9em; font-weight:normal;">Terms & Conditions</a></div><p class="disclaimer">Note: This application currently runs on a free-tier API. If you encounter an "API limit reached" error, I apologize for the inconvenience! A future update is coming soon to upgrade the model to a paid version for uninterrupted access.</p></div></div>
""",
        unsafe_allow_html=True
    )
