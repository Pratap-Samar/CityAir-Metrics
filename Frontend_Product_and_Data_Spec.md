# CityAir Metrics — Frontend Product & Data Specification

## 1. Product Direction

CityAir Metrics is a weather and air-quality analytics application focused on cities, historical trends, city comparison, Indian city rankings, and severe-weather awareness.

The frontend should feel like a professional environmental analytics product with a technical/developer-oriented character.

### Visual principle

Take inspiration from the strengths of modern Linux/Hyprland/Arch environments:

- clean information density
- restrained colors
- excellent typography
- strong dark-mode design
- minimal decoration
- clear hierarchy
- keyboard-friendly interactions
- technical character

Do **not** make the application look like Linux cosplay. The result should still look like a polished environmental analytics application.

---

# 2. Core Frontend Stack

Current frontend:

- React
- TypeScript
- Vite
- ESLint

Planned UI direction:

- Lucide for the primary icon system
- shadcn/ui for customizable UI components
- Radix-style accessible interaction patterns where useful
- A charting library for historical and comparison visualizations
- Custom CityAir theme/design tokens

### Icon principle

Use one primary icon family consistently rather than mixing many unrelated icon sets.

Recommended primary icon library:

- Lucide

Example icon mapping:

| Application feature | Icon concept |
|---|---|
| Dashboard | LayoutDashboard |
| Cities | Building2 |
| Compare | GitCompare |
| Rankings | Trophy |
| Weather | CloudSun |
| Air quality | Wind |
| Temperature | Thermometer |
| Settings | Settings |
| Light theme | Sun |
| Dark theme | Moon |
| Location | MapPin |
| Refresh | RefreshCw |
| Alerts | TriangleAlert |
| Severe weather | CloudLightning |
| Cyclone | Wind / rotating-weather representation |

---

# 3. Application Navigation

Use a vertical navigation bar on the left.

Proposed navigation:

```text
CITYAIR
│
├── Dashboard
├── Cities
├── Compare
├── Rankings
├── History
├── Severe Weather
└── Settings
```

### Dashboard

Primary landing page.

### Cities

Browse and inspect supported cities.

### Compare

Compare 2–4 cities.

### Rankings

Rank Indian cities using documented metrics.

### History

Historical weather and air-quality analysis.

### Severe Weather

Thunderstorms, heavy rain, cyclones, and official warnings.

### Settings

Theme, location preferences, and other application settings.

---

# 4. Theme System

The application must support:

- Light theme
- Dark theme

The theme should be application-wide and consistent.

## Dark theme direction

Use:

- near-black / charcoal background
- slightly lighter panels
- high-contrast gray/white text
- restrained blue/cyan accent
- thin borders
- minimal shadows

## Light theme direction

Use:

- soft gray/white background
- white panels
- dark gray text
- same core accent as dark mode

The light and dark themes should share the same design language rather than being separate designs.

---

# 5. Weather-Aware Background

When viewing a city, the background should correspond to current weather when feasible.

The weather state can be derived from the weather observation / weather code.

Possible visual states:

| Weather state | Visual treatment |
|---|---|
| Sunny / clear | warm/light atmospheric background |
| Partly cloudy | subtle mixed light/cloud treatment |
| Cloudy | cool muted background |
| Rain | darker/cooler treatment with subtle rain visual |
| Thunderstorm | darker storm treatment |
| Snow | cool pale treatment |
| Night | dark blue/charcoal treatment |

## Design rule

The weather background must remain subtle.

It should:

- reinforce current conditions
- improve visual feedback
- not interfere with charts
- not reduce text contrast
- not become a large animated illustration

Day/night should also be considered using the city's local time information where available.

Conceptual flow:

```text
Weather API
    ↓
weather_code + time/day state
    ↓
Frontend weather state
    ↓
weather-aware visual treatment
```

---

# 6. Landing Page / User Location

The landing page should prioritize the user's city.

