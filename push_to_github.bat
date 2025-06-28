@echo off
echo ========================================
echo    Meet Lalaji - Auto GitHub Push
echo ========================================
echo.

:: Check if we're in a git repository
git status >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Not in a git repository!
    echo Please run this script from your project directory.
    exit /b 1
)

:: Check if there are any changes to commit
git diff --quiet
if %errorlevel% equ 0 (
    echo No changes detected. Nothing to commit.
    exit /b 0
)

:: Generate timestamp for commit message
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%-%MM%-%DD% %HH%:%Min%:%Sec%"

:: Set automatic commit message
set commit_message="Auto Update - Meet Lalaji AI Inventory Management - %timestamp%"

echo Current Git Status:
echo ----------------------------------------
git status --short
echo.

echo ========================================
echo Starting Automatic Git Operations...
echo ========================================

:: Add all files
echo.
echo 1. Adding files to staging area...
git add .
if %errorlevel% neq 0 (
    echo ERROR: Failed to add files!
    exit /b 1
)
echo ✓ Files added successfully

:: Commit changes
echo.
echo 2. Committing changes...
git commit -m %commit_message%
if %errorlevel% neq 0 (
    echo ERROR: Failed to commit changes!
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
echo Auto-push completed at %timestamp%
echo. 