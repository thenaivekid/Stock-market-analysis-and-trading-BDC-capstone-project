#!/bin/bash
# Script to run tests inside Docker container

echo "Running unit tests inside Docker container..."
echo "=============================================="

# Run tests from the app/tests directory
python3 -m unittest discover -s app/tests -v

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✓ All tests passed!"
else
    echo ""
    echo "✗ Some tests failed. Exit code: $exit_code"
fi

exit $exit_code
