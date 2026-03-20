Write-Host "======================================="
Write-Host "Texas Hold'em Multi-Agent Game"
Write-Host "======================================="
Write-Host ""
Write-Host "Starting game..."
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Error: Virtual environment not found!"
    Write-Host "Please create and activate virtual environment first, then install AgentScope"
    Read-Host "Press any key to exit..."
    exit 1
}

# Run the game
.venv\Scripts\python main.py

# Pause after game ends
Write-Host ""
Write-Host "Game finished. Press any key to exit..."
Read-Host
