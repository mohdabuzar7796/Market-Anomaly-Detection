.PHONY: data run format lint test clean diagram

PYTHON := uv run python

run:
	uv run python -m market_anomaly_detection.execution.runner

diagram:
	npx -y @mermaid-js/mermaid-cli -i references/architecture_diagram.mmd -o references/architecture_diagram.svg

data:
	@echo "Data directories already created under data/"

format:
	uvx ruff format market_anomaly_detection

lint:
	uvx ruff check market_anomaly_detection

test:
	$(PYTHON) -m pytest

clean:
	@echo "Nothing to clean"
