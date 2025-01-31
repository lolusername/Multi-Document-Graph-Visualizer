# Constants
TXT_DIR := ./txt_data
OUTPUT_DIR := ./viz/public/d3_data
PYTHON_VERSION := 3.10.13

.PHONY: all setup install run  test clean viz serve-frontend

help:
	@echo "Available commands:"
	@echo "  setup        - Initial project setup (first time setup)"
	@echo "  install      - Install/update dependencies"
	@echo "  run          - Run full analysis on PDF directory"
	@echo "  test         - Run test analysis on PDF directory (5 files)"
	@echo "  clean        - Remove generated files and cache"
	@echo "  viz          - Launch visualization app"
	@echo "  help         - Show this help message"

# Main command to run everything
all: setup run serve-frontend

setup:
	@command -v pyenv >/dev/null 2>&1 || { echo >&2 "pyenv is required. Please install it first."; exit 1; }
	@command -v poetry >/dev/null 2>&1 || { echo >&2 "poetry is required. Please install it first."; exit 1; }
	@echo "Installing Python $(PYTHON_VERSION) with pyenv..."
	@pyenv install --skip-existing $(PYTHON_VERSION)
	@pyenv local $(PYTHON_VERSION)
	@echo "Configuring Poetry to use Python $(PYTHON_VERSION)..."
	@poetry env use $$(pyenv which python)
	@echo "Regenerating poetry.lock file..."
	@poetry lock --no-update
	@$(MAKE) install
	@echo "Installing frontend dependencies..."
	cd viz && npm install

install:
	@echo "Installing Python dependencies..."
	@poetry install --no-root
	@echo "Installing spaCy model..."
	@poetry run python -m spacy download en_core_web_sm

run: install
	@echo "Running full analysis on PDF directory..."
	@mkdir -p $(OUTPUT_DIR)
	@poetry run python main.py \
		--pdf_dir $(TXT_DIR) \
		--output_dir $(OUTPUT_DIR)

serve-frontend:
	@echo "Starting Vue frontend..."
	cd viz && npm run dev

test: install
	@echo "Running test analysis on PDF directory (5 files)..."
	@poetry run python main.py \
		--pdf_dir $(PDF_DIR) \
		--output_dir $(OUTPUT_DIR) \
		--test

clean:
	@rm -rf $(OUTPUT_DIR)/*
	@find . -type d -name "__pycache__" -exec rm -r {} +
	@find . -type f -name "*.pyc" -delete
	@poetry env remove --all 2>/dev/null || true
	cd viz && rm -rf node_modules

viz:
	@echo "Starting visualization app..."
	@cd viz && \
		rm -rf node_modules package-lock.json && \
		rm -rf public/data && \
		mkdir -p public && \
		npm install && \
		npm run dev 