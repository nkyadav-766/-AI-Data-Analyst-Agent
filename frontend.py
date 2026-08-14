import streamlit as st
import uuid
import os
import re


from agent import chat


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Data Analyst Agent",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


if "thread_id" not in st.session_state:

    st.session_state.thread_id = str(
        uuid.uuid4()
    )


if "uploaded_file_path" not in st.session_state:

    st.session_state.uploaded_file_path = None


# ============================================================
# FUNCTION: EXTRACT CHART PATHS
# ============================================================

def extract_chart_paths(text):

    if not isinstance(
        text,
        str
    ):

        return []


    # Search for:
    #
    # CHART_GENERATED: charts/chart_xxxxx.png

    pattern = (
        r"CHART_GENERATED:\s*"
        r"([^\s]+\.png)"
    )


    paths = re.findall(
        pattern,
        text
    )


    valid_paths = []


    for path in paths:

        path = path.strip()

        path = path.rstrip(
            ".,);]}"
        )

        path = path.replace(
            "\\",
            os.sep
        )


        if os.path.exists(
            path
        ):

            valid_paths.append(
                path
            )


    return list(
        dict.fromkeys(
            valid_paths
        )
    )


# ============================================================
# FUNCTION: REMOVE CHART MARKER FROM TEXT
# ============================================================

def clean_answer(text):

    if not isinstance(
        text,
        str
    ):

        return str(text)


    cleaned = re.sub(
        r"CHART_GENERATED:\s*[^\s]+\.png",
        "",
        text
    )


    return cleaned.strip()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title(
        "🤖 AI Data Analyst"
    )

    st.markdown("---")


    # ========================================================
    # UPLOAD CSV
    # ========================================================

    st.subheader(
        "📁 Upload CSV"
    )


    uploaded_file = st.file_uploader(
        "Choose your CSV file",
        type=["csv"]
    )


    if uploaded_file is not None:

        os.makedirs(
            "data",
            exist_ok=True
        )


        file_path = os.path.join(
            "data",
            uploaded_file.name
        )


        with open(
            file_path,
            "wb"
        ) as f:

            f.write(
                uploaded_file.getbuffer()
            )


        st.session_state.uploaded_file_path = (
            file_path
        )


        st.success(
            f"✅ {uploaded_file.name}"
        )


    st.markdown("---")


    # ========================================================
    # FEATURES
    # ========================================================

    st.subheader(
        "🛠️ Features"
    )


    st.markdown(
        """
        📂 CSV Analysis

        🔍 Column Inspection

        🧹 Missing Values

        📊 Statistical Summary

        📈 Correlation Analysis

        👥 Churn Rate

        📊 Visualizations

        💬 AI Chat
        """
    )


    st.markdown("---")


    # ========================================================
    # EXAMPLE QUESTIONS
    # ========================================================

    st.subheader(
        "💡 Example Questions"
    )


    st.markdown(
        """
        **Chat**

        Hello, what can you do?

        **Dataset**

        What columns are in my dataset?

        **Statistics**

        Give me the statistical summary.

        **Churn**

        Calculate the churn rate.

        **Visualization**

        Generate a pie chart of churn.

        **Visualization**

        Generate a histogram of age.

        **Visualization**

        Create a scatter plot of balance vs estimated salary.

        **Text + Chart**

        Analyze churn and visualize it.
        """
    )


    st.markdown("---")


    # ========================================================
    # CLEAR CHAT
    # ========================================================

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.session_state.thread_id = str(
            uuid.uuid4()
        )

        st.rerun()


# ============================================================
# MAIN HEADER
# ============================================================

st.title(
    "🤖 AI Data Analyst Agent"
)


st.write(
    "Upload a CSV file and ask questions about your dataset."
)


# ============================================================
# FILE STATUS
# ============================================================

if st.session_state.uploaded_file_path:

    st.success(
        "📁 Dataset ready: "
        + os.path.basename(
            st.session_state.uploaded_file_path
        )
    )

else:

    st.info(
        "👈 Upload a CSV file from the sidebar."
    )


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        content = message["content"]


        # ----------------------------------------------------
        # DISPLAY TEXT
        # ----------------------------------------------------

        cleaned_content = clean_answer(
            content
        )


        if cleaned_content:

            st.markdown(
                cleaned_content
            )


        # ----------------------------------------------------
        # DISPLAY CHARTS
        # ----------------------------------------------------

        chart_paths = extract_chart_paths(
            content
        )


        for chart_path in chart_paths:

            st.image(
                chart_path,
                caption="📊 Generated Visualization",
                use_container_width=True
            )


            with open(
                chart_path,
                "rb"
            ) as chart_file:

                st.download_button(
                    label="⬇️ Download Chart",
                    data=chart_file.read(),
                    file_name=os.path.basename(
                        chart_path
                    ),
                    mime="image/png",
                    key=(
                        "history_"
                        + chart_path
                        + "_"
                        + str(
                            uuid.uuid4()
                        )
                    )
                )


# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input(
    "Ask your AI Data Analyst..."
)


# ============================================================
# PROCESS MESSAGE
# ============================================================

if user_input:

    # ========================================================
    # SAVE USER MESSAGE
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )


    # ========================================================
    # DISPLAY USER MESSAGE
    # ========================================================

    with st.chat_message(
        "user"
    ):

        st.markdown(
            user_input
        )


    # ========================================================
    # ASSISTANT
    # ========================================================

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "🤖 Agent is analyzing..."
        ):

            try:

                # ====================================================
                # BUILD MESSAGE
                # ====================================================

                if (
                    st.session_state
                    .uploaded_file_path
                ):

                    message = f"""
The user uploaded this CSV file:

{st.session_state.uploaded_file_path}

User question:

{user_input}

Use this CSV file when dataset analysis is required.

If the user requests a chart, visualization,
graph, plot, or image of the data,
use the generate_chart tool.
"""

                else:

                    message = user_input


                # ====================================================
                # CALL AGENT
                # ====================================================

                answer = chat(
                    message,
                    st.session_state.thread_id
                )


                # ====================================================
                # CLEAN TEXT
                # ====================================================

                cleaned_answer = clean_answer(
                    answer
                )


                # ====================================================
                # DISPLAY TEXT
                # ====================================================

                if cleaned_answer:

                    st.markdown(
                        cleaned_answer
                    )


                # ====================================================
                # FIND CHARTS
                # ====================================================

                chart_paths = extract_chart_paths(
                    answer
                )


                # ====================================================
                # DISPLAY CHARTS
                # ====================================================

                for chart_path in chart_paths:

                    st.image(
                        chart_path,
                        caption="📊 Generated Visualization",
                        use_container_width=True
                    )


                    with open(
                        chart_path,
                        "rb"
                    ) as chart_file:

                        st.download_button(
                            label="⬇️ Download Chart",
                            data=chart_file.read(),
                            file_name=os.path.basename(
                                chart_path
                            ),
                            mime="image/png",
                            key=(
                                "new_"
                                + str(
                                    uuid.uuid4()
                                )
                            )
                        )


                # ====================================================
                # SAVE ASSISTANT MESSAGE
                # ====================================================

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )


            except Exception as e:

                error = (
                    "❌ Error: "
                    + str(e)
                )


                st.error(
                    error
                )


                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error
                    }
                )