# Chatbot Tool Calling Issues - Analysis & Solutions

## 🔴 Critical Issues Identified

### Issue 1: Groq's Function Calling Format Incompatibility
**Problem:** Groq's LLaMA models use XML-like function format instead of OpenAI's standard format.

**Groq Format:**
```
<function=list_tasks={"is_complete":true}</function>
```

**OpenAI Format:**
```json
{
  "tool_calls": [{
    "function": {
      "name": "list_tasks",
      "arguments": "{\"is_complete\": true}"
    }
  }]
}
```

**Impact:** Function calls appear as raw text in chat instead of being executed.

### Issue 2: Agent Hallucinating Task IDs
**Problem:** Agent invents placeholder IDs like "admission_task_id" instead of looking up real UUIDs.

**Example Error:**
```
Invalid task_id format: <admission_task_id>
```

**Root Cause:** Agent doesn't understand it MUST call `list_tasks` first to get real UUIDs.

### Issue 3: 500 Internal Server Error
**Problem:** When Groq returns malformed function calls, the server crashes.

**Error:**
```
BadRequestError: Error code: 400 - Failed to call a function
```

---

## ✅ Solutions Implemented

### Solution 1: Groq Function Parser (NEW)
Created `groq_parser.py` to handle Groq's XML-like format:

**Features:**
- Detects Groq function format in responses
- Parses `<function=name={args}</function>` syntax
- Extracts clean text without function tags
- Converts to standard tool calls

**Location:** `phase-iii/backend/src/agents/groq_parser.py`

### Solution 2: Enhanced Agent Instructions
Updated `todo_agent.py` with explicit task ID lookup process:

**New Instructions:**
```
CRITICAL: Task ID Lookup Process

When user refers to task by name:
1. FIRST call list_tasks to get all tasks
2. Find matching task by title
3. Extract real task_id (UUID)
4. THEN call appropriate tool with real UUID

NEVER use placeholder IDs like "admission_task_id"
```

### Solution 3: Updated Runner Logic
Modified `runner.py` to:
- Detect Groq function format
- Parse and execute Groq functions
- Handle both OpenAI and Groq formats
- Better error handling

---

## 🚨 Remaining Issues

### The Core Problem: Groq vs OpenAI

**Groq's LLaMA models have LIMITED function calling support:**
- Function calling is experimental
- Format is non-standard
- Reliability is inconsistent
- Often returns malformed calls

**OpenAI's models have FULL function calling support:**
- Stable and reliable
- Standard format
- Proper tool_calls structure
- Better at following instructions

---

## 🎯 Recommended Solutions

### Option 1: Switch to OpenAI (RECOMMENDED)

**Pros:**
- Proper function calling support
- More reliable
- Better instruction following
- Standard format

**Cons:**
- Costs money (but very cheap for testing)
- Need OpenAI API key

**How to Switch:**
```bash
# 1. Get OpenAI API key from platform.openai.com
# 2. Update .env
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini  # Cheap and good

# 3. Restart backend
```

**Cost:** ~$0.01 per 100 messages (very cheap)

### Option 2: Use Groq with Workarounds (CURRENT)

**Pros:**
- Free
- Fast
- Already configured

**Cons:**
- Unreliable function calling
- Requires complex parsing
- May still fail randomly

**Status:** Partially implemented, needs more testing

### Option 3: Disable Function Calling (FALLBACK)

**Approach:** Have agent respond with instructions instead of calling tools.

**Example:**
```
User: "Update admission task to 9 AM"
Agent: "To update the admission task, please:
1. First, show me your tasks by saying 'show my tasks'
2. Then tell me the exact task ID you want to update"
```

**Pros:**
- Always works
- No function calling issues

**Cons:**
- Poor user experience
- Not meeting Phase III requirements

---

## 🔧 Testing the Current Fix

### Test 1: List Tasks
```bash
curl -X POST http://localhost:8000/api/00000000-0000-0000-0000-000000000001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me all my tasks"}'
```

**Expected:** Should list all tasks with proper formatting

### Test 2: Add Task
```bash
curl -X POST http://localhost:8000/api/00000000-0000-0000-0000-000000000001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to call mom"}'
```

**Expected:** Should create task and confirm

### Test 3: Update Task by Name (PROBLEMATIC)
```bash
curl -X POST http://localhost:8000/api/00000000-0000-0000-0000-000000000001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Update the admission task to say go at 9 AM"}'
```

**Expected:** Should list tasks first, find admission task, then update it
**Reality:** May still fail with Groq

---

## 📊 Comparison: OpenAI vs Groq

| Feature | OpenAI GPT-4o-mini | Groq LLaMA 3.3 70B |
|---------|-------------------|-------------------|
| Function Calling | ✅ Excellent | ⚠️ Experimental |
| Reliability | ✅ 99%+ | ⚠️ 70-80% |
| Cost | 💰 ~$0.01/100 msgs | 🆓 Free |
| Speed | ⚡ Fast | ⚡⚡ Very Fast |
| Instruction Following | ✅ Excellent | ⚠️ Good |
| Task ID Lookup | ✅ Reliable | ❌ Often fails |

---

## 🎯 My Recommendation

**For Phase III Submission:**

1. **Switch to OpenAI GPT-4o-mini** for reliable function calling
2. **Keep Groq as backup** for free tier users
3. **Add model selection** in environment variables

**Why:**
- Phase III requires reliable tool calling
- Judges will test the chatbot
- OpenAI costs ~$1 for entire testing period
- Better to spend $1 than lose points

**Implementation:**
```python
# In .env
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini  # or gpt-3.5-turbo for even cheaper
```

---

## 🚀 Next Steps

### Immediate (5 minutes):
1. Get OpenAI API key from platform.openai.com
2. Update `.env` with OpenAI credentials
3. Restart backend
4. Test all commands

### Short Term (30 minutes):
1. Test thoroughly with OpenAI
2. Document any remaining issues
3. Create demo video
4. Prepare for submission

### Optional (1 hour):
1. Implement model switching (OpenAI/Groq)
2. Add fallback logic
3. Better error messages

---

## 💡 Quick Fix Right Now

If you want to test immediately:

```bash
# 1. Stop current backend
# 2. Update .env:
OPENAI_API_KEY=sk-proj-...  # Your OpenAI key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# 3. Restart backend
cd phase-iii/backend
.venv\Scripts\activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Then test in browser at http://localhost:3000

---

## 📝 Summary

**Current Status:**
- ✅ Groq parser implemented
- ✅ Agent instructions improved
- ⚠️ Still unreliable with Groq
- ❌ Function calling not working consistently

**Best Solution:**
- Switch to OpenAI GPT-4o-mini
- Cost: ~$1 for entire project
- Reliability: 99%+
- Time to fix: 5 minutes

**Your Choice:**
1. **Switch to OpenAI** - Recommended, reliable, small cost
2. **Keep debugging Groq** - Free but frustrating
3. **Disable function calling** - Works but poor UX

What would you like to do?
