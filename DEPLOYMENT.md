# 🚀 Deployment Guide - Sprypt Chatbot

Complete step-by-step deployment instructions for all platforms.

## 📋 Pre-Deployment Checklist

- [ ] OpenAI API key ready
- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] `.env` file configured (locally only, don't commit!)
- [ ] CSV data files included in repository

---

## 🎯 Option 1: Render.com (RECOMMENDED - Easiest)

### Why Render?
- ✅ Free tier available
- ✅ Auto-deploys from GitHub
- ✅ Easy environment variable management
- ✅ Automatic HTTPS
- ✅ Great for Python apps

### Cost
- **Free tier**: Limited (sleeps after 15 mins of inactivity)
- **Paid**: $7/month per service (always-on)
- **Total for both services**: $14/month

### Step-by-Step Deployment

#### 1. Create Render Account
1. Go to [https://render.com](https://render.com)
2. Sign up with GitHub

#### 2. Deploy FastAPI Backend

1. **Click "New +"** → **"Web Service"**
2. **Connect Repository**: Select `Sprypt-chat-bot`
3. **Configure:**
   ```
   Name: sprypt-chatbot-api
   Environment: Python 3
   Branch: main
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn server:app --host 0.0.0.0 --port $PORT
   ```
4. **Add Environment Variable:**
   - Key: `OPENAI_API_KEY`
   - Value: `your-openai-api-key`
5. **Click "Create Web Service"**
6. **Wait for deployment** (5-10 minutes)
7. **Copy the URL** (e.g., `https://sprypt-chatbot-api.onrender.com`)

#### 3. Deploy Streamlit Frontend

1. **Click "New +"** → **"Web Service"**
2. **Connect Repository**: Select `Sprypt-chat-bot` again
3. **Configure:**
   ```
   Name: sprypt-chatbot-frontend
   Environment: Python 3
   Branch: main
   Build Command: pip install -r requirements.txt
   Start Command: streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
   ```
4. **Add Environment Variable:**
   - Key: `OPENAI_API_KEY`
   - Value: `your-openai-api-key`
5. **Click "Create Web Service"**
6. **Wait for deployment** (5-10 minutes)

#### 4. Update CORS

After deployment, update `server.py` line 18:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-streamlit-frontend.onrender.com"  # Add your Streamlit URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit and push:
```bash
git add server.py
git commit -m "Update CORS for production"
git push origin main
```

Render will auto-redeploy!

#### 5. Access Your Apps

- **API**: `https://sprypt-chatbot-api.onrender.com`
- **API Docs**: `https://sprypt-chatbot-api.onrender.com/docs`
- **Streamlit App**: `https://sprypt-chatbot-frontend.onrender.com`

---

## 🎯 Option 2: Railway.app

### Why Railway?
- ✅ Very simple setup
- ✅ $5 free credit/month
- ✅ Great developer experience
- ✅ Auto-deploys from GitHub

### Cost
- **Free**: $5/month credit (runs out in ~7-10 days for 2 services)
- **Paid**: ~$10-15/month for both services

### Step-by-Step Deployment

#### 1. Create Railway Account
1. Go to [https://railway.app](https://railway.app)
2. Sign up with GitHub

#### 2. Deploy Backend

1. **Click "New Project"**
2. **Deploy from GitHub repo**
3. **Select** `Sprypt-chat-bot`
4. **Add Variables:**
   - `OPENAI_API_KEY`: your-key
   - `PORT`: 8000
5. **Add Start Command:**
   ```
   uvicorn server:app --host 0.0.0.0 --port $PORT
   ```
6. **Deploy**
7. **Generate Domain** (Settings → Generate Domain)

#### 3. Deploy Frontend

1. **Click "New"** in same project
2. **Deploy from GitHub repo** (same repo)
3. **Add Variables:**
   - `OPENAI_API_KEY`: your-key
4. **Add Start Command:**
   ```
   streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```
5. **Deploy**
6. **Generate Domain**

---

## 🎯 Option 3: Streamlit Cloud + Render

### Split Deployment (Best Free Option)

**Streamlit Frontend** → Streamlit Cloud (FREE!)
**FastAPI Backend** → Render (Free tier)

#### 1. Deploy Backend on Render
Follow "Option 1" steps 1-2 above for backend only.

#### 2. Deploy Frontend on Streamlit Cloud

1. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
2. **Sign in with GitHub**
3. **Click "New app"**
4. **Configure:**
   ```
   Repository: koushals-sys/Sprypt-chat-bot
   Branch: main
   Main file path: app.py
   ```
5. **Advanced Settings** → **Secrets:**
   ```toml
   OPENAI_API_KEY = "your-openai-api-key"
   ```
6. **Deploy!**

**Cost**: FREE! (Both services on free tiers)

---

## 🎯 Option 4: Heroku

### Cost
- ❌ **No free tier**
- **Basic**: $7/month per dyno
- **Total**: $14/month for both services

### Deployment

1. **Install Heroku CLI**
```bash
brew install heroku/brew/heroku  # macOS
```

2. **Login**
```bash
heroku login
```

3. **Create Apps**
```bash
heroku create sprypt-chatbot-api
heroku create sprypt-chatbot-frontend
```

4. **Deploy Backend**
```bash
git push heroku main
heroku config:set OPENAI_API_KEY=your-key
```

5. **Deploy Frontend**
```bash
# Create separate Procfile for frontend
echo "web: streamlit run app.py --server.port \$PORT --server.address 0.0.0.0" > Procfile.frontend
git push heroku main
heroku config:set OPENAI_API_KEY=your-key
```

---

## 🎯 Option 5: Docker + Any Cloud

### Create Dockerfile

**backend.Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

**frontend.Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
```

### Docker Compose

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: backend.Dockerfile
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./chroma_db:/app/chroma_db

  frontend:
    build:
      context: .
      dockerfile: frontend.Dockerfile
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - backend
```

**Run:**
```bash
docker-compose up -d
```

---

## 📊 Cost Comparison

| Platform | Free Tier | Paid | Best For |
|----------|-----------|------|----------|
| **Render** | Yes (sleeps) | $14/mo | Production |
| **Railway** | $5 credit | $10-15/mo | Quick deploy |
| **Streamlit Cloud + Render** | Both FREE | $7/mo | Best free option |
| **Heroku** | None | $14/mo | Enterprise |
| **Docker on AWS/GCP** | Free trial | $10-30/mo | Full control |

---

## ✅ Post-Deployment Checklist

- [ ] Both services deployed successfully
- [ ] CORS updated with production URLs
- [ ] Environment variables set correctly
- [ ] API endpoint accessible
- [ ] Streamlit app working
- [ ] Test chatbot responses
- [ ] Vector store initialized
- [ ] Custom domain configured (optional)

---

## 🐛 Common Issues

### Issue: "Address already in use"
**Solution**: Render/Railway manages ports automatically. Don't hardcode ports.

### Issue: "OpenAI API key not found"
**Solution**: Add environment variable in platform settings

### Issue: "ChromaDB tenant error"
**Solution**: Delete and rebuild vector store (automatic on first run)

### Issue: "Module not found"
**Solution**: Verify `requirements.txt` is up to date

---

## 🔒 Security Best Practices

1. **Never commit `.env` file** (already in `.gitignore`)
2. **Use environment variables** for all secrets
3. **Rotate API keys regularly**
4. **Set up CORS properly** (don't use `"*"`)
5. **Enable HTTPS only** (automatic on Render/Railway)
6. **Monitor API usage** (OpenAI dashboard)

---

## 📈 Scaling Considerations

### When to Scale Up?

- More than 100 requests/day → Upgrade to paid tier
- Need faster response times → Upgrade instance size
- Multiple concurrent users → Add load balancing

### Optimization Tips

1. **Cache frequently asked questions**
2. **Use smaller embedding models** if cost is a concern
3. **Implement rate limiting**
4. **Add Redis for session management**
5. **Use GPT-4 only for complex questions**

---

## 🎓 Next Steps After Deployment

1. **Monitor performance** (Render/Railway dashboards)
2. **Set up custom domain** (optional)
3. **Add analytics** (Google Analytics, PostHog)
4. **Implement user feedback** mechanism
5. **A/B test different prompts**
6. **Add authentication** if needed

---

## 📞 Need Help?

- **Render Docs**: https://render.com/docs
- **Railway Docs**: https://docs.railway.app
- **Streamlit Cloud**: https://docs.streamlit.io/streamlit-community-cloud

---

**Happy Deploying! 🚀**
