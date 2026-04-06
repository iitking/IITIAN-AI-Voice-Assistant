#!/usr/bin/env bash
# Run all tests
cd "$(dirname "$0")/.."
echo "🧪 Running IITIAN Test Suite..."
python3 -m unittest discover -s tests -p "test_*.py"
