from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from chatbot_logic import initialize_chatbot, ask_question

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Sprypt.com FAQ Chatbot API",
    description="RAG-based chatbot API for Sprypt.com FAQs",
    version="1.0.0"
)

# Enable CORS for localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Global variable to store the chatbot instance
qa_chain = None


# Request model
class ChatRequest(BaseModel):
    question: str

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is Sprypt?"
            }
        }


# Response model
class ChatResponse(BaseModel):
    answer: str
    sources: list = []

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Sprypt is a company that...",
                "sources": ["Source 1: ...", "Source 2: ..."]
            }
        }


@app.on_event("startup")
async def startup_event():
    """
    Initialize the chatbot when the server starts.
    """
    global qa_chain

    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found in environment variables!")
        print("Please add your API key to the .env file")
        return

    print("Initializing chatbot...")
    try:
        qa_chain = initialize_chatbot()
        print("Chatbot initialized successfully!")
    except Exception as e:
        print(f"Error initializing chatbot: {str(e)}")
        qa_chain = None


@app.get("/")
async def root():
    """
    Root endpoint - API health check.
    """
    return {
        "message": "Sprypt.com FAQ Chatbot API",
        "status": "running",
        "chatbot_ready": qa_chain is not None
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - accepts a question and returns an answer.

    Args:
        request: ChatRequest containing the user's question

    Returns:
        ChatResponse containing the answer and source documents

    Raises:
        HTTPException: If chatbot is not initialized or an error occurs
    """
    # Check if chatbot is initialized
    if qa_chain is None:
        raise HTTPException(
            status_code=503,
            detail="Chatbot is not initialized. Please check server logs."
        )

    # Validate question
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        # Get answer from chatbot
        response = ask_question(qa_chain, request.question)

        # Extract source documents
        sources = []
        if response.get("source_documents"):
            for i, doc in enumerate(response["source_documents"], 1):
                source_text = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                sources.append(f"Source {i}: {source_text}")

        return ChatResponse(
            answer=response["answer"],
            sources=sources
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "chatbot_initialized": qa_chain is not None,
        "api_key_configured": bool(os.getenv("OPENAI_API_KEY"))
    }


if __name__ == "__main__":
    import uvicorn

    print("Starting Sprypt.com FAQ Chatbot API...")
    print("API will be available at: http://localhost:8000")
    print("API docs will be available at: http://localhost:8000/docs")

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes
    )
