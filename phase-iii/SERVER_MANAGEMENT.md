# Phase-III Server Management Guide

## 🟢 Currently Running

Your phase-iii application is running with:
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000

## 🛑 How to Stop Servers

If you need to stop the servers:

### Stop All Background Tasks
```bash
# This will stop both backend and frontend
# (You'll need to identify the task IDs)
```

### Manual Stop
1. Find the processes:
   ```bash
   # Windows
   netstat -ano | findstr "8000"
   netstat -ano | findstr "3000"
   
   # Then kill by PID
   taskkill /PID <pid> /F
   ```

2. Or press `Ctrl+C` in the terminal where servers are running

## 🔄 How to Restart Servers

### Restart Backend
```bash
cd phase-iii/backend
.venv\Scripts\activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Restart Frontend
```bash
cd phase-iii/frontend
npm run dev
```

## 📊 Check Server Status

### Backend Health Check
```bash
curl http://localhost:8000/health
```

Expected response: `{"status":"healthy"}`

### Frontend Check
```bash
curl http://localhost:3000
```

Should return HTML content

### View API Documentation
Open in browser: http://localhost:8000/docs

## 🔍 Troubleshooting

### Port Already in Use
If you get "port already in use" error:

**Windows:**
```bash
# Find process using port 8000
netstat -ano | findstr "8000"

# Kill the process
taskkill /PID <pid> /F
```

### Backend Not Responding
1. Check if backend is running: `curl http://localhost:8000/health`
2. Check backend logs for errors
3. Verify .env file has correct configuration
4. Restart backend server

### Frontend Not Loading
1. Check if frontend is running: `curl http://localhost:3000`
2. Clear browser cache
3. Check .env.local has correct API URL
4. Restart frontend server

### CORS Errors
1. Verify backend .env has: `ALLOWED_ORIGINS=http://localhost:3000`
2. Restart backend server
3. Clear browser cache

## 📝 Logs

### View Backend Logs
Backend logs are displayed in the terminal where it's running

### View Frontend Logs
Frontend logs are displayed in the terminal where it's running

## 🧪 Testing

### Test Backend API
```bash
# Health check
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/00000000-0000-0000-0000-000000000001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

### Test Frontend
Open http://localhost:3000 in your browser

## 💡 Tips

- Keep both terminal windows open to see logs
- Use `--reload` flag for auto-restart on code changes
- Check logs if something doesn't work
- Use API docs at /docs to explore endpoints

## 🚀 Production Deployment

For production, you'll want to:
1. Use a production WSGI server (gunicorn)
2. Set DEBUG=False in backend
3. Build frontend: `npm run build`
4. Use a reverse proxy (nginx)
5. Set up SSL certificates
6. Use environment variables for secrets

## 📚 Additional Resources

- Backend API Docs: http://localhost:8000/docs
- Chat Commands: phase-iii/CHAT_COMMANDS.md
- Groq API Docs: https://console.groq.com/docs
