from ingestion.transform import transform_air_quality


def test_transform_air_quality():

    city = {
        "name": "Delhi",
        "country": "India",
        "latitude": 28.6139,
        "longitude": 77.2090,
    }

    data = {
        "current": {
            "time": "2026-08-27T11:30",
            "pm10": 90.1,
            "pm2_5": 64.0,
            "carbon_monoxide": 590.0,
            "nitrogen_dioxide": 21.0,
            "sulphur_dioxide": 46.6,
            "ozone": 213.0,
            "us_aqi": 171,
        },
        "utc_offset_seconds": 19800,
    }

    observation = transform_air_quality(city, data)

    assert observation.city == "Delhi"
    assert observation.pm10 == 90.1
    assert observation.pm2_5 == 64.0
    assert observation.carbon_monoxide == 590.0
    assert observation.nitrogen_dioxide == 21.0
    assert observation.sulphur_dioxide == 46.6
    assert observation.ozone == 213.0
    assert observation.us_aqi == 171