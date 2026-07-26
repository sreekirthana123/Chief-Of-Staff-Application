<div align="center">
  <p>🚀 Built with Passion by</p>
  <h2>V Sree Kirthana</h2>
</div>

# 👑 Chief of Staff AI

**Intelligent Triage & Autonomous Scheduling for your Inbox.**  
[🔗 Access the Live App Here](https://sree-kirthana-chief-of-staff.streamlit.app)

Chief of Staff AI is a fully functional AI agent that acts as a ruthless gatekeeper for your attention. It connects securely to your Google account and automatically classifies your incoming emails into four buckets: Urgent, Needs Reply, FYI, and Ignore, while intelligently drafting responses and managing your calendar.

---

## 🛠 Tech Stack

* **Framework:** Streamlit (Custom Aurora Glassmorphism UI)
* **AI/LLM:** Google Gemini 2.5 Flash
* **Processing:** Gmail API & Google Calendar API (OAuth 2.0 Web Flow)
* **Deployment:** Streamlit Community Cloud

---

## 📂 Project Structure

* **`app.py`:** The main entry point; manages the Streamlit UI, OAuth 2.0 authentication flow, and the four-phase dashboard pipeline (Triage, Drafts, Approval, Export).
* **`engine.py`:** The core logic engine; securely fetches live email threads and interfaces with Gemini 2.5 Flash to analyze intent, assign priority, and generate professional drafts.
* **`ui.py`:** The frontend module; houses the custom CSS (including White Glassmorphism and Aurora gradients) and renders the structured landing page.
* **`PRIVACY.md` & `TERMS.md`:** Documentation explicitly outlining the Human-in-the-Loop security model and data handling protocols.

---

## 📂 Folder Structure

```text
Chief-Of-Staff-Application/
├── .streamlit/             # App configuration (theme settings)
├── app.py                  # Main Streamlit dashboard UI & routing
├── engine.py               # AI triage, drafting, and Google API logic
├── ui.py                   # Custom CSS styling and landing page structure
├── requirements.txt        # Project dependencies (Streamlit, Google Auth, etc.)
├── PRIVACY.md              # Privacy Policy 
└── TERMS.md                # Terms & Conditions
---
```
## Inside the app
<img width="1920" height="920" alt="Screenshot (1529)" src="https://github.com/user-attachments/assets/48fdab39-cd2a-440a-92d5-3c80e0e1df7b" />

---

## 📬 Connect & Share Feedback

I’d love to hear your thoughts on Chief of Staff AI! Whether it’s a feature suggestion, a bug report, or just general feedback, your input helps make this project better.

* **Connect with me:** [My LinkedIn Profile](https://www.linkedin.com/in/v-sree-kirthana-565b4a367)
* **Share Feedback:** [Create a GitHub Issue](https://github.com/sreekirthana123/Chief-Of-Staff-Application/issues)
---

``
## 📜 License

&copy; 2026 V. Sree Kirthana. All rights reserved.  
This project was developed as part of a project.  
Unauthorized reproduction or distribution is not permitted without explicit consent from the author.
