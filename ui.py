import streamlit as st

def render_aurora_landing_page(auth_url: str) -> None:
    # --- CSS Injection ---
    st.markdown(
    """
    <style>
      /* Increase font-size for ALL body texts AND lists */
      p,
      .markdown-text,
      .element-container > div,
       ul li,  /* Unordered lists */ 
       ol li {  /* Ordered lists */  
          font-size: 27px !important;
       }
        /* The Aurora Background ... (rest of existing styles remain unchanged)*/

        .legal-links {
            color: #a5b4fc;
            text-decoration: none;
            margin-right: 2rem;
            font-weight: normal !important;   // overrides old style!
            font-size: inherit !important;     // uses default link size from page style first...
         }
         </style>
     """, unsafe_allow_html=True)

# HTML Structure Updated Below

st.markdown(
f"""
<div class="landing-wrapper"><div class="hero-section">...</div><div><a href="{auth_url}" target="_top" class="google-btn">🔑 Sign in with Google</a></div>...other cards remain unchanged...

<div><p>Note about API limits:</p></div>

<!-- NEW CLASS APPLIED HERE -->
<a href="https://github.com/sreekirthana123/Chief-Of-Staff-Application/blob/master/PRIVACY.md" target="_blank" rel="noopener noreferrer" style=color-inherit;line-height-inherit;"class=legal-links;">Privacy Policy</a><br>
<a href="https://github.com/sreekirthana123/Chief
