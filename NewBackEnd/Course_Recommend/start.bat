@echo off
echo Starting Course Recommender API...
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting server on http://localhost:5001
echo Press Ctrl+C to stop the server
echo.
python app.py
pause 