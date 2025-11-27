# Infrastructure as Code
mkdir -p terraform/modules/s3 terraform/modules/kinesis terraform/modules/redshift terraform/modules/glue terraform/modules/lambda terraform/modules/sns_sqs
touch terraform/main.tf terraform/variables.tf terraform/outputs.tf terraform/provider.tf

# Data directories
mkdir -p data/raw data/processed

# Scripts
mkdir -p scripts
touch scripts/simulator.py scripts/glue_etl.py scripts/utils.py

# Notebooks
mkdir -p notebooks
touch notebooks/flight_analysis.ipynb

# Documentation
mkdir -p docs
touch docs/architecture_diagram.png docs/data_dictionary.md

# Tests
mkdir -p tests
touch tests/test_glue_etl.py tests/test_streaming.py

# Core files (skip if already done)
touch README.md .gitignore

echo "Project structure created successfully in current directory!"
