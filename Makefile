.PHONY: init lint test clean

init:
	pip install -r requirements.txt

lint:
	pylint src tests

test:
	pytest -ra

clean:
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf tests/__pycache__/
	rm -rf build/

run:
	python3 src/
