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
         body {
             background-color: #0f172a;
             color: white;   // text color!
         }

        h1,h2,h3,h4 {
            color:#ffffff !important; // header colors!
            text-align:center;
        }

        a.google-btn{
            padding-top :5px;
            padding-bottom :5px;
           width :30rem ;    
           margin-top :4rem ;
           border-radius:8px;

         }
          div.hero-section img {
              width:"100%";
              height:"auto";    

          }
           .features-card{
               display:flex!important;

               flex-direction=row!important;

                justify-content="space-between"!

                 gap="2rem"

                   margin-bottom=5em!

                  align-items-center!

                  max-width="80vw"
                  padding-left='3em'
                   padding-right='3em'

                    box-shadow:'none'

                     background-color="#fffbfe"

                      border-radius:"16 px "
                       overflow-hidden ! important


                         transition:'box-shadow ease-out duration -[ ']./assets/blur.png',""}

                        </style>""", unsafe_allow_html=True)

# HTML Structure Updated Below

st.markdown(f"""
<div class="landing-wrapper">
   <div class="hero-section">
     <img src="./assets/aurora-blurred.png" alt="">
    
