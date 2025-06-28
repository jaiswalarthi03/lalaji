# Meet Lalaji - GitHub Push Script (PowerShell)
# Run this script from your project directory

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Meet Lalaji - GitHub Push Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in a git repository
try {
    $gitStatus = git status 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Not in a git repository!" -ForegroundColor Red
        Write-Host "Please run this script from your project directory." -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
} catch {
    Write-Host "ERROR: Git not found or not accessible!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if there are any changes to commit
$hasChanges = git diff --quiet 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "No changes detected. Nothing to commit." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 0
}

# Show current status
Write-Host "Current Git Status:" -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Gray
git status --short
Write-Host ""

# Ask for commit message
$commitMessage = Read-Host "Enter commit message (or press Enter for default)"
if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    $commitMessage = "Update Meet Lalaji - AI Inventory Management"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Git Operations..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Add all files
Write-Host ""
Write-Host "1. Adding files to staging area..." -ForegroundColor Yellow
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to add files!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Files added successfully" -ForegroundColor Green

# Commit changes
Write-Host ""
Write-Host "2. Committing changes..." -ForegroundColor Yellow
git commit -m $commitMessage
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to commit changes!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Changes committed successfully" -ForegroundColor Green

# Push to GitHub
Write-Host ""
Write-Host "3. Pushing to GitHub..." -ForegroundColor Yellow
git push origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to push to GitHub!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible solutions:" -ForegroundColor Yellow
    Write-Host "- Check your internet connection" -ForegroundColor Gray
    Write-Host "- Verify your GitHub credentials" -ForegroundColor Gray
    Write-Host "- Make sure you have write access to the repository" -ForegroundColor Gray
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ SUCCESS! All changes pushed to GitHub" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Repository: https://github.com/jaiswalarthi03/lalaji" -ForegroundColor Cyan
Write-Host "Live App: https://lalaji.vercel.app/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Commit Message: $commitMessage" -ForegroundColor Gray
Write-Host ""

Read-Host "Press Enter to exit" 