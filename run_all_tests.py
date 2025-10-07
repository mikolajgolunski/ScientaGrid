#!/usr/bin/env python
"""
Run all tests for ScientaGrid project with coverage reporting.
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ScientaGrid.settings.local'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True, keepdb=False)

    # Run all tests
    failures = test_runner.run_tests([
        "apps.locations",
        "apps.institutions",
        "apps.infrastructures",
        "apps.equipment",
        "apps.services",
        "apps.access",
        "apps.taxonomy",
        "apps.specifications",
        "apps.research_problems",
        "apps.documents",
        "apps.audit",
        "apps.users",
        "apps.search",
    ])

    if failures:
        sys.exit(1)

    print("\n" + "=" * 70)
    print("All tests passed successfully!")
    print("=" * 70)