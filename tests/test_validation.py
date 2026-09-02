from datetime import datetime, timedelta, timezone

import pytest

from ingestion.validation import validate_freshness


def test_fresh_observation_passes():
    observed_at = datetime.now(timezone.utc) - timedelta(minutes=30)

    validate_freshness(
        observed_at,
        max_age_minutes=120,
    )


def test_stale_observation_fails():
    observed_at = datetime.now(timezone.utc) - timedelta(minutes=180)

    with pytest.raises(ValueError, match="Stale observation"):
        validate_freshness(
            observed_at,
            max_age_minutes=120,
        )


def test_future_observation_fails():
    observed_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    with pytest.raises(
        ValueError,
        match="Observation timestamp is in the future",
    ):
        validate_freshness(
            observed_at,
            max_age_minutes=120,
        )