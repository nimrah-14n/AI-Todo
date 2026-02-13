@echo off
echo Stopping Node processes...
taskkill /F /IM node.exe 2>nul

echo Clearing Next.js cache...
cd frontend
if exist .next rmdir /s /q .next

echo Starting development server...
npm run dev