Conceptually:

```text
Your location

Bhopal, Madhya Pradesh
India

28°C
Partly cloudy

Humidity       64%
Wind           12 km/h
PM2.5          32 µg/m³
US AQI         78
```

Below the current conditions:

```text
Today

Temperature
[24-hour historical chart]

Air Quality
[24-hour historical chart]
```

## Location behavior

A future implementation can support:

1. Detect user's location with browser permission.
2. Resolve the location to a supported CityAir city.
3. Show that city on the dashboard.
4. Provide a manual city selector as fallback.

Do not assume browser geolocation is always available or permitted.

---

# 7. Current City Dashboard

The city dashboard should show current weather and air-quality information prominently.

Primary metrics:

- Temperature
- Apparent temperature
- Humidity
- Wind speed
- Wind direction
- Precipitation
- PM10
- PM2.5
- Carbon monoxide
- Nitrogen dioxide
- Sulphur dioxide
- Ozone
- US AQI

The existing backend already provides latest city weather and air-quality data through `/analytics`.

---

# 8. Historical Data Views

Historical data should have three primary UI windows:

| View | Resolution | Purpose |
|---|---|---|
| 24H | Hourly observations | Short-term conditions |
| 7D | Daily aggregates | Weekly patterns |
| 30D | Daily aggregates | Medium-term patterns |

Do **not** call the 30-day view "weekly".

A true weekly aggregation would contain approximately 4–5 weekly points over 30 days. The planned 30D view should use daily data points.

## 24H

Use hourly observations.

Purpose:

- today's temperature movement
- recent PM2.5 movement
- recent AQI movement
- short-term weather changes
- identifying spikes

## 7D

Use daily aggregates.

Purpose:

- identify daily patterns
- compare days
- see whether conditions are improving or worsening
- reduce visual noise from 168 hourly points

## 30D

Use daily aggregates.

Purpose:

- medium-term trends
- sustained air-quality changes
- broader weather patterns

---

# 9. Historical API Design

Existing historical endpoints:

```text
GET /weather/history/{city_id}?hours=24
GET /air-quality/history/{city_id}?hours=24
```

These return chronological observations.

## Weather history fields

```text
observed_at
temperature_c
humidity_percent
apparent_temperature_c
precipitation_mm
wind_speed_kmh
```

## Air-quality history fields

```text
observed_at
pm10
pm2_5
carbon_monoxide
nitrogen_dioxide
sulphur_dioxide
ozone
us_aqi
```

The backend should eventually expose daily aggregates for 7D and 30D rather than making React perform analytical aggregation.

Principle:

```text
PostgreSQL
    ↓
Analytics layer
    ↓
FastAPI
    ↓
React
```

Do not make the frontend responsible for core analytical calculations.

---

# 10. History vs Trend

These are different concepts.

## History

History means:

> Return the observations over a selected period.

Example:

```text
08:00  21°C
09:00  22°C
10:00  24°C
11:00  26°C
```

This is what a historical chart uses.

## Trend

Trend means:

> Compare two periods and determine whether the metric is increasing, decreasing, or stable.

Current implementation concept:

```text
24-hour period
│
├──────────────┬──────────────┤
 previous       recent
 12 hours       12 hours
```

Example:

```text
Previous average = 20°C
Recent average   = 24°C

Change = +4°C
Direction = increasing
```

This should be interpreted precisely as:

> The recent 12-hour average is higher than the preceding 12-hour average.

It should not automatically be described as a universal long-term trend.

---

# 11. Trend Metrics

Current analytical trend functions include:

- Temperature trend
- PM2.5 trend

The trend result contains conceptually:

```text
city_id
city_name
country
previous_average
recent_average
change
direction
```

Possible directions:

```text
increasing
decreasing
stable
```

Future implementations can make trend windows more explicit for 7D and 30D analysis.

---

# 12. Scientific / Analytical Principle

CityAir should not manufacture scientific indices or warning classifications when established standards already exist.

