#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Run test suite for PRISM
.DESCRIPTION
    Runs pytest with coverage reporting and generates both terminal and HTML reports
.PARAMETER Coverage
    Generate coverage report (default: $true)
.PARAMETER Verbose
    Show verbose output (default: $false)
.PARAMETER HTMLReport
    Generate HTML coverage report (default: $true)
.EXAMPLE
    .\run-tests.ps1
    .\run-tests.ps1 -Verbose
    .\run-tests.ps1 -Coverage:$false
#>

param(
    [bool]$Coverage = $true,
    [bool]$Verbose = $false,
    [bool]$HTMLReport = $true
)

Write-Host "Starting test suite..." -ForegroundColor Cyan

# Check if pytest is installed
try {
    py -3 -m pytest --version | Out-Null
} catch {
    Write-Host "pytest not found. Installing dev dependencies..." -ForegroundColor Yellow
    py -3 -m pip install -r requirements.txt -e .
}

# Ensure pytest-cov is installed if coverage is requested
if ($Coverage) {
    py -3 -m pip install pytest-cov -q
}

# Build pytest arguments
$args = @("tests/")

if ($Verbose) {
    $args += "-v"
    $args += "-s"
}

if ($Coverage) {
    $args += "--cov=src"
    $args += "--cov-report=term-missing"
    if ($HTMLReport) {
        $args += "--cov-report=html"
    }
}

# Run tests
Write-Host "Running tests with arguments: $($args -join ' ')" -ForegroundColor Gray
py -3 -m pytest @args

$exitCode = $LASTEXITCODE

# Print summary
Write-Host "`n" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "[PASS] All tests passed!" -ForegroundColor Green
    if ($HTMLReport -and $Coverage) {
        Write-Host "Coverage report generated at: htmlcov/index.html" -ForegroundColor Green
    }
} else {
    Write-Host "[FAIL] Tests failed with exit code: $exitCode" -ForegroundColor Red
}

exit $exitCode
