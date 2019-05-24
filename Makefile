clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	name '*~' -exec rm --force  {}

clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

pip:
	pip install -r requirements.txt

run:
	pipenv run python main.py
