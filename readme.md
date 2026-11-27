# CrewAI Examples & Multi-Agent Workflows

A practical collection of multi-agent systems and workflows built with [CrewAI](https://github.com/crewAIInc/crewAI). This repository covers foundational single-agent and multi-agent concepts up to advanced production patterns including declarative YAML configuration, custom guardrails, memory, and lifecycle hooks.

---

## 📁 Repository Structure

```text
CrewAI_Examples/
├── AI_Agents/
│   ├── config/
│   │   ├── agents.yaml            # Declarative agent roles, goals, and backstories
│   │   └── tasks.yaml             # Declarative task descriptions and expected outputs
│   └── deep_research_agent.py     # Advanced research crew (YAML configs, memory, guardrails, hooks)
├── Foundation/
│   ├── example.py                 # Single-agent workflow (YouTube Shorts Content Planner)
│   ├── multiagent_example.py      # Multi-agent research crew (Planner, Researcher, Fact Checker, Writer)
│   ├── assessment.py              # Automated Code Review & Security Analysis crew
│   ├── code_changes.txt           # Sample code diffs analyzed by the assessment crew
│   └── unittests.py               # Local testing harness for agents, tasks, and tools
├── utils.py                       # Helper utilities for loading environment variables & API keys
├── requirements.txt               # Python package dependencies
└── readme.md                      # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python**: 3.10 to 3.12 recommended
- **Conda** (optional but recommended)

### 2. Create and Activate Virtual Environment

Using Conda:
```powershell
conda create -n crewai-env python=3.12 -y
conda activate crewai-env
```

Or using standard Python `venv`:
```powershell
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On macOS / Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 🔑 Environment Configuration

Create a `.env` file in the project root directory:

```env
# Required for live LLM execution
OPENAI_API_KEY=your_openai_api_key_here

# Required for web search tools (depending on the example)
EXA_API_KEY=your_exa_api_key_here          # Used by multiagent_example.py and deep_research_agent.py
SERPER_API_KEY=your_serper_api_key_here    # Used by assessment.py

# Optional: Custom OpenAI model or base URLs
OPENAI_MODEL_NAME=gpt-4o-mini
```

> [!NOTE]
> **Course / Mock Testing Mode**:
> Several examples include `os.environ["CREWAI_TESTING"] = "true"`. This simulates API calls with mock responses without incurring API charges. To run with live OpenAI and search APIs, comment out or remove that line in the script.

---

## 🛠️ Code Examples & Workflows

### 1. Foundation: Single-Agent Content Planner
- **File**: [Foundation/example.py](file:///d:/code/CrewAI_Examples/Foundation/example.py)
- **Concept**: Basic Agent and Task initialization using the sequential process.
- **Workflow**:
  - **YouTube Shorts Micro-History Strategist**: Crafts a 1-week posting plan with 5 structured video blueprints formatted as JSON.
- **Run**:
  ```powershell
  python Foundation/example.py
  ```

---

### 2. Foundation: Multi-Agent Research Crew
- **File**: [Foundation/multiagent_example.py](file:///d:/code/CrewAI_Examples/Foundation/multiagent_example.py)
- **Concept**: Collaborative multi-agent pipeline using specialized tools.
- **Tools**: `EXASearchTool` (neural search) and `ScrapeWebsiteTool` (web page scraper).
- **Crew Composition**:
  1. **Research Planner**: Breaks the research prompt into focused investigation topics.
  2. **Internet Researcher**: Uses Exa search and web scraping to collect verified evidence.
  3. **Fact Checker**: Cross-references findings, spots discrepancies, and flags misinformation.
  4. **Report Writer**: Synthesizes verified data into an executive research report with actionable insights and citations.
- **Run**:
  ```powershell
  python Foundation/multiagent_example.py
  ```

---

### 3. Foundation: Automated Code & Security Review
- **File**: [Foundation/assessment.py](file:///d:/code/CrewAI_Examples/Foundation/assessment.py)
- **Concept**: Multi-agent code review pipeline with security checks and validation tests.
- **Tools**: `SerperDevTool` (configured for OWASP vulnerability lookups) and `ScrapeWebsiteTool`.
- **Crew Composition**:
  1. **Senior Developer**: Analyzes code quality, maintainability, and code structure.
  2. **Security Engineer**: Checks for vulnerabilities (SQL injection, XSS, insecure dependencies) against OWASP guidelines.
  3. **Tech Lead**: Synthesizes quality and security findings into a prioritized action plan.
- **Run**:
  ```powershell
  python Foundation/assessment.py
  ```

---

### 4. Advanced: Deep Research Agent with Guardrails & Memory
- **File**: [AI_Agents/deep_research_agent.py](file:///d:/code/CrewAI_Examples/AI_Agents/deep_research_agent.py)
- **Configuration**: [AI_Agents/config/agents.yaml](file:///d:/code/CrewAI_Examples/AI_Agents/config/agents.yaml) and [AI_Agents/config/tasks.yaml](file:///d:/code/CrewAI_Examples/AI_Agents/config/tasks.yaml)
- **Advanced Features**:
  - **YAML-driven configuration**: Keeps prompt engineering and backstories cleanly separated from Python code.
  - **Output Guardrails (`write_report_guardrail`)**: Validates that the report includes required sections (`## Summary`, `## Insights`, `## Citations`) before finishing.
  - **Crew Memory (`memory=True`)**: Enables conversational and contextual memory across tasks.
  - **Lifecycle Callbacks (`after_kickoff_callbacks`)**: Automatically persists the final markdown report to `research_report.md`.
- **Run**:
  ```powershell
  cd AI_Agents
  python deep_research_agent.py
  ```

---

## 🧩 Key CrewAI Concepts Demonstrated

| Feature | Where It's Used | Purpose |
| :--- | :--- | :--- |
| **Single-Agent Tasks** | `Foundation/example.py` | Direct prompt-to-task execution with structured outputs |
| **Multi-Agent Sequential Process** | `Foundation/multiagent_example.py` | Handing off structured deliverables across specialized agents |
| **Tool Integration** | `EXASearchTool`, `SerperDevTool`, `ScrapeWebsiteTool` | Giving agents live web search and scraping capabilities |
| **Declarative YAML Configs** | `AI_Agents/config/` | Clean architecture separating prompts from execution code |
| **Output Guardrails** | `AI_Agents/deep_research_agent.py` | Enforcing strict validation rules on task outputs |
| **Agent Memory** | `AI_Agents/deep_research_agent.py` | Maintaining cross-agent context throughout the run |
| **Kickoff Callbacks** | `save_file_hook` in `AI_Agents` | Exporting final deliverables to local files |

---

## 📄 License
This repository is for educational and experimental purposes.
