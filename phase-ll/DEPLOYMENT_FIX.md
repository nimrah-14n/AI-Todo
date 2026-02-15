# Fix for 405 Error on /api/auth/signin

## Problem
The frontend is making requests to its own domain (`ai-todo-ao1q.vercel.app/api/auth/signin`) instead of the backend API (`backend-rho-flame-41.vercel.app/api/auth/signin`).

## Root Cause
The `NEXT_PUBLIC_API_URL` environment variable is not properly set in Vercel's dashboard for the frontend deployment.

## Solution

### Step 1: Configure Environment Variables in Vercel

#### For Frontend Project (ai-todo-ao1q or frontend):
1. Go to Vercel Dashboard → Your Frontend Project → Settings → Environment Variables
2. Add/Update the following variables for **Production** environment:
   ```
   NEXT_PUBLIC_API_URL=https://backend-rho-flame-41.vercel.app
   NEXT_PUBLIC_APP_NAME=Todo App
   NEXT_PUBLIC_APP_URL=https://ai-todo-ao1q.vercel.app
   BETTER_AUTH_SECRET=dvcJjRVksqjieHu6JANGs7YgsArBz34WuKu1aroVTXqCBSL4w0MWCgsVwdR5pWq
   ```

#### For Backend Project:
1. Go to Vercel Dashboard → Your Backend Project → Settings → Environment Variables
2. Verify these variables are set for **Production** environment:
   ```
   DATABASE_URL=postgresql://neondb_owner:npg_ULOZaJXK2dW9@ep-bitter-paper-ahfyukwe-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require
   BETTER_AUTH_SECRET=dvcJjRVksqjieHu6JANGs7YgsArBz34WuKu1aroVTXqCBBSL4w0MWCgsVwdR5pWq
   APP_ENV=production
   DEBUG=False
   CORS_ORIGINS=https://frontend-alpha-coral-97.vercel.app,https://ai-todo-ao1q.vercel.app,http://localhost:3000
   HOST=0.0.0.0
   PORT=8000
   ```

### Step 2: Redeploy Both Projects

#### Option A: Using Vercel CLI
```bash
# Redeploy backend
cd phase-ll/backend
vercel --prod

# Redeploy frontend
cd ../frontend
vercel --prod
```

#### Option B: Using Git Push
```bash
# Commit the changes
git add phase-ll/frontend/next.config.js phase-ll/backend/.env.production
git commit -m "Fix: Add API proxy rewrites and update CORS configuration"
git push origin main
```

#### Option C: Manual Redeploy in Vercel Dashboard
1. Go to Vercel Dashboard → Deployments
2. Click on the latest deployment
3. Click "Redeploy" button

### Step 3: Verify the Fix

1. Open browser DevTools (F12) → Network tab
2. Navigate to `https://ai-todo-ao1q.vercel.app/signin`
3. Try to sign in
4. Check the Network tab:
   - The request should go to: `https://backend-rho-flame-41.vercel.app/api/auth/signin`
   - Status should be 200 (not 405)

### Step 4: Test the Authentication Flow

1. **Sign Up**: Create a new account at `/signup`
2. **Sign In**: Log in with the created account at `/signin`
3. **Dashboard**: Verify you're redirected to `/dashboard` after successful login
4. **Create Task**: Try creating a new task
5. **Sign Out**: Test the sign out functionality

## Changes Made

### 1. Frontend: next.config.js
Added API proxy rewrites to forward `/api/*` requests to the backend URL. This ensures that even if the environment variable isn't set, requests will be proxied correctly.

### 2. Backend: .env.production
Updated CORS_ORIGINS to include all frontend domains and localhost for development.

## Troubleshooting

### If you still get 405 errors:

1. **Check Environment Variables**:
   ```bash
   # In Vercel Dashboard, verify NEXT_PUBLIC_API_URL is set
   # It should be: https://backend-rho-flame-41.vercel.app
   ```

2. **Check Browser Console**:
   - Open DevTools → Console
   - Look for the actual URL being called
   - If it's still calling `ai-todo-ao1q.vercel.app/api/...`, the env var isn't set

3. **Clear Cache and Redeploy**:
   ```bash
   cd phase-ll/frontend
   vercel --prod --force
   ```

4. **Check Backend Logs**:
   - Go to Vercel Dashboard → Backend Project → Logs
   - Look for CORS errors or 405 errors
   - Verify the backend is receiving requests

### If you get CORS errors:

1. Verify the backend CORS_ORIGINS includes your frontend domain
2. Check that the backend is deployed and running
3. Test the backend directly: `https://backend-rho-flame-41.vercel.app/health`

## Additional Notes

- The rewrites configuration in next.config.js acts as a fallback proxy
- For production, the proper solution is setting NEXT_PUBLIC_API_URL in Vercel
- Both frontend and backend must be redeployed after environment variable changes
- Environment variables in Vercel are only applied to new deployments, not existing ones
