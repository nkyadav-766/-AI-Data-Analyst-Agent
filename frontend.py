import os
import uuid

import streamlit as st

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
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title(
        "🤖 AI Data Analyst"
    )

    st.markdown("---")


    # ========================================================
    # UPLOAD
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

📊 Visualizations

🧹 Data Cleaning

💡 Insights

🤖 AI Data Questions
"""
    )


    st.markdown("---")


    # ========================================================
    # EXAMPLES
    # ========================================================

    st.subheader(
        "💡 Example Questions"
    )

    st.markdown(
        """
**Summary**

Give me a summary of my dataset.

**Missing Values**

Show missing values.

**Statistics**

Give me important statistics.

**Visualization**

Create a histogram of study time.

**Visualization**

Create a bar chart of gender.

**Visualization**

Create a scatter plot of study time vs previous grade.

**Analysis**

What are the most important insights?
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
# HEADER
# ============================================================

st.title(
    "🤖 AI Data Analyst Agent"
)

st.write(
    "Upload a CSV file and ask questions "
    "about your dataset."
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

        # ----------------------------------------------------
        # TEXT
        # ----------------------------------------------------

        content = message.get(
            "content",
            ""
        )

        if content:

            st.markdown(
                content
            )


        # ----------------------------------------------------
        # CHARTS
        # ----------------------------------------------------

        charts = message.get(
            "charts",
            []
        )

        for chart_path in charts:

            if os.path.exists(
                chart_path
            ):

                st.image(
                    chart_path,
                    caption="📊 Generated Visualization",
                    use_container_width=True
                )


# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input(
    "Ask your AI Data Analyst..."
)


# ============================================================
# PROCESS USER MESSAGE
# ============================================================

if user_input:

    # ========================================================
    # USER MESSAGE
    # ========================================================

    user_message = {
        "role": "user",
        "content": user_input,
        "charts": []
    }

    st.session_state.messages.append(
        user_message
    )


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
            "🤖 Analyzing your data..."
        ):

            try:

                # =================================================
                # CREATE CLEAN INTERNAL MESSAGE
                # =================================================

                if st.session_state.uploaded_file_path:

                    message = (
                        "CSV_PATH="
                        + st.session_state.uploaded_file_path
                        + "\n\n"
                        + "USER_QUESTION="
                        + user_input
                    )

                else:

                    message = (
                        "USER_QUESTION="
                        + user_input
                    )


                # =================================================
                # CALL AGENT
                # =================================================

                result = chat(
                    message,
                    st.session_state.thread_id
                )


                # =================================================
                # GET RESPONSE
                # =================================================

                answer = result.get(
                    "text",
                    ""
                )

                charts = result.get(
                    "charts",
                    []
                )


                # =================================================
                # DISPLAY TEXT
                # =================================================

                if answer:

                    st.markdown(
                        answer
                    )


                # =================================================
                # DISPLAY CHARTS
                # =================================================

                for chart_path in charts:

                    if os.path.exists(
                        chart_path
                    ):

                        st.image(
                            chart_path,
                            caption="📊 Generated Visualization",
                            use_container_width=True
                        )

                    else:

                        st.warning(
                            "Generated chart file "
                            "could not be found."
                        )


                # =================================================
                # SAVE RESPONSE
                # =================================================

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "charts": charts
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
                        "content": error,
                        "charts": []
                    }
                )