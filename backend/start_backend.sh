#!/bin/bash

# Enter the virtual environment
source ../.venv/bin/activate

# Run the API
uvicorn app:app --reload --reload-exclude './venv'