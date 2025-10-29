


# 🧠 Job Interview Roadmap Generator (LangChain + Gemini AI)

A multi-agent AI system built using **LangChain** and **Google Gemini API** that automatically analyzes job descriptions, extracts key skills, and builds a **structured interview preparation roadmap** customized for a specific **company and role**.

---

## 🚀 Overview

This project generates an **AI-powered interview preparation roadmap** by combining:
- **Job Description Parsing (JD Parser Agent)**
- **Company Process Insights (Company Agent)**
- **Study Plan & Skill Prioritization (Roadmap Builder Agent)**

It uses **Gemini-2.0-flash** (via LangChain) for reasoning and structured JSON outputs and integrates **DuckDuckGo Search API** for real-time company insights.

---

## 🧩 System Architecture

```

[User Input]
│
▼
┌──────────────────────┐
│ JDParser Agent       │
│ - Extracts key skills│
│ - Identifies role    │
└──────────────────────┘
│
▼
┌──────────────────────┐
│ Company Agent        │
│ - Searches company   │
│   interview process  │
│   via DuckDuckGo     │
└──────────────────────┘
│
▼
┌──────────────────────┐
│ Roadmap Builder Agent│
│ - Merges info        │
│ - Generates roadmap  │
│   JSON               │
└──────────────────────┘
│
▼
[Output: JSON Roadmap + Summary View]

````

---

## ⚙️ How the Agent Works

### 1. **Input Processing**
The user provides:
- `Company Name`
- `Role`
- `Full Job Description`

The input is passed into the **RoadmapGenerator** class.

### 2. **JD Parsing & Skill Extraction**
The system uses Gemini-2.0-flash through LangChain to:
- Identify **key skills**, tools, and domains mentioned in the job description.
- Estimate the **difficulty level** (Easy / Medium / Hard / Very Hard).
- Detect the **role category** (e.g., Backend Engineer, Data Analyst, Product Manager).

Example Extraction:
```json
{
  "key_skills": ["Python", "REST APIs", "Docker", "AWS"],
  "topic_count": 4
}
````

---

### 3. **Company Information Retrieval**

The **Company Agent** calls the **DuckDuckGo API** with smart search queries like:

* “Google Software Engineer interview process”
* “Google technical interview questions”

It extracts the most relevant summaries and related topics, merges them, and passes them to the next stage.

If DuckDuckGo search fails, it uses a **fallback template** based on standard hiring patterns.

---

### 4. **Roadmap Reasoning and Generation**

The **Roadmap Builder Agent** constructs a detailed, structured roadmap via Gemini reasoning.
It generates a JSON output containing:

* Company and role context
* List of interview rounds
* Topics to study for each round
* Recommended study order
* Extracted skills evidence from JD

Example output:

```json
{
  "company": "Google",
  "role": "SDE1",
  "rounds": [
    {"type": "Technical Screening", "topics": ["Data Structures", "Algorithms"]},
    {"type": "System Design", "topics": ["Scalability", "Database Design"]},
    {"type": "Behavioral", "topics": ["Leadership", "Communication"]}
  ],
  "difficulty": "Hard",
  "recommended_order": ["Data Structures", "Algorithms", "System Design", "Behavioral"],
  "evidence": {
    "key_skills": ["Python", "AWS", "Docker"],
    "topic_count": 3
  },
  "generated_at": "2025-10-28T15:45:00",
  "version": "1.0"
}
```

---

## 🧠 Reasoning Flow (Simplified)

| Step | Function                   | Description                                       |
| ---- | -------------------------- | ------------------------------------------------- |
| 1    | `generate_roadmap()`       | Orchestrates all steps and handles flow           |
| 2    | `search_company_info()`    | Uses DuckDuckGo to get company interview info     |
| 3    | `ChatGoogleGenerativeAI`   | Generates structured roadmap via Gemini reasoning |
| 4    | `extract_json_from_text()` | Cleans, validates, and parses AI output to JSON   |
| 5    | `save_roadmap()`           | Saves roadmap as `company_role_roadmap.json`      |

---

## 🧾 Output Example

```
============================================================
📊 ROADMAP SUMMARY
============================================================
🏢 Company: Google
💼 Role: SDE1
🎯 Difficulty: Hard
🔄 Total Rounds: 3

🔄 Interview Rounds:
  1. Technical Screening
     📚 Topics: Data Structures, Algorithms
  2. System Design
     📚 Topics: Scalability, Database Design
  3. Behavioral
     📚 Topics: Leadership, Communication

📖 Recommended Study Order: Data Structures, Algorithms, System Design, Behavioral
🔍 Key Skills from JD: Python, AWS, Docker
============================================================
```

---

## 📦 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/job-roadmap-agent.git
cd job-roadmap-agent
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # (Linux/macOS)
venv\Scripts\activate      # (Windows)
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the project root:

```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

> Get your free Gemini API key from:
> 🔗 [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

---

## 🧪 Run the Application

```bash
python agent.py
```

You’ll be prompted for:

* Company name
* Job role
* Job description (paste manually, end with Ctrl+Z on Windows)

The agent will generate and save:

```
💾 {company}_{role}_roadmap.json
```

---

## 📚 Requirements

```
langchain==0.1.0
langchain-google-genai==0.0.3
langchain-community==0.0.14
google-generativeai==0.3.2
python-dotenv==1.0.0
requests==2.31.0
```

---

## 🧩 Key Design Principles

✅ **Single LLM → Multi-agent logic**
The system uses structured functions (JDParser → CompanyAgent → RoadmapBuilder) instead of multiple LLM calls, optimizing cost and latency.

✅ **Robust JSON Enforcement**
Prompts explicitly request valid JSON with field validation to prevent malformed output.

✅ **Automatic Fallback**
If Gemini or API calls fail, a **default roadmap** is generated — ensuring the app always returns something useful.

✅ **Portable & API-key Safe**
No hardcoded keys — all credentials loaded securely from `.env`.

---

## 🧰 Future Extensions

* Add **SERP API** or **LangChain Tools** for richer company research.
* Integrate **Streamlit/Gradio** for UI.
* Support **multi-role batch JD parsing**.
* Add **resume-matching recommendations** using Gemini embeddings.

---

## 🧑‍💻 Author

**Abhay Maurya**

🔗 [GitHub Profile](https://github.com/abhay1maurya)

---


