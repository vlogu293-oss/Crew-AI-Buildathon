# CrewAI Customer Support System

A customer support system built with **CrewAI** and **Streamlit** using three sequential agents.

## Features

- Three CrewAI agents running sequentially.
- Agent 1 provides a direct answer.
- Agent 2 searches the web using Serper and provides a web-based answer.
- Agent 3 records the customer query and both answers.
- Results are displayed in the Streamlit UI.
- Each interaction is saved as a `.txt` file.
- API keys are loaded from environment variables.
- API keys are not hard-coded in the source code.

## Project Structure

```text
buildathon-support-crew/
│
├── .venv/
├── .env
├── .gitignore
├── app.py
├── requirements.txt
└── README.md
Technologies Used
Python
CrewAI
CrewAI Tools
Streamlit
Serper API
python-dotenv
Installation
1. Clone or create the project
mkdir buildathon-support-crew
cd buildathon-support-crew
2. Create a virtual environment
python -m venv .venv
3. Activate the virtual environment

On Windows:

.venv\Scripts\activate
4. Install dependencies
pip install -r requirements.txt
Environment Variables

Create a .env file in the project root:

OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key

Never hard-code API keys in app.py.

Never commit the .env file to Git.

.gitignore

Make sure .gitignore contains:

.env
.venv/
venv/
__pycache__/
*.pyc
support_record_*.txt
Running the Application

Start the Streamlit application:

streamlit run app.py

If you are using the .venv environment on Windows:

.venv\Scripts\python.exe -m streamlit run app.py

The application will open in your browser.

How It Works

The application uses CrewAI's sequential process:

                User Query
                    │
                    ▼
        ┌─────────────────────┐
        │     Agent 1          │
        │ Customer Support     │
        │ Direct Answer        │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │     Agent 2          │
        │   Web Research       │
        │ Serper Web Search    │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │     Agent 3          │
        │    Entry Agent       │
        │ Save Interaction     │
        └──────────┬──────────┘
                   │
                   ▼
          Text File + UI Output
Agents
Agent 1 — Customer Support Assistant

The first agent receives the user's query and answers it directly using its available knowledge.

It does not perform web searches.

Agent 2 — Web Research Customer Support Agent

The second agent receives the original query and the first agent's output.

It uses the Serper web-search tool to search for relevant information and produces a web-researched answer.

Agent 3 — Customer Support Entry Agent

The third agent receives the outputs of the previous agents.

It prepares the final interaction record containing:

Original customer query
Assistant Agent answer
Web Search Agent answer

The application saves these details into a .txt file.

Sequential Processing

The Crew is configured using:

process=Process.sequential

This ensures the agents execute in order:

Agent 1 → Agent 2 → Agent 3
Streamlit Interface

The UI contains:

Query/task input box
Run button
Assistant Answer section
Web Search Answer section
Support record download button
Output File

After a successful request, a text file is created similar to:

support_record_20260925_043000_123456.txt

The file contains:

============================================================
CUSTOMER SUPPORT RECORD
============================================================

Timestamp:
2026-09-25 04:30:00

------------------------------------------------------------
USER QUERY
------------------------------------------------------------

What is the difference between Python and Java?

------------------------------------------------------------
ASSISTANT AGENT ANSWER
------------------------------------------------------------

<Assistant Agent response>

------------------------------------------------------------
WEB SEARCH AGENT ANSWER
------------------------------------------------------------

<Web Search Agent response>

============================================================
END OF RECORD
============================================================
Example Questions

You can test the application with:

What is CrewAI and how does it work?
What is the difference between Python and Java?
How do I create a virtual environment in Python?
What are the latest features of Python 3.14?
What is Streamlit?
