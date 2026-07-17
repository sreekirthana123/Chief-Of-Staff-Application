import streamlit as st

def render_aurora_landing_page(auth_url: str) -> None:
    st.title("✍️ Chief of Staff AI")
    st.subheader("Intelligent Triage & Autonomous Scheduling for your Inbox.")
    
    st.write("---")
    
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        st.markdown("### What This Is")
        st.write(
            "Meet your new fully functional AI agent. **Chief of Staff AI** acts as a ruthless "
            "gatekeeper for your attention. It connects securely to your Google account and "
            "automatically classifies your incoming emails into four buckets: "
            "**Urgent**, **Needs Reply**, **FYI**, and **Ignore**."
        )
        
        st.markdown("### Inside the Engine")
        st.write("1. **Inbox & Triage:** AI analyzes context, intent, and urgency.")
        st.write("2. **Draft Generation:** AI instantly generates contextual, professional replies.")
        st.write("3. **Approval Gate:** Human-in-the-loop control. Nothing sends without your click.")
        st.write("4. **Smart Scheduling:** AI parses meeting requests and books them on your calendar.")

    with col2:
        st.info("🔐 Secure Google OAuth 2.0")
        
        # We only use HTML for the actual clickable button to ensure the redirect works
        st.markdown(
            f"""
            <a href="{auth_url}" target="_top" 
               style="display:block; text-align:center; padding:14px 24px; 
                      background-color:#FF4B4B; color:white; border-radius:8px; 
                      text-decoration:none; font-weight:bold; font-size: 1.1rem;
                      margin-top: 10px; margin-bottom: 10px;">
                🔑 Sign in with Google
            </a>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Click above to authenticate and begin.")
        
        st.write("---")
        st.markdown("### Architecture")
        st.caption("• **Core Logic:** Python\n"
                   "• **AI Engine:** Google Gemini 2.5 Flash\n"
                   "• **Infrastructure:** GCP & Streamlit Cloud\n"
                   "• **Integrations:** Gmail & Calendar API")
