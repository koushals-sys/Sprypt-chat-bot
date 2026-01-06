import os
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def load_and_process_csv(csv_path):
    """
    Load CSV file and convert it to documents.

    Args:
        csv_path (str): Path to the CSV file

    Returns:
        list: List of Document objects
    """
    # Read the CSV file
    df = pd.read_csv(csv_path)

    # Convert each row to a document
    documents = []
    for index, row in df.iterrows():
        # Combine all column values into a single text
        text_parts = []
        for col in df.columns:
            if pd.notna(row[col]):
                text_parts.append(f"{col}: {row[col]}")

        text = "\n".join(text_parts)
        documents.append(Document(page_content=text, metadata={"row": index}))

    return documents


def load_website_content(website_file="sprypt_website_content.txt"):
    """
    Load website content as fallback knowledge source.

    Args:
        website_file (str): Path to the website content file

    Returns:
        list: List of Document objects
    """
    documents = []

    if os.path.exists(website_file):
        with open(website_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split website content into sections based on headers
        sections = content.split('\n## ')

        for i, section in enumerate(sections):
            if section.strip():
                # Add back the header marker for sections after the first
                if i > 0:
                    section = '## ' + section

                documents.append(Document(
                    page_content=section.strip(),
                    metadata={"source": "website", "section": i}
                ))

        print(f"Loaded {len(documents)} sections from website content")
    else:
        print(f"Warning: Website content file '{website_file}' not found. Proceeding without fallback data.")

    return documents


def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    """
    Split documents into smaller chunks.

    Args:
        documents (list): List of Document objects
        chunk_size (int): Size of each chunk
        chunk_overlap (int): Overlap between chunks

    Returns:
        list: List of split documents
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )

    splits = text_splitter.split_documents(documents)
    return splits


def create_vector_store(documents, persist_directory="./chroma_db"):
    """
    Create embeddings and store them in ChromaDB.

    Args:
        documents (list): List of Document objects
        persist_directory (str): Directory to persist the vector store

    Returns:
        Chroma: ChromaDB vector store
    """
    # Initialize OpenAI embeddings
    embeddings = OpenAIEmbeddings()

    # Create and persist the vector store
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )

    return vectorstore


def load_vector_store(persist_directory="./chroma_db"):
    """
    Load an existing vector store from disk.

    Args:
        persist_directory (str): Directory where the vector store is persisted

    Returns:
        Chroma: ChromaDB vector store
    """
    try:
        embeddings = OpenAIEmbeddings()

        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )

        return vectorstore
    except Exception as e:
        print(f"Error loading existing vector store: {e}")
        print("Will create a new vector store instead.")
        return None


def create_retrieval_chain(vectorstore, temperature=0.7):
    """
    Create a retrieval chain that answers questions based on the vector store.

    Args:
        vectorstore: ChromaDB vector store
        temperature (float): Temperature for the LLM (0.7 = more natural/conversational)

    Returns:
        RetrievalQA: Question-answering chain
    """
    # Initialize the LLM with higher temperature for more natural, conversational responses
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=temperature
    )

    # Define the system prompt
    template = """You are a friendly Sprypt chatbot assistant. Chat naturally with users like a helpful colleague would - be warm, conversational, and personable.

CONVERSATION STYLE:
- For greetings (hi, hello, hey): Respond warmly and briefly, then ask how you can help. Example: "Hi there! 👋 I'm here to help you learn about Sprypt. What would you like to know?"
- For casual questions: Keep responses natural and conversational, not overly formal
- For simple questions: Give concise, clear answers (2-3 sentences)
- For complex questions: Provide detailed explanations with specific information
- Use a friendly, approachable tone - imagine chatting with a colleague over coffee
- Avoid corporate jargon or overly formal language
- Be helpful and enthusiastic without being over-the-top

The context includes information from:
1. Internal FAQ documents (primary source - most detailed and specific)
2. Sprypt.com website content (fallback source - general information)

CRITICAL RULES:
1. Answer ONLY using the information from the provided context below
2. Prioritize information from FAQ documents when available
3. Use website content to supplement or provide general information when FAQ doesn't have the answer
4. If the answer is not in ANY of the provided context, respond naturally: "Hmm, I don't have that information in my knowledge base right now. But I can direct you to our support team who can help! Check out: https://help.sprypt.com/"
5. Do NOT make up information or hallucinate facts
6. Do NOT use external knowledge - stick to the context only

ANSWER GUIDELINES:
1. Match your response length to the question type:
   - Greetings/casual: Brief and friendly
   - Simple questions: Concise (2-3 sentences)
   - Detailed questions: Comprehensive (4-5+ sentences with specifics)
2. When comparing products, explain differences conversationally with specific features
3. Include relevant details, features, statistics from the context
4. Use natural language - contractions, simple words, conversational phrases
5. Break up long answers with bullet points or clear structure when helpful
6. When using website information, share key stats and features naturally

SPECIAL RESPONSES:
- If someone asks about booking/scheduling a demo: "I'd love to help you see Sprypt in action! You can book a demo here: https://www.sprypt.com/demo"
- If someone needs technical support: "For technical questions, our support team has you covered: https://help.sprypt.com/"
- For "thank you": Respond warmly like "You're welcome! Happy to help! Let me know if you have any other questions."

Context: {context}

Question: {question}

Answer naturally:"""

    PROMPT = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )

    # Create the retrieval chain with more documents to include both FAQ and website content
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}  # Retrieve more docs to include both FAQ and website
        ),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )

    return qa_chain


def initialize_chatbot(csv_paths=None,
                       persist_directory="./chroma_db",
                       force_reload=False):
    """
    Initialize the chatbot by loading data and creating the retrieval chain.

    Args:
        csv_paths (str or list): Path to CSV file(s). Can be a single path or list of paths
        persist_directory (str): Directory to persist the vector store
        force_reload (bool): If True, reload data even if vector store exists

    Returns:
        RetrievalQA: Question-answering chain
    """
    # Default CSV files if none specified
    if csv_paths is None:
        csv_paths = [
            "Firefiles to FAQ - Final Sheet.csv",
            "Firefiles to FAQ - Feature Focus .csv"
        ]

    # Convert single path to list for uniform processing
    if isinstance(csv_paths, str):
        csv_paths = [csv_paths]

    # Check if vector store already exists
    vectorstore = None
    if os.path.exists(persist_directory) and not force_reload:
        print("Loading existing vector store...")
        vectorstore = load_vector_store(persist_directory)

    # If vector store doesn't exist or failed to load, create a new one
    if vectorstore is None:
        print("Creating new vector store...")

        # Load and process all CSV files
        all_documents = []
        for csv_path in csv_paths:
            print(f"Loading {csv_path}...")
            documents = load_and_process_csv(csv_path)
            all_documents.extend(documents)
            print(f"  Loaded {len(documents)} documents from {csv_path}")

        print(f"Total CSV documents loaded: {len(all_documents)}")

        # Load website content as fallback knowledge source
        print("Loading website content as fallback source...")
        website_docs = load_website_content()
        all_documents.extend(website_docs)

        print(f"Total documents (CSV + Website): {len(all_documents)}")

        # Split documents into chunks
        splits = split_documents(all_documents)
        print(f"Split into {len(splits)} chunks")

        # Create vector store
        vectorstore = create_vector_store(splits, persist_directory)
        print("Vector store created and persisted")

    # Create retrieval chain
    qa_chain = create_retrieval_chain(vectorstore)
    print("Chatbot initialized successfully!")

    return qa_chain


def ask_question(qa_chain, question):
    """
    Ask a question to the chatbot and get an answer.

    Args:
        qa_chain: Question-answering chain
        question (str): User's question

    Returns:
        dict: Dictionary containing the answer and source documents
    """
    result = qa_chain({"query": question})
    return {
        "answer": result["result"],
        "source_documents": result["source_documents"]
    }


if __name__ == "__main__":
    # Example usage
    print("Initializing chatbot...")
    qa_chain = initialize_chatbot()

    # Test with a sample question
    test_question = "What is Sprypt?"
    print(f"\nQuestion: {test_question}")

    response = ask_question(qa_chain, test_question)
    print(f"Answer: {response['answer']}")
    print(f"\nNumber of source documents: {len(response['source_documents'])}")
