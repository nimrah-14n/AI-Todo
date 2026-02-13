# Phase III Todo AI Chatbot - Quick Start Guide

## ✅ Setup Status: COMPLETE + TOOL CALLING ENABLED

All dependencies installed and configured. **Tool calling integration is now fully functional!**

### 🎉 What's New (February 8, 2026)

**Critical Update:** The AI agent now **actually executes MCP tools** to manage tasks!

- ✅ Agent can create tasks in the database
- ✅ Agent can list and filter tasks
- ✅ Agent can complete tasks
- ✅ Agent can delete tasks
- ✅ Agent can update task details
- ✅ Multi-turn tool calling (agent can call multiple tools in sequence)

**See:** `TOOL_CALLING_IMPLEMENTATION.md` for technical details

---

## 🔑 STEP 1: Verify Your Groq API Configuration (ALREADY CONFIGURED)

**File:** `phase-iii/backend/.env`

**Current configuration:**
```
OPENAI_API_KEY=gsk_your_groq_api_key_here
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.3-70b-versatile
```

✅ **Already configured to use Groq API with Llama 3.3 70B model**

**Get your Groq API key:** https://console.groq.com/keys

---

## 🚀 STEP 2: Start Backend Server

**Open Terminal 1** and run these commands:

```bash
cd C:\Users\ALCL\Desktop\ai-cloud-hackathon-2\phase-iii\backend
.venv\Scripts\activate
uvicorn src.api.chat:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Backend URL:** http://localhost:8000

---

## 🎨 STEP 3: Start Frontend Server

**Open Terminal 2** (keep Terminal 1 running) and run:

```bash
cd C:\Users\ALCL\Desktop\ai-cloud-hackathon-2\phase-iii\frontend
npm run dev
```

**Expected output:**
```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
- event compiled client and server successfully
```

**Frontend URL:** http://localhost:3000

---

## 🌐 STEP 4: Open in Browser

Navigate to: **http://localhost:3000**

You'll see the Todo AI Chatbot interface!

---

## 💬 Try These Commands

Once the chat interface loads, try:

### Create Tasks
- "Add a task to buy groceries"
- "Create a reminder to call mom tomorrow"
- "I need to finish the report by Friday"

### View Tasks
- "Show me all my tasks"
- "List my incomplete tasks"
- "What do I need to do?"

### Complete Tasks
- "Mark 'buy groceries' as complete"
- "I finished the report"
- "Done with calling mom"

### Delete Tasks
- "Delete the groceries task"
- "Remove the reminder about mom"

### Update Tasks
- "Change 'buy groceries' to 'buy groceries and snacks'"
- "Update the report task description to include deadline"

---

## 🔧 Troubleshooting

### Backend won't start
- ❌ **Missing API key**: Add your Groq API key to `.env`
- ❌ **Port in use**: Kill process on port 8000 or use different port
- ❌ **Database error**: Check Phase II database is accessible

### Frontend won't start
- ❌ **Port in use**: Kill process on port 3000 or use different port
- ❌ **Dependencies**: Run `npm install` again

### Chat not working
- ❌ **Backend not running**: Check Terminal 1 for errors
- ❌ **API key invalid**: Verify your Groq API key has credits
- ❌ **CORS error**: Check browser console, backend should allow localhost:3000

---

## 📊 What You'll See

### Chat Interface Features
✅ Clean, modern UI with purple theme
✅ Message history with user/assistant bubbles
✅ Real-time typing indicator
✅ Optimistic updates (messages appear instantly)
✅ Error handling with rollback
✅ Conversation persistence

### Backend Features
✅ Natural language processing via Groq (Llama 3.3 70B)
✅ 5 MCP tools for task management
✅ Rate limiting (60 req/min)
✅ Input sanitization
✅ Comprehensive logging
✅ Metrics collection

---

## 💰 Cost Note

**Groq API Usage:**
- Each message uses Llama 3.3 70B tokens
- Groq offers fast inference with competitive pricing
- Make sure your Groq account has credits
- Check pricing: https://console.groq.com/settings/limits

---

## 🎯 Quick Test Checklist

After starting both servers:

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:3000
- [ ] Can access chat interface in browser
- [ ] Can send a message: "Hello"
- [ ] **Can create a task: "Add a task to test the app"** ← Tool calling!
- [ ] **Can list tasks: "Show me all my tasks"** ← Tool calling!
- [ ] **Can see the task in the response** ← Actual database query!
- [ ] **Can complete task: "Mark the test task as done"** ← Tool calling!
- [ ] **Can verify in database that task was created/updated** ← Real persistence!

### 🧪 Verify Tool Calling Works

**Option 1: Run automated test**
```bash
cd phase-iii/backend
python test_tool_calling.py
```

**Option 2: Check backend logs**
When you send "Add a task to buy groceries", you should see:
```
INFO: Executing tool: add_task with args: {'title': 'Buy groceries'}
INFO: Tool add_task executed successfully in 0.123s
```

**Option 3: Check database**
```sql
SELECT * FROM tasks WHERE user_id = 'your-user-id' ORDER BY created_at DESC;
```

---

## 📝 Notes

- Keep both terminals open while using the app
- Backend logs show all API requests
- Frontend shows real-time updates
- Conversation history persists in database
- Press CTRL+C in terminals to stop servers

---

## 🆘 Need Help?

Check the comprehensive documentation:
- **Tool Calling Details**: `phase-iii/TOOL_CALLING_IMPLEMENTATION.md` ← NEW!
- **API Docs**: `phase-iii/backend/docs/api.md`
- **Setup Guide**: `phase-iii/README.md`
- **Implementation Summary**: `phase-iii/IMPLEMENTATION_COMPLETE.md`
- **Test Script**: `phase-iii/backend/test_tool_calling.py` ← NEW!

---

**Ready to start? Follow Steps 1-4 above!** 🚀

**The AI agent now actually manages your tasks - not just talks about them!** ✨
