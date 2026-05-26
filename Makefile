.PHONY: data run format lint test clean

PYTHON := python

run:
	$(PYTHON) -m market_anomaly_detection.modeling.predict

data:
	@echo "Data directories already created under data/"

format:
	$(PYTHON) -m black market_anomaly_detection

lint:
	$(PYTHON) -m flake8 market_anomaly_detection

test:
	$(PYTHON) -m pytest

clean:
	@echo "Nothing to clean"
