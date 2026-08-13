import streamlit as st
import uuid
import os

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
    st.session_state.thread_id = str(uuid.uuid4())

if "uploaded_file_path" not in st.session_state:
    st.session_state.uploaded_file_path = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🤖 AI Data Analyst")

    st.markdown("---")

    # ========================================================
    # UPLOAD CSV
    # ========================================================

    st.subheader("📁 Upload CSV")

    uploaded_file = st.file_uploader(
        "Choose your CSV file",
        type=["csv"]
    )

    if uploaded_file is not None:

        os.makedirs("data", exist_ok=True)

        file_path = os.path.join(
            "data",
            uploaded_file.name
        )

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.session_state.uploaded_file_path = file_path

        st.success(
            f"✅ {uploaded_file.name}"
        )

    st.markdown("---")

    # ========================================================
    # FEATURES
    # ========================================================

    st.subheader("🛠️ Features")

    st.markdown(
        """
        📂 CSV Analysis

        🔍 Column Inspection

        🧹 Missing Values

        📊 Statistical Summary

        📈 Correlation Analysis

        👥 Churn Rate

        🤖 AI Data Questions
        """
    )

    st.markdown("---")

    # ========================================================
    # EXAMPLE QUESTIONS
    # ========================================================

    st.subheader("💡 Example Questions")

    st.markdown(
        """
        **Dataset**

        What columns are in my dataset?

        **Missing Values**

        Check missing values.

        **Statistics**

        Give me the statistical summary.

        **Churn**

        Calculate the churn rate.

        **Correlation**

        Show correlation between numerical variables.
        """
    )

    st.markdown("---")

    # ========================================================
    # PRINT CHAT
    # ========================================================

    st.subheader("🖨️ Chat")

    if st.button(
        "🖨️ Print Chat",
        use_container_width=True
    ):

        st.markdown(
            """
            <script>
                window.print();
            </script>
            """,
            unsafe_allow_html=True
        )

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

st.title("🤖 AI Data Analyst Agent")

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

        st.markdown(
            message["content"]
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
    # USER MESSAGE
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):

        st.markdown(user_input)


    # ========================================================
    # AGENT RESPONSE
    # ========================================================

    with st.chat_message("assistant"):

        with st.spinner(
            "🤖 Agent is analyzing..."
        ):

            try:

                # ------------------------------------------------
                # CSV PATH
                # ------------------------------------------------

                if st.session_state.uploaded_file_path:

                    message = f"""
The user uploaded this CSV file:

{st.session_state.uploaded_file_path}

User question:

{user_input}

Use this CSV file when dataset analysis is required.
"""

                else:

                    message = user_input


                # ------------------------------------------------
                # CALL BACKEND
                # ------------------------------------------------

                answer = chat(
                    message,
                    st.session_state.thread_id
                )


                # ------------------------------------------------
                # DISPLAY ANSWER
                # ------------------------------------------------

                st.markdown(answer)


                # ------------------------------------------------
                # SAVE ANSWER
                # ------------------------------------------------

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

                st.error(error)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error
                    }
                )