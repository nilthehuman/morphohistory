PYTHON = python3

.PHONY: init init_optional lint test clean run

init:
	$(PYTHON) -m pip install kivy[base] kivy_examples --pre --extra-index-url https://kivy.org/downloads/simple/
	# maybe consider switching to Poetry later
	$(PYTHON) -m pip install -r requirements.txt

init_optional:
	$(PYTHON) -m pip install -r optional-requirements.txt

lint:
	pylint src tests

test:
	pytest -x -ra

typecheck:
	mypy -p src --ignore-missing-imports

clean:
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf src/gui/__pycache__/
	rm -rf tests/__pycache__/
	rm -rf build/
	rm -rf .mypy_cache/
	rm -rf .pytest_cache/

run:
	$(PYTHON) .
