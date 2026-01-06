import streamlit as st
import requests
import json

# Backend API URL
API_URL = "https://sprypt-chatbot-api.onrender.com/api/chat"

# Set page configuration
st.set_page_config(
    page_title="Sprypt.com FAQ Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar configuration
st.sidebar.title("⚙️ Configuration")
st.sidebar.markdown("---")
st.sidebar.success("✅ Connected to Sprypt API")

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "This chatbot uses your Sprypt.com FAQ data to answer questions. "
    "It only provides answers based on the provided context and will not hallucinate information."
)

st.sidebar.markdown("### Data Sources")
st.sidebar.text("📄 Firefiles to FAQ - Final Sheet.csv")
st.sidebar.text("📄 Firefiles to FAQ - Feature Focus.csv")
st.sidebar.text("🌐 Sprypt.com Website")

st.sidebar.markdown("---")
st.sidebar.markdown("### Helpful Links")
st.sidebar.markdown("🎯 [Book a Demo](https://www.sprypt.com/demo)")
st.sidebar.markdown("💡 [Support Center](https://help.sprypt.com/)")

st.sidebar.markdown("---")
# Clear chat button
if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

# Main chat interface
st.title("🤖 Sprypt.com FAQ Chatbot")
st.markdown("Ask me anything about Sprypt.com!")
st.markdown("---")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Display sources if available
        if message["role"] == "assistant" and "sources" in message and message["sources"]:
            with st.expander("📚 View Sources"):
                for i, source in enumerate(message["sources"], 1):
                    st.markdown(f"**{source[:200]}...**" if len(source) > 200 else f"**{source}**")
                    if i < len(message["sources"]):
                        st.markdown("---")

# Chat input
if prompt := st.chat_input("Type your question here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Call backend API
                response = requests.post(
                    API_URL,
                    json={"question": prompt},
                    timeout=120  # 2 minute timeout
                )

                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "Sorry, I couldn't generate a response.")
                    sources = data.get("sources", [])

                    # Display the answer
                    st.markdown(answer)

                    # Display sources in expander
                    if sources:
                        with st.expander("📚 View Sources"):
                            for i, source in enumerate(sources, 1):
                                st.markdown(f"**{source[:200]}...**" if len(source) > 200 else f"**{source}**")
                                if i < len(sources):
                                    st.markdown("---")

                    # Add assistant message to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                else:
                    error_message = f"❌ API Error: {response.status_code} - {response.text}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})

            except requests.exceptions.Timeout:
                error_message = "❌ Request timed out. The server might be initializing. Please try again in a moment."
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})
            except Exception as e:
                error_message = f"❌ Error: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Powered by OpenAI, LangChain, and ChromaDB | Built with Streamlit"
    "</div>",
    unsafe_allow_html=True
)
