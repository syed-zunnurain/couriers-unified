#!/usr/bin/env python
"""
Test runner script for the couriers-unified project
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shipment.test_settings")
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["shipment"])
    if failures:
        sys.exit(bool(failures))
