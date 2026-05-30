param(
    [Parameter(Position = 0)]
    [string]$Target = "run"
)

switch ($Target) {
    "run" {
        uv run python -m market_anomaly_detection.execution.runner
    }
    "diagram" {
        Write-Host "Compiling Mermaid Diagram to SVG..." -ForegroundColor Cyan
        npx -y "@mermaid-js/mermaid-cli" -i references\architecture_diagram.mmd -o references\architecture_diagram.svg
    }
    "data" {
        Write-Host "Data directories already created under data/"
    }
    "format" {
        uvx ruff format market_anomaly_detection
    }
    "lint" {
        uvx ruff check market_anomaly_detection
    }
    "test" {
        uv run python -m pytest
    }
    "clean" {
        Write-Host "Nothing to clean"
    }
    default {
        Write-Host "Unknown target: $Target"
        Write-Host "Usage: .\make.ps1 [run|data|format|lint|test|clean]"
        exit 1
    }
}