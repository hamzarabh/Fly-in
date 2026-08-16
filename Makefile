install:
	python3 -m venv  venv
	./venv/bin/python3 -m pip install -r requirements.txt

run:
	python3 src/main.py

debug:
	python3 -m pdb src/main.py

clean:
	rm -rf venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

lint:
	python3 -m  flake8 src
	python3 -m mypy src --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
