# Open-source Aviation ✈️📈
A list of open-source aviation projects and data.

> [!NOTE]
> Still work-in-progress, feel free to fork and contribute!

## Content
* [ADS-B Data](#ads-b-data)
* [Airport Data](#airport-data)
* [Weather Data](#weather-data)
* [OSINT](#osint)
* [Tools and Libraries](#tools-and-libraries)
* [Other Lists](#other-lists)


## ADS-B Data
* [ADS-B Exchange](https://www.adsbexchange.com/) - Community-driven ADS-B network, offers free sample data and freemium Rest APIs


## Airport Data
#### [OurAirports.com](https://ourairports.com/)
* [ourairports.com](https://ourairports.com/) - Community-driven airport database which includes geo coordinates, airport names and more.
* [airports.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airports.csv) - Raw CSV file of OurAirports.com,  78K+ airports
* [runways.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/runways.csv) - Runways information. Including length, width, altitude and more.
* [airport-frequencies.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airport-frequencies.csv) - MHZ Airport Frequencies.
* [countries.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/countries.csv) - Additional Country data
* [regions.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/regions.csv) - Additional Region Data
* [navaids.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/navaids.csv)
* [airport-comments.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airport-comments.csv) - Community comments

#### [openflights.org](https://openflights.org/)
* [airports.dat](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat) - Airport data, might be outdated
* [airports-extended.dat](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports-extended.dat) - Airports, train stations and ferry terminals, including user contributions
* [airlines.dat](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat)
* [routes.dat](https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat)

#### [aviowiki](https://aviowiki.com/)
* [free_airports.json.zip](https://exports.aviowiki.com/free_airports.json.zip) - 32K structured airport data

## Weather Data
* [NOAA's METAR](https://tgftp.nws.noaa.gov/data/observations/metar/stations/) - Up-to-date METARs, for a specific station you can add the {ICAO}.TXT at the end of the url (e.g. [EGLL](https://tgftp.nws.noaa.gov/data/observations/metar/stations/EGLL.TXT))
* [AVWX-Engine](https://github.com/avwx-rest/avwx-engine) - Aviation Weather parsing engine. METAR & TAF

## OSINT
* [skytrack](https://github.com/ANG13T/skytrack) - A planespotting and aircraft OSINT tool made using Python

## Tools and Libraries
* [traffic-viz](https://github.com/xoolive/traffic) - A toolbox for processing and analysing air traffic data
* [pitot](https://github.com/open-aviation/pitot) - A toolbox for aeronautic calculations
* [openap-top](https://github.com/junzis/openap-top) - Open flight trajectory optimizer built with non-linear optimal control method
* [aeronautical_charting](https://github.com/antoniolocandro/aeronautical_charting) - Stylesheets for aeronautical charting
* [qOLS](https://github.com/FLYGHT7/qOLS) - Qgis extension to create Obstacle Limitation Surfaces

## AIXM
#### [delorean-aixm.io](https://delorean-aixm.io/)
 * [delorean-aixm](https://github.com/3l-gee/delorean-aixm) - ETL tool to manage AIXM dataset with postgresql

## Sims
* [AirTrafficSim](https://github.com/HKUST-OCTAD-LAB/AirTrafficSim) - Web-based air traffic simulation and visualization platform for ATM research.

## Other Lists
* [awesome-flying](https://github.com/bauidch/awesome-flying) - A curated list of flying/aviation tools

----

# Data Metadata

| name                                                                                                                      | last_modified       | row_count   |
|:--------------------------------------------------------------------------------------------------------------------------|:--------------------|:------------|
| [airports.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airports.csv)                       | 2026-01-18 02:53:11 | 84,442      |
| [runways.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/runways.csv)                         | 2026-01-18 02:53:11 | 47,509      |
| [airport-frequencies.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airport-frequencies.csv) | 2026-01-18 02:53:11 | 30,199      |
| [airport-comments.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airport-comments.csv)       | 2026-01-18 02:53:11 | 15,852      |
| [regions.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/regions.csv)                         | 2025-11-28 15:04:50 | 3,942       |
| [navaids.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/navaids.csv)                         | 2025-03-02 02:53:11 | 11,010      |
| [countries.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/countries.csv)                     | 2025-02-28 02:53:11 | 249         |
| [airports.dat](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat)                           | 2019-05-13 11:54:02 | 7,697       |
| [airports-extended.dat](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports-extended.dat)         | 2019-05-13 11:54:02 | 12,667      |
| [airlines.dat](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat)                           | 2017-02-02 11:32:12 | 6,161       |
| [routes.dat](https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat)                               | 2017-02-02 11:32:12 | 67,662      |