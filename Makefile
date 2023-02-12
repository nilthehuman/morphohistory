PYTHON = python3

.PHONY: setup lint test clean run

setup:
	# maybe consider switching to Poetry later
	$(PYTHON) -m pip install -r requirements.txt

lint:
	pylint src tests

test:
	pytest -x -ra

clean:
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf src/gui/__pycache__/
	rm -rf tests/__pycache__/
	rm -rf build/

run:
	$(PYTHON) .
