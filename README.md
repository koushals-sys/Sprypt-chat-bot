# 🤖 Sprypt.com RAG Chatbot

An intelligent FAQ chatbot for Sprypt.com built with RAG (Retrieval-Augmented Generation) technology. Provides accurate, context-aware answers about Sprypt's features, pricing, and services.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-yellow.svg)](https://python.langchain.com/)

## 🌟 Features

- 💬 **Conversational AI**: Natural, human-like responses using GPT-3.5-turbo
- 📚 **RAG Technology**: Retrieves accurate information from FAQ documents and website content
- 🎯 **Context-Aware**: Understands follow-up questions and maintains conversation flow
- 🔍 **Multi-Source Knowledge**: Combines FAQ data with Sprypt.com website information
- 🚀 **FastAPI Backend**: High-performance REST API for scalability
- 🎨 **Streamlit Frontend**: Beautiful, user-friendly chat interface
- 🔗 **Helpful Links**: Direct access to demo booking and support center

## 🏗️ Tech Stack

### Backend
- **Framework**: FastAPI
- **LLM**: OpenAI GPT-3.5-turbo
- **Embeddings**: OpenAI text-embedding-ada-002
- **Vector Database**: ChromaDB (local)
- **RAG Framework**: LangChain
- **Server**: Uvicorn (ASGI)

### Frontend
- **Framework**: Streamlit
- **State Management**: Streamlit session state
- **UI Components**: Native Streamlit widgets

### Data Processing
- **CSV Processing**: Pandas
- **Text Splitting**: LangChain text splitters
- **Environment**: python-dotenv

## 📁 Project Structure

```
Sprypt_bot/
├── app.py                              # Streamlit frontend
├── server.py                           # FastAPI backend
├── chatbot_logic.py                    # RAG logic & vector store
├── requirements.txt                    # Python dependencies
├── .env                                # Environment variables (not in git)
├── .env.example                        # Environment template
├── .gitignore                          # Git ignore rules
├── sprypt_website_content.txt          # Website knowledge base
├── Firefiles to FAQ - Final Sheet.csv  # Primary FAQ data
├── Firefiles to FAQ - Feature Focus.csv # Additional FAQ data
└── chroma_db/                          # Vector store (auto-generated)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- OpenAI API key
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/koushals-sys/Sprypt-chat-bot.git
cd Sprypt-chat-bot
```

2. **Create virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

**.env file:**
```env
OPENAI_API_KEY=your-openai-api-key-here
```

### Running Locally

#### Option 1: Run Both Services

**Terminal 1 - FastAPI Backend:**
```bash
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Streamlit Frontend:**
```bash
streamlit run app.py
```

**Access:**
- FastAPI Backend: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Streamlit App: http://localhost:8501

#### Option 2: Run Only FastAPI (API-only mode)

```bash
python -m uvicorn server:app --reload
```

Test with cURL:
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Sprypt?"}'
```

## 📡 API Endpoints

### POST `/api/chat`

Send a question and receive an AI-generated answer.

**Request:**
```json
{
  "question": "What are the main features of Sprypt?"
}
```

**Response:**
```json
{
  "answer": "Sprypt offers several key features including...",
  "sources": [
    "Source 1: AI Scribe for efficient documentation...",
    "Source 2: Cloud-based appointment dashboard..."
  ]
}
```

### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "chatbot_initialized": true,
  "api_key_configured": true
}
```

## 🌐 Deployment

### Deploy to Render (Recommended)

#### Backend Deployment

1. **Create new Web Service on Render**
2. **Connect your GitHub repository**
3. **Configure:**
   - **Name**: `sprypt-chatbot-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Add Environment Variable**: `OPENAI_API_KEY=your-key`

#### Frontend Deployment

1. **Create new Web Service on Render**
2. **Connect your GitHub repository**
3. **Configure:**
   - **Name**: `sprypt-chatbot-app`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
   - **Add Environment Variable**: `OPENAI_API_KEY=your-key`

### Deploy to Vercel (Frontend Only)

Not recommended for Python apps. Use Render instead.

### Deploy to Railway

1. **Install Railway CLI**
```bash
npm install -g @railway/cli
```

2. **Deploy**
```bash
railway login
railway init
railway up
```

## 🔧 Configuration

### CORS Settings

Update `server.py` to allow your frontend domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Vector Store

The chatbot automatically creates a ChromaDB vector store on first run. To rebuild:

```bash
rm -rf chroma_db/
# Restart the application
```

## 📚 Data Sources

The chatbot uses three knowledge sources:

1. **Firefiles to FAQ - Final Sheet.csv**: Primary FAQ document
2. **Firefiles to FAQ - Feature Focus.csv**: Additional feature information
3. **sprypt_website_content.txt**: Website content as fallback

## 🎨 Customization

### Modify System Prompt

Edit `chatbot_logic.py` line 169:

```python
template = """You are a friendly Sprypt chatbot assistant..."""
```

### Adjust Temperature (Creativity)

Edit `chatbot_logic.py` line 151:

```python
def create_retrieval_chain(vectorstore, temperature=0.7):
    # Higher = more creative, Lower = more deterministic
```

### Change Number of Retrieved Documents

Edit `chatbot_logic.py` line 209:

```python
search_kwargs={"k": 5}  # Retrieve 5 documents
```

## 🐛 Troubleshooting

### ChromaDB Tenant Error

```bash
rm -rf chroma_db/
# Restart the application
```

### OpenAI API Key Not Found

Ensure `.env` file exists and contains:
```env
OPENAI_API_KEY=your-actual-key
```

### Port Already in Use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 8501
lsof -ti:8501 | xargs kill -9
```

### Module Not Found Errors

```bash
pip install -r requirements.txt --upgrade
```

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is private and proprietary to Sprypt.com.

## 🔗 Links

- [Sprypt Website](https://www.sprypt.com/)
- [Book a Demo](https://www.sprypt.com/demo)
- [Support Center](https://help.sprypt.com/)

## 👨‍💻 Author

**Koushal Shekhawat**
- GitHub: [@koushals-sys](https://github.com/koushals-sys)

## 🙏 Acknowledgments

- OpenAI for GPT-3.5-turbo
- LangChain for RAG framework
- Streamlit for the frontend framework
- FastAPI for the backend framework

---

**Built with ❤️ for Sprypt.com**
