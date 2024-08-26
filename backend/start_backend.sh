#!/bin/bash

# Enter the virtual environment (if this fails, run create_venv.sh first)
source venv/bin/activate

# Run the API
uvicorn app:app --reload --reload-exclude './venv'