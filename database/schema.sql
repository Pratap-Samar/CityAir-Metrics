CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL
);


CREATE TABLE weather_observations (
    id SERIAL PRIMARY KEY,
    city_id INTEGER NOT NULL REFERENCES cities(id),
    observed_at TIMESTAMP NOT NULL,

    temperature_c DOUBLE PRECISION,
    humidity_percent DOUBLE PRECISION,
    apparent_temperature_c DOUBLE PRECISION,
    precipitation_mm DOUBLE PRECISION,
    weather_code INTEGER,
    wind_speed_kmh DOUBLE PRECISION,
    wind_direction_degrees DOUBLE PRECISION
);


CREATE TABLE air_quality_observations (
    id SERIAL PRIMARY KEY,
    city_id INTEGER NOT NULL REFERENCES cities(id),
    observed_at TIMESTAMP NOT NULL,

    pm10 DOUBLE PRECISION,
    pm2_5 DOUBLE PRECISION,
    carbon_monoxide DOUBLE PRECISION,
    nitrogen_dioxide DOUBLE PRECISION,
    sulphur_dioxide DOUBLE PRECISION,
    ozone DOUBLE PRECISION,
    us_aqi DOUBLE PRECISION
);