Rule:

> Use established scientific methodologies wherever possible. Clearly label CityAir-specific calculations as CityAir calculations.

Examples:

- AQI → established AQI methodology
- Heat Index → established heat-stress methodology
- WBGT → established heat-stress methodology
- UTCI → established thermal-stress methodology
- Cyclone classification → established meteorological classification
- Severe-weather warnings → authoritative warning source

---

# 13. Weather Comfort / Thermal Indices

Do **not** create an arbitrary "CityAir Weather Comfort Score" without a defensible scientific methodology.

Weather does not have a universal ranking where:

```text
24°C = better than 28°C
```

for every person and purpose.

Potential established indices include:

## Heat Index

Combines temperature and relative humidity to estimate how hot conditions feel to the human body.

Useful for heat stress.

Not a universal pleasant-weather score.

## WBGT

Wet Bulb Globe Temperature is an established heat-stress index that incorporates environmental conditions including temperature, humidity, wind, and radiant/solar effects.

It requires inputs that CityAir does not currently ingest completely.

## UTCI

Universal Thermal Climate Index is designed to describe human thermal stress and incorporates several environmental variables.

It should only be implemented after verifying that required inputs are available and the implementation is scientifically correct.

### Product decision

Instead of:

```text
Weather Comfort Score: 83
```

prefer:

```text
Heat Index
Wind Chill
WBGT
UTCI
```

when the required inputs and methodology are available.

---

# 14. City Comparison

Support comparison of:

- minimum: 2 cities
- maximum: 4 cities

Example:

```text
Compare

[Bhopal ▼] [Delhi ▼] [Bengaluru ▼] [Mumbai ▼]
```

Metrics can include:

- Temperature
- Apparent temperature
- Humidity
- Wind
- Precipitation
- PM10
- PM2.5
- Ozone
- NO2
- AQI
- other available observations

Example table:

```text
Metric          Bhopal   Delhi   Bengaluru   Mumbai
Temperature     28°C     34°C      24°C        29°C
Humidity         62%      41%       72%         78%
PM2.5            32       91        18          45
AQI              78      172        42          96
Wind             11        8        14          19
```

---

# 15. Automatic Good / Bad Highlighting

The comparison interface should automatically highlight favorable and unfavorable values where a defensible interpretation exists.

Do NOT assume that lower is always better.

Example semantics:

```text
PM2.5
direction = lower is better

AQI
direction = lower is better

Temperature
direction = context-dependent

Humidity
direction = optimal range

Wind
direction = context-dependent / neutral

Precipitation
direction = context-dependent
```

This means the UI should not simply color the smallest number green.

Each metric should have explicit semantics.

Possible visual states:

```text
Best
Neutral
Worst
```

Only apply these when the underlying metric has a meaningful comparison rule.

---

# 16. Indian City Rankings

Create a dedicated Rankings page.

Primary ranking categories:

```text
Overall
Air Quality
Weather
```

And allow:

```text
Top
Worst
```

Example:

```text
CITY RANKINGS

Metric: Overall

Top cities
1. Bengaluru
2. Pune
3. Hyderabad
4. Chandigarh
5. Bhopal

Worst cities
1. ...
2. ...
3. ...
```

The application should clearly document how every ranking is calculated.

---

# 17. Air Quality Ranking

Air quality has a more defensible basis for ranking because AQI and pollutant concentrations have established interpretations.

Possible ranking approaches:

- AQI
- PM2.5
- PM10
- other pollutant-specific metrics

The UI should clearly state the metric and period being used.

Example:

```text
Rank by:
[ Air Quality ▼ ]

Metric:
[ AQI ▼ ]

Direction:
[ Best ▼ ]
```

---

# 18. Weather Ranking

Weather ranking requires more care.

There is no universal "best weather" value applicable to every user.

Do not claim that CityAir's weather ranking is an official meteorological ranking.

Possible future approach:

