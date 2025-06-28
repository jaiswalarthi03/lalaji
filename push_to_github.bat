@echo off
echo ========================================
echo    Meet Lalaji - GitHub Push Script
echo ========================================
echo.

:: Check if we're in a git repository
git status >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Not in a git repository!
    echo Please run this script from your project directory.
    pause
    exit /b 1
)

:: Check if there are any changes to commit
git diff --quiet
if %errorlevel% equ 0 (
    echo No changes detected. Nothing to commit.
    echo.
    pause
    exit /b 0
)

:: Show current status
echo Current Git Status:
echo ----------------------------------------
git status --short
echo.

:: Ask for commit message
set /p commit_message="Enter commit message (or press Enter for default): "
if "%commit_message%"=="" set commit_message="Update Meet Lalaji - AI Inventory Management"

echo.
echo ========================================
echo Starting Git Operations...
echo ========================================

:: Add all files
echo.
echo 1. Adding files to staging area...
git add .
if %errorlevel% neq 0 (
    echo ERROR: Failed to add files!
    pause
    exit /b 1
)
echo ✓ Files added successfully

:: Commit changes
echo.
echo 2. Committing changes...
git commit -m %commit_message%
if %errorlevel% neq 0 (
    echo ERROR: Failed to commit changes!
    pause
    exit /b 1
)
echo ✓ Changes committed successfully

:: Push to GitHub
echo.
echo 3. Pushing to GitHub...
git push origin main
if %errorlevel% neq 0 (
    echo ERROR: Failed to push to GitHub!
    echo.
    echo Possible solutions:
    echo - Check your internet connection
    echo - Verify your GitHub credentials
    echo - Make sure you have write access to the repository
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ SUCCESS! All changes pushed to GitHub
echo ========================================
echo.
echo Repository: https://github.com/jaiswalarthi03/lalaji
echo Live App: https://lalaji.vercel.app/
echo.
echo Commit Message: %commit_message%
echo.

pause 