import os
import re

from dotenv import load_dotenv

from langchain_huggingface import (
    HuggingFaceEndpoint,
    ChatHuggingFace
)

from langchain.agents import create_agent

from langgraph.checkpoint.memory import InMemorySaver

from tools import (
    load_csv,
    dataset_summary,
    get_column_info,
    get_missing_values,
    calculate_churn_rate,
    get_correlation,
    generate_chart,
)

from system_message import SYSTEM_MESSAGE


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

HUGGINGFACE_API_KEY = os.getenv(
    "HUGGINGFACE_API_KEY"
)

if not HUGGINGFACE_API_KEY:

    raise ValueError(
        "HUGGINGFACE_API_KEY is missing."
    )


# ============================================================
# MODEL
# ============================================================

llm = HuggingFaceEndpoint(
    repo_id="openai/gpt-oss-20b",
    huggingfacehub_api_token=HUGGINGFACE_API_KEY,
    temperature=0,
    max_new_tokens=2048,
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
    get_missing_values,
    calculate_churn_rate,
    get_correlation,
    generate_chart,
]


# ============================================================
# MEMORY
# ============================================================

memory = InMemorySaver()


# ============================================================
# AGENT
# ============================================================

agent = create_agent(
    model=chat_model,
    tools=tools,
    system_prompt=SYSTEM_MESSAGE,
    checkpointer=memory,
)


# ============================================================
# EXTRACT CHART PATH
# ============================================================

def extract_chart_paths(messages):

    charts = []

    for message in messages:

        content = getattr(
            message,
            "content",
            ""
        )

        if not isinstance(
            content,
            str
        ):

            continue

        matches = re.findall(
            r"CHART_PATH:(.+)",
            content
        )

        for path in matches:

            path = path.strip()

            if path not in charts:

                charts.append(path)

    return charts


# ============================================================
# CLEAN RESPONSE
# ============================================================

def clean_response(text):

    if not text:

        return ""

    # Remove internal chart path markers
    text = re.sub(
        r"CHART_PATH:.*",
        "",
        text
    )

    # Remove accidental internal instructions
    text = re.sub(
        r"The user uploaded this CSV file:.*",
        "",
        text,
        flags=re.DOTALL
    )

    text = re.sub(
        r"User question:.*",
        "",
        text,
        flags=re.DOTALL
    )

    text = text.strip()

    return text


# ============================================================
# CHAT
# ============================================================

def chat(
    user_message,
    thread_id="user-1"
):

    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        },
        config={
            "configurable": {
                "thread_id": thread_id
            }
        },
    )

    messages = response.get(
        "messages",
        []
    )

    if not messages:

        return {
            "text": "No response generated.",
            "charts": []
        }

    # ========================================================
    # CHARTS
    # ========================================================

    charts = extract_chart_paths(
        messages
    )

    # ========================================================
    # FINAL MESSAGE
    # ========================================================

    final_content = messages[-1].content

    if isinstance(
        final_content,
        str
    ):

        answer = final_content

    elif isinstance(
        final_content,
        list
    ):

        text_parts = []

        for item in final_content:

            if isinstance(
                item,
                str
            ):

                text_parts.append(item)

            elif isinstance(
                item,
                dict
            ):

                text = item.get(
                    "text",
                    ""
                )

                if text:

                    text_parts.append(
                        text
                    )

        answer = "\n".join(
            text_parts
        )

    else:

        answer = str(
            final_content
        )

    answer = clean_response(
        answer
    )

    return {
        "text": answer,
        "charts": charts
    }


# ============================================================
# TERMINAL TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("AI DATA ANALYST AGENT")
    print("=" * 60)

    print()
    print("Agent is ready.")
    print("Type 'exit' to stop.")
    print()

    while True:

        user_input = input(
            "You: "
        )

        if user_input.lower().strip() == "exit":

            print(
                "Agent: Goodbye!"
            )

            break

        if not user_input.strip():

            continue

        try:

            result = chat(
                user_input
            )

            print()
            print("Agent:")
            print(
                result["text"]
            )

            if result["charts"]:

                print()
                print(
                    "Charts:"
                )

                for chart in result["charts"]:

                    print(
                        chart
                    )

            print()

        except Exception as e:

            print()
            print(
                "Error:"
            )

            print(e)

            print()