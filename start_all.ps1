Write-Host "Starting all services..." -ForegroundColor Green
Write-Host ""

# Start Frontend
Write-Host "[1/5] Starting Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'NewFrontEnd'; npm run dev"

# Start Quiz Bot
Write-Host "[2/5] Starting Quiz Bot..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'NewBackEnd\Quiz_Bot'; python app.py"

# Start Teacher Chatbot
Write-Host "[3/5] Starting Teacher Chatbot..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'NewBackEnd\teacher_chatbot'; python app.py"

# Start Course Recommender
Write-Host "[4/5] Starting Course Recommender..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'NewBackEnd\Course_Recommend'; python app.py"

# Start AI Roadmap Generator
Write-Host "[5/5] Starting AI Roadmap Generator..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'NewBackEnd\AI_Roadmap_generator'; python app.py"

Write-Host ""
Write-Host "All services are starting..." -ForegroundColor Green
Write-Host ""
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "Quiz Bot: http://localhost:5004" -ForegroundColor Cyan
Write-Host "Teacher Chatbot: http://localhost:5003" -ForegroundColor Cyan
Write-Host "Course Recommender: http://localhost:5001" -ForegroundColor Cyan
Write-Host "AI Roadmap Generator: http://localhost:5002" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 