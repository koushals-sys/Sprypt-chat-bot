import streamlit as st
import os
from chatbot_logic import initialize_chatbot, ask_question
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Sprypt.com FAQ Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None

if "chatbot_initialized" not in st.session_state:
    st.session_state.chatbot_initialized = False


# Sidebar configuration
st.sidebar.title("⚙️ Configuration")
st.sidebar.markdown("---")

# Check if API key is loaded from .env
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    st.sidebar.success("✅ API Key loaded from .env file")

    # Initialize chatbot if not already done
    if not st.session_state.chatbot_initialized:
        with st.spinner("Initializing chatbot... This may take a moment on first run."):
            try:
                st.session_state.qa_chain = initialize_chatbot()
                st.session_state.chatbot_initialized = True
                st.sidebar.success("✅ Chatbot initialized!")
            except Exception as e:
                st.sidebar.error(f"❌ Error initializing chatbot: {str(e)}")
else:
    st.sidebar.error("❌ OpenAI API Key not found in .env file")
    st.sidebar.info("Please add your API key to the .env file")

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "This chatbot uses your Sprypt.com FAQ data to answer questions. "
    "It only provides answers based on the provided context and will not hallucinate information."
)

st.sidebar.markdown("### Data Sources")
st.sidebar.text("📄 Firefiles to FAQ - Final Sheet.csv")
st.sidebar.text("📄 Firefiles to FAQ - Feature Focus .csv")
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

# Chat input
if prompt := st.chat_input("Type your question here..."):
    # Check if chatbot is initialized
    if not st.session_state.chatbot_initialized:
        st.error("⚠️ Chatbot is still initializing. Please wait...")
    else:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response from chatbot
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = ask_question(st.session_state.qa_chain, prompt)
                    answer = response["answer"]

                    # Display the answer
                    st.markdown(answer)

                    # Optionally display source documents in an expander
                    if response["source_documents"]:
                        with st.expander("📚 View Source Documents"):
                            for i, doc in enumerate(response["source_documents"], 1):
                                st.markdown(f"**Source {i}:**")
                                st.text(doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content)
                                st.markdown("---")

                    # Add assistant message to chat history
                    st.session_state.messages.append({"role": "assistant", "content": answer})

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
