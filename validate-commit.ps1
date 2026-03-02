# Pre-commit validation script for Windows PowerShell
# Run this before committing: .\validate-commit.ps1

$ErrorActionPreference = "Continue"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  PRE-COMMIT VALIDATION" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$allPassed = $true

# 1. CHECK DEPENDENCIES
Write-Host "[1/5] Checking dependencies..." -ForegroundColor Green
$dependencies = @("docker", "pytest", "python")
foreach ($dep in $dependencies) {
    if (Get-Command $dep -ErrorAction SilentlyContinue) {
        Write-Host "  OK - $dep" -ForegroundColor Green
    } else {
        Write-Host "  FAIL - $dep NOT installed" -ForegroundColor Red
        $allPassed = $false
    }
}

# 2. RUN PYTEST
Write-Host "`n[2/5] Running pytest..." -ForegroundColor Green
try {
    $testOutput = python -m pytest tests/ -v --tb=short 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK - All tests passed" -ForegroundColor Green
    } else {
        Write-Host "  FAIL - Tests failed" -ForegroundColor Red
        $allPassed = $false
    }
} catch {
    Write-Host "  FAIL - Error: $_" -ForegroundColor Red
    $allPassed = $false
}

# 3. BUILD DOCKER IMAGE
Write-Host "`n[3/5] Building Docker image..." -ForegroundColor Green
try {
    $dockerOutput = docker build -t llm-rag-qa-agent:latest . 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK - Docker image built" -ForegroundColor Green
    } else {
        Write-Host "  FAIL - Docker build failed" -ForegroundColor Red
        $allPassed = $false
    }
} catch {
    Write-Host "  FAIL - Error: $_" -ForegroundColor Red
    $allPassed = $false
}

# 4. VALIDATE DOCKER-COMPOSE
Write-Host "`n[4/5] Validating docker-compose.yml..." -ForegroundColor Green
try {
    docker-compose config > $null 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK - docker-compose.yml valid" -ForegroundColor Green
    } else {
        Write-Host "  FAIL - docker-compose validation failed" -ForegroundColor Red
        $allPassed = $false
    }
} catch {
    Write-Host "  FAIL - Error: $_" -ForegroundColor Red
    $allPassed = $false
}

# 5. CHECK REQUIRED FILES
Write-Host "`n[5/5] Verifying project structure..." -ForegroundColor Green
$requiredFiles = @(
    "requirements.txt", "setup.cfg", "Dockerfile", "docker-compose.yml",
    ".pre-commit-config.yaml", ".github/workflows/ci.yml", "Makefile",
    "tests/test_agents.py", "docs/TESTING.md", "docs/CI-CD.md"
)
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  OK - $file" -ForegroundColor Green
    } else {
        Write-Host "  FAIL - $file (MISSING)" -ForegroundColor Red
        $allPassed = $false
    }
}

# SUMMARY  
Write-Host "`n========================================" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host "  SUCCESS: Ready to commit!" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Cyan
    exit 0
} else {
    Write-Host "  FAILED: Fix issues before committing" -ForegroundColor Red
    Write-Host "========================================`n" -ForegroundColor Cyan
    exit 1
}
if ($allPassed) {
    exit 0
} else {
    exit 1
}
