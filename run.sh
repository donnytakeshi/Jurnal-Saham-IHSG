cd /Users/donnytakeshi/Documents/jurnal-saham-ihsg
./run.sh#!/bin/bash
# Quick script to run the AI Agent with virtual environment activated

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Activate virtual environment
source venv/bin/activate

# Run the AI Agent
python ai_agent.py "$@"
