#!/bin/bash
# Kill any existing backend process
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Start Backend
echo "Starting Backend..."
cd backend
source ../venv/bin/activate
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Start Frontend
echo "Starting Frontend..."
cd ../frontend
source ~/.nvm/nvm.sh
npm run dev &
FRONTEND_PID=$!

echo "App running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "Press CTRL+C to stop."

wait $BACKEND_PID $FRONTEND_PID
