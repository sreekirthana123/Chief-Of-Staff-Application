<div align="center">
  <p>🚀 Built with Passion by</p>
  <h2>V Sree Kirthana</h2>
</div>

# 👑 Chief of Staff AI

**Intelligent Triage & Autonomous Scheduling for your Inbox.**  
[🔗 Access the Live App Here](https://sree-kirthana-chief-of-staff.streamlit.app)

Chief of Staff AI is a fully functional AI agent that acts as a ruthless gatekeeper for your attention. It connects securely to your Google account and automatically classifies your incoming emails into four buckets: Urgent, Needs Reply, FYI, and Ignore, while intelligently drafting responses and managing your calendar.

---
## ✨ Features

*   **📥 Automated Inbox Triage** — Categorizes incoming emails into Urgent (🔴), Needs Reply (⚪), FYI (🟢), and Ignore (⚫) based on deep NLP contextual analysis.
*   **✍️ Contextual Draft Generation** — Instantly crafts tailored, professional response drafts for actionable messages to eliminate manual typing time.
*   **📅 Smart Calendar Scheduling** — Automatically detects meeting requests, verifies Google Calendar availability, and schedules confirmed events upon approval.
*   **🛡️ Human-in-the-Loop Gate** — Zero unapproved outbound emails. Users can Regenerate, Edit, or Approve every draft before it hits the outbox.
*   **🎨 Dual-UI Architecture** — Features a stunning Aurora Glassmorphism landing page and transitions into a high-contrast, low-fatigue dashboard (Earth/Cream tones) optimized for heavy text reading.
*   **📊 Audit Export** — Generates clean "Proof of Work" reports in Markdown or HTML for record-keeping and workflow tracking.
---

## 🛠 Tech Stack

* **Framework:** Streamlit (Custom Aurora Glassmorphism UI)
* **AI/LLM:** Google Gemini 2.5 Flash
* **Processing:** Gmail API & Google Calendar API (OAuth 2.0 Web Flow)
* **Deployment:** Streamlit Community Cloud

---

## 📂 Project Structure

* **`app.py`**: The main entry point; manages the Streamlit UI, OAuth 2.0 authentication flow, and the four-phase dashboard pipeline (Triage, Drafts, Approval, Export).
* **`engine.py`**: The core logic engine; securely fetches live email threads and interfaces with Gemini 2.5 Flash to analyze intent, assign priority, and route data.
* **`ui.py`**: The frontend module; houses the custom CSS (including the Aurora gradients and dark mode themes) and renders the structured landing page.
* **`approval_gate.py`**: Manages the Human-in-the-Loop UI, rendering side-by-side drafts and handling the logic for Regenerating, Editing, or Approving emails.
* **`draft_machine.py`**: The dedicated AI module that constructs strict prompts for Gemini to generate highly contextual, professional email responses.
* **`calendar_engine.py`**: Interfaces with the Google Calendar API to parse meeting requests, check availability, and autonomously schedule events.
* **`context_builder.py`**: Processes raw email threads and historical data to build accurate, token-efficient context windows for the LLM.
* **`SRS - Chief of Staff AI.pdf`**: The official Software Requirements Specification document detailing system architecture, data flow, and functional requirements.
* **`PRIVACY.md` & `TERMS.md`**: Legal documentation explicitly outlining the Human-in-the-Loop security model, data handling protocols, and user terms.
* **`DEPLOYMENT.md`**: Technical documentation outlining the steps, architecture, and environment variables required to deploy the application to production.
* **`requirements.txt`**: Lists all Python dependencies and external libraries required to run the application.
* **`action_log.json`**: A local storage file that maintains a secure audit trail of all system actions, triage decisions, and errors.
* **`approved_drafts.json`**: Temporary local database that securely holds drafts that have passed human approval before final dispatch.
* **`past_replies.json`**: Stores historical communication data to provide the LLM with few-shot examples to better mimic the user's personal writing style.
* **`emails.txt`**: A temporary local text file used for logging raw email payloads during the extraction phase.
* **`.streamlit/`**: Configuration directory holding the application's Streamlit-specific theme overrides and server settings.
* **`Gmail-MCP-Server/`**: Backend directory containing server configurations for advanced Gmail Model Context Protocol integration.
---
``
## ⚙️ System Pipeline (The 4 Phases)

```text
  Live Inbox (Gmail API)
           ↓
  Phase 1: Triage & Classification
  (Context, Intent, Urgency Extraction via Gemini)
           ↓
  ┌─────────────────────┐      ┌────────────────────────┐
  │  🔴 Urgent          │      │  ⚪ Needs Reply        │
  │  (High Priority)    │      │  (Standard Priority)   │
  └────────┬────────────┘      └──────────┬─────────────┘
           └──────────────┬───────────────┘
                          ↓
  Phase 2: Draft Generation
  (Gemini 2.5 Flash contextual prompt engineering)
                          ↓
  Phase 3: Human-in-the-Loop Approval Gate
  (Streamlit UI: Render side-by-side drafts)
           ↓              ↓               ↓
      [Regenerate]      [Edit]        [Approve]
           │              │               │
           └──────────────┴───────────────┤
                                          ↓
                               Phase 4: Execution
                  (Dispatch via Gmail API, Sync to Calendar)
---
```
## 🗺️ Development Roadmap (Spiral Model)

* ✅ **Phase 1** — GCP Project Setup & OAuth 2.0 Authentication Flow
* ✅ **Phase 2** — Gmail API Integration (Thread extraction & parsing)
* ✅ **Phase 3** — Gemini Prompt Engineering (Triage logic & Draft generation)
* ✅ **Phase 4** — Frontend Dashboard Construction (Streamlit state management)
* ✅ **Phase 5** — Human-in-the-Loop implementation (Approve/Edit/Regenerate routing)
* ✅ **Phase 6** — Dual-UI Styling (Aurora landing page + High-contrast dashboard)
* ✅ **Phase 7** — Google Calendar API Integration & Audit Export
* 🔄 **Phase 8** — Upgrade to paid-tier LLM for higher rate limits (Upcoming)
```
```
``
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
## 🧠 Why Gemini 2.5 Flash & Human-in-the-Loop?

### ⚡ The Engine: Gemini 2.5 Flash
Traditional LLMs often struggle with long email threads, either forgetting earlier messages due to context limits or taking too long to generate responses. Gemini 2.5 Flash was explicitly chosen for this architecture because of:
* **Ultra-Low Latency:** Triage classification and draft generation happen in seconds, ensuring the pipeline doesn't bottleneck when processing a high volume of unread emails.
* **Massive Context Window:** The agent can easily ingest deeply nested, months-long email chains without hallucinating past details or losing the core thread context.
* **Cost-to-Performance Ratio:** It delivers high-tier reasoning and contextual understanding at a fraction of the compute cost, making it ideal for a high-frequency automation tool.

### 🛡️ The Safety Net: Human-in-the-Loop (HITL)
Connecting a fully autonomous, unchecked AI to a personal or corporate inbox is a massive security risk. This system was built from the ground up around a strict **Human-in-the-Loop (HITL)** security model:
* **AI as an Assistant, Not a Replacement:** The AI does 95% of the heavy lifting—reading, analyzing, prioritizing, and typing. 
* **Absolute Executive Authority:** The human does the final 5%. The system physically cannot dispatch an email or finalize a calendar event without explicit human click-approval.
* **Zero Hallucination Risk:** If the AI misunderstands the nuance of an email, the user can instantly click **Regenerate** to try again, or manually **Edit** the draft. Mistakes do not make it to the outbox.
```
---
```
## Inside the app
<img width="1920" height="960" alt="Screenshot (1546)" src="https://github.com/user-attachments/assets/ac29c617-8b35-4b24-b682-7bdeda9f806d" />

<img width="1920" height="975" alt="Screenshot (1530)" src="https://github.com/user-attachments/assets/413cc212-b767-4bf7-8ada-6a446afdeb91" />

---
---
```
```
## 📬 Connect & Share Feedback

I’d love to hear your thoughts on Chief of Staff AI! Whether it’s a feature suggestion, a bug report, or just general feedback, your input helps make this project better.

* **Connect with me:** [My LinkedIn Profile](https://www.linkedin.com/in/v-sree-kirthana-565b4a367)
* **Share Feedback:** [Create a GitHub Issue](https://github.com/sreekirthana123/Chief-Of-Staff-Application/issues)
---
## 👩‍💻 Author

**V Sree Kirthana** <br>
B.Tech CSE — JBIET, Hyderabad | 2nd Year <br>
AI/ML Engineer in process <br>
sreekeerthana64@gmail.com <br><br>
*Built with curiosity, caffeine, and a lot of debugging ☕🔥*

---
## 📜 License

&copy; 2026 V. Sree Kirthana. All rights reserved.  
This project was developed as part of a project.  
Unauthorized reproduction or distribution is not permitted without explicit consent from the author.
