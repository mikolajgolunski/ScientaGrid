#!/bin/bash

echo "Running ScientaGrid Tests..."
echo "=============================="

# Run all tests with coverage
python manage.py test --verbosity=2

# Or if using pytest:
# pytest --cov=apps --cov-report=html --cov-report=term

echo ""
echo "Tests completed!"