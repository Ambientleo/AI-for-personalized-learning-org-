@echo off
echo Starting AI Roadmap Generator API...
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting server on http://localhost:5002
echo Press Ctrl+C to stop the server
echo.
python app.py
pause 