Param(
    [switch]$Format,
    [switch]$Lint,
    [switch]$TypeCheck,
    [switch]$Test
)

if (-not ($Format -or $Lint -or $TypeCheck -or $Test)) {
    $Format = $true
    $Lint = $true
    $TypeCheck = $true
    $Test = $true
}

if ($Format) {
    Write-Host "Running formatters..." -ForegroundColor Cyan
    python -m black apps config graph rag state tools observability tests
    python -m isort apps config graph rag state tools observability tests
}

if ($Lint) {
    Write-Host "Running ruff lint..." -ForegroundColor Cyan
    python -m ruff check .
}

if ($TypeCheck) {
    Write-Host "Running mypy..." -ForegroundColor Cyan
    python -m mypy apps config graph rag state tools
}

if ($Test) {
    Write-Host "Running pytest..." -ForegroundColor Cyan
    python -m pytest tests
}

Write-Host "All requested checks completed." -ForegroundColor Green