- rank using an established thermal-stress index when appropriate
- rank specific measurable weather properties separately
- clearly label any CityAir-derived ranking methodology
- document assumptions and thresholds

For example:

```text
Weather

Temperature
Humidity
Heat Index
Wind
Precipitation
```

Rather than pretending that a single arbitrary score represents universally good weather.

---

# 19. Overall Ranking

An overall ranking can eventually combine multiple established measures.

Conceptually:

```text
Air-quality component
        +
weather-related component
        ↓
overall ranking
```

But the weighting methodology must be explicitly defined before implementation.

Do not invent arbitrary weights without documenting and justifying them.

---

# 20. Severe Weather Page

Create a dedicated:

```text
Severe Weather
```

page.

Potential alert types:

- Thunderstorms
- Lightning
- Heavy rain
- Very heavy rain
- Extreme rain
- Strong winds
- Heat wave
- Cold wave
- Hail
- Dust storms
- Cyclones
- other officially published warnings

For India, the preferred authoritative source for official weather warnings is the India Meteorological Department (IMD).

The application should preserve the distinction between:

- forecast
- warning
- observed condition
- active event

Do not represent a forecast as an observation.

---

# 21. Severe Weather Interactive Map

The Severe Weather page should include an interactive map where feasible.

Users should be able to:

- zoom
- pan
- click a region
- click an alert
- filter alert types
- inspect severity
- inspect validity period
- view affected regions
- view cyclone tracks
- view forecast tracks

Conceptual structure:

```text
Severe Weather
│
├── Filters
│   ├── All
│   ├── Thunderstorm
│   ├── Heavy Rain
│   ├── Cyclone
│   └── Other warnings
│
├── Interactive India Map
│
└── Active Alerts
```

---

# 22. Warning Levels

Where the authoritative source provides warning levels, CityAir should preserve them rather than inventing a new danger score.

Example presentation:

```text
GREEN
No warning

YELLOW
Watch / Be updated

ORANGE
Alert / Be prepared

RED
Warning / Take action
```

The UI should identify the authoritative source and timestamp where appropriate.

---

# 23. Cyclone Tracking

Cyclones deserve specialized map treatment.

The map can show:

```text
Observed track
       ●
                 ●
                     ●──────●
                                     ●
                                     forecast
                   track
```

Potential cyclone information:

- cyclone name
- classification
- current position
- maximum sustained wind
- movement direction
- movement speed
- central pressure
- forecast track
- affected regions
- warning level
- last update

Where available, use authoritative meteorological cyclone classifications rather than creating CityAir categories.

---

# 24. Thunderstorm / Lightning Data

Do not assume the existing Open-Meteo weather code represents a dedicated lightning detection network.

Distinguish:

```text
Official warning
```

from:

```text
Observed lightning detection
```

They are different datasets.

If lightning detection data is added later, its source and coverage must be documented.

---

# 25. Map Technology

The interactive map should use real geographic boundaries and authoritative event locations/regions where available.

Do not invent geographic boundaries or alert locations.

Map functionality should prioritize:

- correct geography
- readable labels
- zoom/pan
- click interaction
- filtering
- accessible controls
- responsive behavior

Potential map stack can be selected during implementation based on project requirements.

---

# 26. Dashboard Layout

Proposed high-level dashboard:

```text
┌────────┬───────────────────────────────────────────────────┐
│        │                                                   │
│ CITYAIR│  Your location                                   │
│        │  Bhopal, Madhya Pradesh                          │
│ Home   │                                                   │
│        │  28°C       PM2.5        AQI                      │
│ Cities │                                                   │
│        │                                                   │
│ Compare│  Weather history                                  │
│        │  [24H] [7D] [30D]                                │
│ Rankings│                                                  │
│        │  ┌─────────────────────────────────────────────┐  │
│ History│  │                                             │  │
│        │  │              Temperature                    │  │
│ Severe │  │                                             │  │
│ Weather│  └─────────────────────────────────────────────┘  │
│        │                                                   │
│ Settings│ ┌─────────────────────────────────────────────┐ │
│        │ │              PM2.5 / AQI                     │ │
└────────┴─┴─────────────────────────────────────────────┴─┘
```

