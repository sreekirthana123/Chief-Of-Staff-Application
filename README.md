# Chief of Staff AI: Intelligent Triage & Autonomous Scheduling

An end-to-end AI agent project exploring autonomous inbox management, leveraging advanced LLMs to evaluate email context, identify priority levels, automatically draft contextual responses, and manage calendar scheduling via Google Workspace APIs.

### Project Access & Resources
* **Live Interactive Application:** [View Live App Here](#) *(Replace with your Streamlit link)*
* **Architecture Documentation:** [View Privacy Policy & Terms](PRIVACY.md)
* **GitHub Repository:** [Access Source Code](#)

---

### Problem Statement

Professionals and executives frequently struggle with severe inbox overload, where critical communications are buried under newsletters, low-priority updates, and spam. Manually triaging emails, drafting repetitive responses, and cross-referencing availability for meeting requests consumes hours of high-value time.

This project solves these challenges by leveraging **Google Gemini 2.5 Flash** to execute automated data extraction, intent analysis, and response generation, paired with an interactive **Streamlit Dashboard** utilizing a secure, Human-in-the-Loop "Approval Gate" to ensure total user control over outbound communications and calendar events.

---

### Phase 1: Inbox & Triage

To process live communications, the system connects to the user's Google Workspace to pull active email threads and uses AI to transform unstructured inbox data into prioritized, structured categories.

* **Process:** Utilizes the Gmail API via OAuth 2.0 to securely fetch active unread threads.
* **AI Integration:** Passes thread text to Gemini 2.5 Flash to analyze the context, intent, and urgency of every message.
* **Classification Validation:** Automatically assigns a strict priority bucket to each thread: **Urgent (🔴)**, **Needs Reply (⚪)**, **FYI (🟢)**, and **Ignore (⚫)**.

---

### Phase 2: Draft Generation

Analyzes the context of actionable emails to instantly generate highly relevant, professional responses, reducing manual typing time to zero.

* **The "Brain":** Evaluates the specific request or question within threads flagged as *Urgent* or *Needs Reply*.
* **Response Generation:** Interfaces with the Gemini AI Engine to formulate a contextual draft tailored to the tone of the original message.
* **Graceful Handling:** Implements robust error handling for API rate limits to ensure continuous operation.

---

### Phase 3: Approval Gate (Human-in-the-Loop)

This analysis breaks down the generated drafts and presents them in an interactive dashboard, ensuring no automated actions occur without explicit consent.

* **Total Control:** Displays original email threads side-by-side with the AI-generated drafts.
* **Actionable Options:** Provides the user with three distinct controls for every draft: *Regenerate*, *Edit*, or *Approve*.
* **Secure Dispatch:** Dispatches emails directly to the recipient via the Gmail API only after the user clicks "Send" on an approved draft. Mistakes do not make it to the outbox.

---

### Phase 4: Smart Calendar Scheduling & Export Proof

This phase evaluates temporal requests and manages the logic required to keep the user's schedule organized and auditable.

* **Automated Scheduling:** The AI parses incoming emails for meeting requests or proposed times, cross-references availability, and autonomously books the event directly onto **Google Calendar**.
* **Export Proof:** Maintains a complete audit trail of the AI's work, allowing the user to download a full Proof of Work report as a cleanly formatted Markdown (`.md`) or HTML (`.html`) file.

---

### Strategic Recommendations & Action Plan

Based on the AI triage logic and response generation capabilities, the following core productivity strategies are automated by the system:

**Attention & Focus Optimization:**
* **Energy Allocation:** By filtering out *FYI* and *Ignore* emails, maximum mental resources are conserved for high-stakes, *Urgent* communications.
* **Automated Delegation:** Repetitive scheduling and standard reply tasks are fully delegated to the AI engine, acting as a true Chief of Staff.

**Security & Workflow Allocation:**
* Prioritize human oversight by strictly adhering to the Phase 3 Approval Gate.
* Maintain consistent adherence to secure OAuth 2.0 Web Flow practices, ensuring email data is processed in temporary session states rather than stored permanently.

---

### Technical Tool Stack & Development Workflow

* **Python & Google Gemini 2.5 Flash:** Applied for intelligent text parsing, intent classification, and contextual response generation—utilizing advanced prompting logic to execute multi-layered triage calculations.
* **Streamlit (Custom Aurora UI):** Leveraged for the main entry point, managing user interactions, authentication flows, and dynamic UI rendering using a custom "White Glassmorphism" CSS framework.
* **Google Cloud Platform (GCP):** Utilized for cloud infrastructure, managing the OAuth 2.0 Web Flow (PKCE), and handling API quotas.
* **External Integrations:** Gmail API and Google Calendar API cross-validated against user consent scopes to execute read/write operations securely.

---

### Conclusion

This project demonstrates an end-to-end AI automation workflow, turning a chaotic inbox into a streamlined, prioritized task list. 

By combining Google Workspace APIs with the dynamic reasoning capabilities of Gemini 2.5 Flash, the project provides a structured, secure approach to inbox management—highlighting urgent needs, generating immediate drafts, and booking meetings autonomously. The findings offer a strong foundation for supporting data-driven decisions in personal productivity and executive time management.

---

### Future Work

* **Expanded Model Upgrades:** Upgrading from free-tier AI APIs to paid enterprise models to handle significantly higher daily token throughput and avoid rate-limiting.
* **Tone Personalization:** Incorporating few-shot learning by ingesting the user's sent folder to match their exact writing style and vocabulary dynamically.
* **Predictive Analytics:** Exploring forecasting models to estimate peak email volume days and preemptively block out "focus time" on the user's calendar.
