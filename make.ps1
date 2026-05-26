param(
    [Parameter(Position=0)]
    [string]$Target = "run"
)

$python = "python"

switch ($Target) {
    "run" {
        & $python -m market_anomaly_detection.modeling.predict
    }
    "data" {
        Write-Host "Data directories already created under data/"
    }
    "format" {
        & $python -m black market_anomaly_detection
    }
    "lint" {
        & $python -m flake8 market_anomaly_detection
    }
    "test" {
        & $python -m pytest
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
