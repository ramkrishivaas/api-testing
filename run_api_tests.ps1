
$ErrorActionPreference = "Continue"

Write-Host "`n========== RUNNING API TESTS ==========" -ForegroundColor Cyan

python -m pytest -v -s --alluredir=allure-results --clean-alluredir

$testExitCode = $LASTEXITCODE

Write-Host "`n========== GENERATING ALLURE REPORT ==========" -ForegroundColor Cyan

if (Get-Command allure -ErrorAction SilentlyContinue) {
    allure generate allure-results --clean -o allure-report

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Allure report generated: allure-report" -ForegroundColor Green
        allure open allure-report
    } else {
        Write-Host "Allure report generation failed." -ForegroundColor Red
    }
} else {
    Write-Host "Allure CLI is not installed or not on PATH." -ForegroundColor Yellow
    Write-Host "Install/configure the Allure command-line tool first."
}

exit $testExitCode

Write-Host "Starting Krishivaas API automation..." -ForegroundColor Cyan

python -m pytest -v -s `
    --alluredir=allure-results `
    --clean-alluredir

$testExitCode = $LASTEXITCODE

Write-Host "Generating Allure HTML report..." -ForegroundColor Cyan

if (Get-Command allure -ErrorAction SilentlyContinue) {
    allure generate allure-results --clean -o allure-report
    $reportExitCode = $LASTEXITCODE

    if ($reportExitCode -eq 0) {
        Write-Host "Report saved to: allure-report/index.html" -ForegroundColor Green
    } else {
        Write-Host "Allure report generation failed." -ForegroundColor Red
    }
} else {
    Write-Host "Allure CLI is missing or not on PATH." -ForegroundColor Yellow
}

if ($testExitCode -ne 0) {
    exit $testExitCode
}

if (-not (Get-Command allure -ErrorAction SilentlyContinue)) {
    exit 2
}

exit $reportExitCode
