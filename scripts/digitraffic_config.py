"""Shared Digitraffic API configuration."""

import os


def get_digitraffic_user() -> str:
    """Return the configured Digitraffic-User header."""

    value = os.environ.get("DIGITRAFFIC_USER", "").strip()

    if not value:
        raise ValueError(
            "DIGITRAFFIC_USER is not set. "
            "Example: export DIGITRAFFIC_USER='MyOrg/vms-history-scan'"
        )

    return value