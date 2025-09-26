@echo off
echo Starting all services...
echo.

echo [1/5] Starting Frontend...
start "Frontend" cmd /k "cd NewFrontEnd && npm run dev"

echo [2/5] Starting Quiz Bot...
start "Quiz Bot" cmd /k "cd NewBackEnd\Quiz_Bot && python app.py"

echo [3/5] Starting Teacher Chatbot...
start "Teacher Chatbot" cmd /k "cd NewBackEnd\teacher_chatbot && python app.py"

echo [4/5] Starting Course Recommender...
start "Course Recommender" cmd /k "cd NewBackEnd\Course_Recommend && python app.py"

echo [5/5] Starting AI Roadmap Generator...
start "AI Roadmap Generator" cmd /k "cd NewBackEnd\AI_Roadmap_generator && python app.py"

echo.
echo All services are starting...
echo.
echo Frontend: http://localhost:5173
echo Quiz Bot: http://localhost:5004
echo Teacher Chatbot: http://localhost:5003
echo Course Recommender: http://localhost:5001
echo AI Roadmap Generator: http://localhost:5002
echo.
echo Press any key to exit...
pause > nul 