---

# 27. Frontend UX Principles

The UI should be:

- sleek
- information-dense without being cluttered
- responsive
- accessible
- keyboard-friendly
- consistent
- visually calm
- data-first

Avoid:

- excessive gradients
- excessive animations
- decorative cards for everything
- huge empty areas
- overly rounded "SaaS template" styling
- inconsistent icons
- fake scientific scores
- unexplained rankings
- misleading weather/alert visualizations

---

# 28. Data Integrity Principles

CityAir should distinguish between:

### Observed

Data actually stored from an observation.

### Forecast

Predicted future conditions.

### Warning

An official warning issued by an authoritative source.

### Analytical calculation

A value calculated by CityAir from stored data.

The UI should make these distinctions clear.

---

# 29. Recommended Frontend Feature Roadmap

## Phase 1 — Design system

- Install/configure Lucide
- Establish theme tokens
- Light theme
- Dark theme
- Application typography
- Sidebar
- navigation
- reusable cards
- buttons
- selects
- status indicators

## Phase 2 — Dashboard

- user's city
- current weather
- current air quality
- weather-aware background
- 24H charts
- responsive layout

## Phase 3 — Historical analytics

- 24H hourly
- 7D daily
- 30D daily
- temperature chart
- PM2.5 chart
- AQI chart
- historical metric selection

## Phase 4 — City comparison

- 2–4 cities
- comparison table
- visual highlighting
- metric semantics
- comparison charts

## Phase 5 — Rankings

- Indian cities
- top / worst
- air quality ranking
- weather-related ranking
- documented methodology
- overall ranking only after methodology is defensible

## Phase 6 — Severe weather

- IMD warning integration
- alert page
- interactive India map
- thunderstorm warnings
- heavy rain warnings
- cyclone information
- cyclone tracks
- alert filters

## Phase 7 — Polish

- responsive/mobile navigation
- accessibility
- loading states
- empty states
- error states
- animation refinement
- performance
- visual consistency

---

# 30. Product Architecture

```text
                         CITYAIR METRICS
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ↓                 ↓                 ↓
          Dashboard          Analytics       Severe Weather
              │                 │                 │
              │          ┌──────┼──────┐          │
              │          ↓      ↓      ↓          │
              │         24H    7D     30D         │
              │          │      │      │           │
              │          └──────┼──────┘           │
              │                 │                  │
              └─────────────────┼──────────────────┘
                                ↓
                             FastAPI
                                ↓
                          Analytics Layer
                                ↓
                           PostgreSQL
                                ↓
                         Ingestion Pipeline
                                ↓
                         External Sources
```

---

# 31. Core Product Rule

CityAir should combine:

```text
real observations
+
established scientific indices
+
official warnings
+
transparent CityAir analytics
```

It should avoid:

```text
arbitrary scores
+
unexplained rankings
+
invented warning classifications
+
fake precision
```

This is important both for technical credibility and for the portfolio/recruiter value of the project.

---

# 32. Current Backend Capability

Already implemented:

- PostgreSQL data model
- weather ingestion
- air-quality ingestion
- pipeline run tracking
- latest weather analytics
- latest air-quality analytics
- city snapshot analytics
- average weather analytics
- average air-quality analytics
- temperature trend
- PM2.5 trend
- historical weather query
- historical air-quality query
- FastAPI endpoints
- Pydantic response models
- API tests
- React/TypeScript frontend scaffold
- API-backed React dashboard
- CORS for local frontend/backend development

Current historical backend supports a configurable hour window, with 24 hours as the initial/default use case.

Next backend work should extend this cleanly for daily 7-day and 30-day analytical views.

