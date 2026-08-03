"""Hypothesis configuration and fixtures for property-based testing."""

import os

import hypofuzz
from hypothesis import HealthCheck, settings

# Register profiles for local development, CI, and continuous fuzzing
settings.register_profile("dev", max_examples=50)
settings.register_profile("ci", max_examples=200)
settings.register_profile(
    "fuzz",
    max_examples=1000,
    suppress_health_check=[HealthCheck.too_slow],
)

# Load profile depending on whether hypofuzz is active or via environment variable
if hypofuzz.in_hypofuzz_run():
    settings.load_profile("fuzz")
else:
    settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))
