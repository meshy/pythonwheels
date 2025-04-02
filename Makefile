help:
	@echo "make help     -- print this help"
	@echo "make generate -- regenerate the json"

generate:
	wget https://hugovk.github.io/top-pypi-packages/top-pypi-packages.min.json -O top-pypi-packages.json
	python3 generate.py
