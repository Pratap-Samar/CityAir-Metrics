from datetime import datetime, timezone
from ingestion.models import WeatherObservation, AirQualityObservation


MAX_DATA_AGE_MINUTES = 120


def validate_freshness(
    observed_at: datetime,
    max_age_minutes: int = MAX_DATA_AGE_MINUTES,
) -> None:
    now = datetime.now(timezone.utc)

    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(tzinfo=timezone.utc)

    age_minutes = (now - observed_at).total_seconds() / 60

    if age_minutes > max_age_minutes:
        raise ValueError(
            f"Stale observation: age={age_minutes:.2f} minutes, "
            f"maximum={max_age_minutes} minutes"
        )

    if age_minutes < 0:
        raise ValueError(
            f"Observation timestamp is in the future: {observed_at}"
        )


def validate_weather_freshness(
    observation: WeatherObservation,
) -> None:
    validate_freshness(observation.observed_at)


def validate_air_quality_freshness(
    observation: AirQualityObservation,
) -> None:
    validate_freshness(observation.observed_at)