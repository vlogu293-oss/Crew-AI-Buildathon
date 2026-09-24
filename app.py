import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool


# ============================================================
# Configuration
# ============================================================

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Fail early with a useful message instead of exposing keys.
if not OPENAI_API_KEY:
    st.error(
        "OPENAI_API_KEY is not configured. "
        "Please add it to your environment variables or .env file."
    )
    st.stop()

if not SERPER_API_KEY:
    st.error(
        "SERPER_API_KEY is not configured. "
        "Please add it to your environment variables or .env file."
    )
    st.stop()

# CrewAI / OpenAI reads this environment variable.
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["SERPER_API_KEY"] = SERPER_API_KEY


# ============================================================
# Streamlit UI
# ============================================================

st.set_page_config(
    page_title="CrewAI Customer Support",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 CrewAI Customer Support System")
st.write(
    "Ask a question or give the system a task. "
    "Three agents will process it sequentially."
)

st.info(
    "Workflow: Assistant Agent → Web Search Agent → Entry Agent"
)

query = st.text_area(
    "Enter your query or task",
    placeholder="Example: What is CrewAI and how is it different from LangChain?",
    height=150,
)

run_button = st.button(
    "🚀 Run Support System",
    type="primary",
    use_container_width=True,
)


# ============================================================
# Helper functions
# ============================================================

def get_task_output_text(task_output):
    """
    Safely convert a CrewAI TaskOutput to a string.
    """
    if task_output is None:
        return ""

    if hasattr(task_output, "raw"):
        return str(task_output.raw)

    return str(task_output)


def save_support_record(user_query, assistant_answer, web_answer):
    """
    Save the query and both agent answers into a text file.
    A new file is created for every request.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    filename = f"support_record_{filename_timestamp}.txt"

    content = f"""
============================================================
CUSTOMER SUPPORT RECORD
============================================================

Timestamp:
{timestamp}

------------------------------------------------------------
USER QUERY
------------------------------------------------------------

{user_query}

------------------------------------------------------------
ASSISTANT AGENT ANSWER
------------------------------------------------------------

{assistant_answer}

------------------------------------------------------------
WEB SEARCH AGENT ANSWER
------------------------------------------------------------

{web_answer}

============================================================
END OF RECORD
============================================================
"""

    with open(filename, "w", encoding="utf-8") as file:
        file.write(content.strip())

    return filename


# ============================================================
# Run CrewAI workflow
# ============================================================

if run_button:

    if not query.strip():
        st.warning("Please enter a query or task.")
        st.stop()

    with st.spinner("Running the three-agent support system..."):

        try:

            # ------------------------------------------------
            # Web search tool
            # ------------------------------------------------

            web_search_tool = SerperDevTool()


            # ------------------------------------------------
            # AGENT 1 — Assistant Agent
            # ------------------------------------------------

            assistant_agent = Agent(
                role="Customer Support Assistant",
                goal=(
                    "Answer the customer's query directly, clearly, "
                    "accurately, and helpfully without performing web searches."
                ),
                backstory=(
                    "You are the first-line customer support assistant. "
                    "You provide a useful answer using your existing knowledge. "
                    "Keep the response relevant to the customer's request."
                ),
                verbose=True,
                allow_delegation=False,
            )


            # ------------------------------------------------
            # AGENT 2 — Web Search Agent
            # ------------------------------------------------

            web_agent = Agent(
                role="Web Research Customer Support Agent",
                goal=(
                    "Search the web for information relevant to the customer's "
                    "query and provide a clear answer based on the information "
                    "you find."
                ),
                backstory=(
                    "You are a customer-support research specialist. "
                    "You use web search to verify and supplement information. "
                    "Your answer should directly address the original customer "
                    "query and distinguish useful facts from uncertainty."
                ),
                tools=[web_search_tool],
                verbose=True,
                allow_delegation=False,
            )


            # ------------------------------------------------
            # AGENT 3 — Entry Agent
            # ------------------------------------------------

            entry_agent = Agent(
                role="Customer Support Entry Agent",
                goal=(
                    "Record the original customer query and the answers from "
                    "the Assistant Agent and Web Search Agent into a text file, "
                    "then return both answers."
                ),
                backstory=(
                    "You are the final customer-support records agent. "
                    "You receive the original query and the previous agents' "
                    "answers. Your job is to make sure the complete interaction "
                    "is saved as a text record and that both answers are returned "
                    "for display to the customer."
                ),
                verbose=True,
                allow_delegation=False,
            )


            # =================================================
            # TASK 1 — Direct answer
            # =================================================

            assistant_task = Task(
                description=f"""
                Answer the following customer query directly.

                CUSTOMER QUERY:
                {query}

                Requirements:
                - Answer the query clearly.
                - Do not use web search.
                - Do not ask another agent for help.
                - Give a complete, useful answer.
                """,
                expected_output=(
                    "A clear and complete answer to the customer's query."
                ),
                agent=assistant_agent,
            )


            # =================================================
            # TASK 2 — Web search answer
            # =================================================

            web_task = Task(
                description=f"""
                Research the following customer query using the web search tool.

                CUSTOMER QUERY:
                {query}

                You are the second agent in a sequential workflow.

                First, perform web searches relevant to the customer's query.
                Then provide your own answer based on the information found.

                You may use the first agent's answer as additional context, "
                "but independently research the query.

                Requirements:
                - Use the web search tool.
                - Answer the ORIGINAL customer query.
                - Clearly summarize useful findings.
                - Do not simply repeat the first agent's answer.
                """,
                expected_output=(
                    "A web-researched answer to the original customer query."
                ),
                agent=web_agent,
                context=[assistant_task],
            )


            # =================================================
            # TASK 3 — Save record + return both answers
            # =================================================

            entry_task = Task(
                description=f"""
                You are the final Entry Agent.

                ORIGINAL CUSTOMER QUERY:
                {query}

                The first agent produced an answer and the second agent "
                "produced a web-researched answer.

                Your job is to:

                1. Preserve the original customer query.
                2. Preserve the Assistant Agent answer.
                3. Preserve the Web Search Agent answer.
                4. Make sure all three pieces of information are recorded "
                   "for the support interaction.
                5. Return BOTH answers clearly in your final output.

                IMPORTANT:
                The Streamlit application will save the final interaction "
                "to a .txt file after this task completes.

                Your final output must contain:

                ASSISTANT ANSWER:
                <first agent answer>

                WEB SEARCH ANSWER:
                <second agent answer>
                """,
                expected_output=(
                    "The original query context plus both the Assistant Agent "
                    "answer and Web Search Agent answer, clearly separated."
                ),
                agent=entry_agent,
                context=[assistant_task, web_task],
            )


            # =================================================
            # Create sequential Crew
            # =================================================

            crew = Crew(
                agents=[
                    assistant_agent,
                    web_agent,
                    entry_agent,
                ],
                tasks=[
                    assistant_task,
                    web_task,
                    entry_task,
                ],
                process=Process.sequential,
                verbose=True,
            )


            # =================================================
            # Execute
            # =================================================

            result = crew.kickoff()


            # =================================================
            # Extract individual task outputs
            # =================================================

            assistant_answer = get_task_output_text(
                assistant_task.output
            )

            web_answer = get_task_output_text(
                web_task.output
            )


            # =================================================
            # Save query + both answers
            # =================================================

            saved_filename = save_support_record(
                user_query=query,
                assistant_answer=assistant_answer,
                web_answer=web_answer,
            )


            # =================================================
            # Display results
            # =================================================

            st.success(
                f"Support request completed successfully. "
                f"Record saved as `{saved_filename}`."
            )

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🤖 Assistant Answer")
                st.markdown(assistant_answer)

            with col2:
                st.subheader("🌐 Web Search Answer")
                st.markdown(web_answer)


            # ------------------------------------------------
            # Show saved record download
            # ------------------------------------------------

            with open(saved_filename, "rb") as file:
                st.download_button(
                    label="📄 Download Support Record",
                    data=file,
                    file_name=saved_filename,
                    mime="text/plain",
                    use_container_width=True,
                )


        except Exception as error:

            st.error("The support workflow failed.")

            st.exception(error)

