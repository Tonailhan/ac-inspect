@echo off
setlocal
echo [DEBUG] Script started > "%~dp0debug.log"
cd /d "%~dp0"
echo [DEBUG] Changed directory to %CD% >> "%~dp0debug.log"

title AC Inspect - Anode Cover Inspector
echo.
echo  ========================================
echo   AC Inspect - Zero-Config Startup
echo  ========================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10-3.12 from python.org and ensure "Add Python to PATH" is checked.
    pause
    exit /b 1
)

:: Backend Setup
echo [1/4] Checking backend environment...
cd /d "%~dp0backend"
if not exist "venv312\Scripts\python.exe" (
    echo  - Creating Python virtual environment...
    python -m venv venv312
    echo  - Installing backend dependencies ^(downloads ~600MB, please wait^)...
    call venv312\Scripts\activate.bat
    python -m pip install --upgrade pip >nul
    pip install -r requirements.txt
    rem NOTE: inside a parenthesised block %errorlevel% expands at parse time,
    rem so it must be tested with "if errorlevel 1" to read the live value.
    if errorlevel 1 (
        echo.
        echo [ERROR] Dependency installation failed.
        echo   The most common cause is an unsupported Python version.
        echo   TensorFlow requires Python 3.10 to 3.12; yours is:
        python --version
        echo   Install Python 3.12, delete the backend\venv312 folder, and run this again.
        echo.
        call deactivate
        pause
        exit /b 1
    )
    call deactivate
) else (
    echo  - Backend environment ready.
)

:: Confirm the ML stack is actually importable — a backend without TensorFlow
:: starts normally but returns HTTP 503 for every inspection.
venv312\Scripts\python.exe -c "import tensorflow, numpy" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] TensorFlow is not available in backend\venv312.
    echo   Inspections would fail with HTTP 503.
    echo   Fix: delete the backend\venv312 folder and run start.bat again
    echo        using Python 3.10-3.12.
    echo.
    pause
    exit /b 1
)

:: Check for Node.js
cd /d "%~dp0"
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo Please install Node.js ^(LTS^) from nodejs.org.
    pause
    exit /b 1
)

:: Ensure pnpm is installed
call pnpm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  - Installing pnpm globally...
    call npm install -g pnpm >nul
)

:: Frontend Setup
echo [2/4] Checking frontend environment...
cd /d "%~dp0frontend"
if not exist "node_modules" (
    echo  - Installing frontend dependencies with pnpm ^(this may take a minute^)...
    call pnpm install
) else (
    echo  - Frontend environment ready.
)

:: Start Backend
echo [3/4] Starting backend (FastAPI on port 5001)...
cd /d "%~dp0backend"
start "AC Inspect Backend" /min cmd /c "venv312\Scripts\python.exe app.py"

echo  - Waiting for backend to initialize ^(TensorFlow model takes ~10s to load^)...
ping -n 13 127.0.0.1 >nul

:: Start Frontend
echo [4/4] Starting frontend (Next.js on port 3000)...
cd /d "%~dp0frontend"
start "AC Inspect Frontend" /min cmd /c "pnpm dev --hostname 0.0.0.0"

:: Wait for frontend to compile
cd /d "%~dp0"
echo  - Waiting for frontend to compile...
ping -n 5 127.0.0.1 >nul

:: Open browser
echo.
echo  Opening browser...
start http://localhost:3000

echo.
echo  ========================================
echo   Both servers are running!
echo   Backend:  http://localhost:5001
echo   Frontend: http://localhost:3000
echo  ========================================
echo.
echo  Close this window to exit, or use stop.bat to stop the servers.
echo  - Servers will keep running in the background terminals
pause
