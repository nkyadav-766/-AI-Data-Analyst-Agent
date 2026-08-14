import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from tools import (
    load_csv,
    dataset_summary,
    get_column_info,
    calculate_churn_rate,
    get_correlation,
)

from system_message import SYSTEM_MESSAGE


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

import os

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

if not HUGGINGFACE_API_KEY:
    raise ValueError(
        "HUGGINGFACE_API_KEY is missing. "
        "Add it to your .env file."
    )


# ============================================================
# CREATE HUGGING FACE MODEL
# ============================================================

llm = HuggingFaceEndpoint(
    repo_id="openai/gpt-oss-20b",
    huggingfacehub_api_token=HUGGINGFACE_API_KEY,
    temperature=0,
    max_new_tokens=1024,
)

chat_model = ChatHuggingFace(
    llm=llm
)

# ============================================================
# TOOLS
# ============================================================

tools = [
    load_csv,
    dataset_summary,
    get_column_info,
    calculate_churn_rate,
    get_correlation,
]


# ============================================================
# MEMORY
# ============================================================

memory = InMemorySaver()


# ============================================================
# CREATE AGENT
# ============================================================

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_MESSAGE,
    checkpointer=memory,
)


# ============================================================
# CHAT FUNCTION
# ============================================================

def chat(user_message, thread_id="user-1"):

    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_message,
                }
            ]
        },
        config={
            "configurable": {
                "thread_id": thread_id
            }
        },
    )

    content = response["messages"][-1].content

    # Gemini can sometimes return content as a list
    if isinstance(content, list):

        text_parts = []

        for item in content:

            if isinstance(item, dict):

                if item.get("type") == "text":

                    text_parts.append(
                        item.get("text", "")
                    )

            elif isinstance(item, str):

                text_parts.append(item)

        return "\n".join(text_parts)

    return content


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("AI DATA ANALYST AGENT - GOOGLE GEMINI")
    print("=" * 60)

    print("\nAgent is ready.")
    print("Type 'exit' to stop.\n")

    while True:

        user_input = input("You: ")

        # Exit
        if user_input.lower().strip() == "exit":

            print("Agent: Goodbye!")

            break

        # Ignore empty input
        if not user_input.strip():

            continue

        try:

            answer = chat(user_input)

            print("\nAgent:")
            print(answer)
            print()

        except Exception as e:

            print("\nError:")
            print(e)
            print()