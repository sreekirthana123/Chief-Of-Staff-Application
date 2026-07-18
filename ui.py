import streamlit as st

def render_aurora_landing_page(auth_url: str) -> None:
    st.markdown(f"""
        <style>
        /* Vibrant Background with extra glitter */
        .stApp {{
            background: linear-gradient(160deg, #020b26 0%, #0056b3 35%, #99ddff 70%, #ff80ab 100%) !important;
            background-attachment: fixed !important;
            color: #FAFAFA;
            font-family: 'Inter', sans-serif;
        }}
        .stApp::before {{
            content: '';
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: 
                radial-gradient(2.5px 2.5px at 20px 30px, #ffffff, rgba(0,0,0,0)),
                radial-gradient(3px 3px at 40px 70px, rgba(255,255,255,0.9), rgba(0,0,0,0)),
                radial-gradient(2px 2px at 80px 160px, rgba(255,255,255,0.8), rgba(0,0,0,0)),
                radial-gradient(2.5px 2.5px at 150px 40px, #ffffff, rgba(0,0,0,0));
            background-repeat: repeat;
            background-size: 250px 250px;
            opacity: 0.85; 
            z-index: 0;
            pointer-events: none;
        }}
        #MainMenu, header, footer {{visibility: hidden;}}
        
        /* Full width and large content */
        .landing-wrapper {{ width: 100%; max-width: 100%; padding: 40px 2%; box-sizing: border-box; }}
        .glass-card {{ background: rgba(10, 15, 30, 0.55); backdrop-filter: blur(24px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 20px; padding: 5rem; margin-bottom: 4rem; width: 100%; }}
        .card-title {{ font-size: 3.5rem; font-weight: 800; color: #90e0ef; border-bottom: 2px solid rgba(255,255,255,0.15); padding-bottom: 1rem; margin-bottom: 2rem; }}
        p, li {{ font-size: 2.2rem !important; line-height: 1.9; color: #ffffff; margin-bottom: 1.5rem; }}
        ul {{ margin-left: 3.5rem; margin-bottom: 2rem; }}
        li {{ margin-bottom: 1.5rem; }}
        strong {{ color: #90e0ef; font-weight: 700; }}
        
        .hero-section {{ text-align: center; margin-bottom: 6rem; margin-top: 3rem; }}
        .hero-title {{ font-size: 8rem; font-weight: 900; color: white; margin-bottom: 1rem; }}
        .hero-subtitle {{ font-size: 2.8rem; color: #cbd5e1; margin-bottom: 4rem; }}
        .google-btn {{ display: inline-block; padding: 25px 60px; background: rgba(255, 255, 255, 0.15); color: white; border-radius: 15px; font-size: 2.2rem; text-decoration: none; font-weight: bold; }}
        .footer-links a {{ color: #a5b4fc; font-size: 1.8rem; margin-right: 2.5rem; }}
        </style>

        <div class="landing-wrapper">
            <div class="hero-section">
                <div class="hero-title">Chief of Staff AI</div>
                <div class="hero-subtitle">Intelligent Triage & Autonomous Scheduling for your Inbox.</div>
                <a href="{auth_url}" target="_top" class="google-btn">🔑 Sign in with Google</a>
            </div>
            
            <div class="glass-card">
                <div class="card-title">Who I Am</div>
                <p>I'm <strong>V Sree Kirthana</strong>, an AI specialist, full-stack developer, and automation engineer based in Hyderabad, India. Currently pursuing my B.Tech in Computer Science with a specialization in Artificial Intelligence and Machine Learning (AIML), my core focus is bridging the gap between raw datasets and production-ready machine learning architectures.</p>
                <p>I engineer automated, self-sustaining AI workflows and the full-stack systems required to support them. My practical experience includes processing analytical data and building predictive algorithms as a Data Science Intern at CodSoft, alongside building robust web frameworks during my Full-Stack Development stint at Cognifyz Technologies. I've also advanced my capabilities in prompt engineering and next-gen autonomous systems through the Outskill GenAI Mastermind Program. Whether I am integrating generative AI tools, optimizing data pipelines, or writing core Python logic, I don't just write code—I architect intelligent solutions that solve real-world bottlenecks.</p>
            </div>

            <div class="glass-card">
                <div class="card-title">What This Is</div>
                <p>Meet your new fully functional AI agent. <strong>Chief of Staff AI</strong> acts as a ruthless gatekeeper for your attention. It connects securely to your Google account and automatically classifies your incoming emails into four buckets: <strong>Urgent</strong>, <strong>Needs Reply</strong>, <strong>FYI</strong>, and <strong>Ignore</strong>. You only give your energy to what actually matters, while the AI handles the heavy lifting of reading, sorting, and drafting.</p>
                <p>Want to skip the manual steps? Hit the <strong>Run Full Pipeline</strong> button to instantly fetch your emails, triage them, generate all necessary drafts, and jump straight to the Approval Gate.</p>
            </div>

            <div class="glass-card">
                <div class="card-title">Inside the Engine: The Four Phases</div>
                <ul>
                    <li><strong>Phase 1: Inbox & Triage:</strong> The agent pulls your live email threads and uses AI to analyze the context, intent, and urgency of every message.</li>
                    <li><strong>Phase 2: Draft Generation:</strong> For any email flagged as <em>Urgent</em> or <em>Needs Reply</em>, the AI instantly generates a highly contextual, professional draft response.</li>
                    <li><strong>Phase 3: Approval Gate:</strong> You are in the driver's seat with three options: Regenerate, Edit, or Approve.</li>
                    <li><strong>Phase 4: Export Proof:</strong> A complete audit trail of the AI's work available as Markdown or HTML.</li>
                </ul>
            </div>
            
            <div class="glass-card">
                <div class="card-title">Connect With Me</div>
                <div class="footer-links">
                    <a href="https://in.bold.pro/my/v-sreekirthana" target="_blank">Bold.pro</a>
                    <a href="https://www.linkedin.com/in/v-sree-kirthana-565b4a367" target="_blank">LinkedIn</a>
                    <a href="https://github.com/sreekirthana123/sreekirthana123" target="_blank">GitHub</a>
                    <br><br>
                    <a href="https://sree-kirthana-studypilot.streamlit.app/" target="_blank" style="color: #ff80ab; font-weight: 800;">🚀 View my recent AI Agent StudyPilot</a>
                    <br><br>
                    <a href="https://github.com/sreekirthana123/Chief-Of-Staff-Application/blob/master/PRIVACY.md" target="_blank">Privacy Policy</a>
                    <a href="https://github.com/sreekirthana123/Chief-Of-Staff-Application/blob/master/TERMS.md" target="_blank">Terms & Conditions</a>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
