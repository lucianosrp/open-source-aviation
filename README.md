# Open-source Aviation ✈️📈

A curated list of open-source aviation projects, tools and datasets.

[![Update Metadata](https://github.com/lucianosrp/open-source-aviation/actions/workflows/update-metadata.yaml/badge.svg)](https://github.com/lucianosrp/open-source-aviation/actions/workflows/update-metadata.yaml)
[![License: CC0-1.0](https://img.shields.io/badge/license-CC0--1.0-blue.svg)](LICENSE)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> [!NOTE]
> Still work-in-progress, feel free to fork and contribute!
> See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add an entry.

## Contents

* [Data](#data)
  * [ADS-B Data](#ads-b-data)
  * [Airport Data](#airport-data)
  * [Weather Data](#weather-data)
  * [AIXM](#aixm)
* [Software](#software)
  * [Tools and Libraries](#tools-and-libraries)
  * [OSINT](#osint)
  * [Sims](#sims)
* [Learning](#learning)
  * [Guide](#guide)
* [Other Lists](#other-lists)
* [Data Metadata](#data-metadata)

## Data

Datasets and data sources. Every `.csv` and `.dat` file linked below is tracked
in the [Data Metadata](#data-metadata) table, refreshed daily, so you can check
how current a file is before downloading it.

### ADS-B Data

* [ADS-B Exchange](https://www.adsbexchange.com/) - Community-driven ADS-B network, offers free sample data and freemium Rest APIs

### Airport Data

Airport, runway and navigation reference data. Four independent sources, listed
newest-maintained first.

#### [OurAirports.com](https://ourairports.com/)

Actively maintained and the most complete of the four. Updated daily.

* [ourairports.com](https://ourairports.com/) - Community-driven airport database which includes geo coordinates, airport names and more.
* [airports.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airports.csv) - Raw CSV file of OurAirports.com, 78K+ airports
* [runways.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/runways.csv) - Runways information. Including length, width, altitude and more.
* [airport-frequencies.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airport-frequencies.csv) - MHZ Airport Frequencies.
* [countries.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/countries.csv) - Additional Country data
* [regions.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/regions.csv) - Additional Region Data
* [navaids.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/navaids.csv) - Radio navigation aids, with frequency, type and associated airport.
* [airport-comments.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airport-comments.csv) - Community comments

#### [logibook](https://logibook.dataint.net/en/countries)

* [logibook airports](https://logibook.dataint.net/en/countries) - Browsable reference over OurAirports data: per-airport runway & taxiway layout diagrams (rendered from OpenStreetMap), radio frequencies, runway dimensions/surface/heading, plus cross-links to the nearest ports, cities and trade zones by distance. Per-country roll-ups (e.g. [Cyprus](https://logibook.dataint.net/en/countries/cyprus/airports)) add World Bank air-transport indicators. 25 languages, no registration.

#### [aviowiki](https://aviowiki.com/)

* [free_airports.json.zip](https://exports.aviowiki.com/free_airports.json.zip) - 32K structured airport data

#### [openflights.org](https://openflights.org/)

Wider coverage of airlines and routes than the others, but unmaintained.

* [airports.dat](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat) - Airport data, might be outdated
* [airports-extended.dat](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports-extended.dat) - Airports, train stations and ferry terminals, including user contributions
* [airlines.dat](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat) - Airline records with IATA/ICAO codes, callsigns and country.
* [routes.dat](https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat) - Airline route pairs, including stops and equipment.

> [!IMPORTANT]
> The OpenFlights `.dat` exports have no header row and have not been updated
> upstream since 2019. Read them with explicit column names.

### Weather Data

* [NOAA's METAR](https://tgftp.nws.noaa.gov/data/observations/metar/stations/) - Up-to-date METARs, for a specific station you can add the {ICAO}.TXT at the end of the url (e.g. [EGLL](https://tgftp.nws.noaa.gov/data/observations/metar/stations/EGLL.TXT))
* [AVWX-Engine](https://github.com/avwx-rest/avwx-engine) - Aviation Weather parsing engine. METAR & TAF

### AIXM

[AIXM](https://aixm.aero/) is the ICAO/EUROCONTROL XML standard for exchanging
aeronautical information (airspaces, routes, procedures).

#### [delorean-aixm.io](https://delorean-aixm.io/)

* [delorean-aixm](https://github.com/3l-gee/delorean-aixm) - ETL tool to manage AIXM dataset with postgresql

## Software

### Tools and Libraries

* [traffic-viz](https://github.com/xoolive/traffic) - A toolbox for processing and analysing air traffic data
* [pitot](https://github.com/open-aviation/pitot) - A toolbox for aeronautic calculations
* [openap-top](https://github.com/junzis/openap-top) - Open flight trajectory optimizer built with non-linear optimal control method
* [aeronautical_charting](https://github.com/antoniolocandro/aeronautical_charting) - Stylesheets for aeronautical charting
* [qOLS](https://github.com/FLYGHT7/qOLS) - Qgis extension to create Obstacle Limitation Surfaces

### OSINT

* [skytrack](https://github.com/ANG13T/skytrack) - A planespotting and aircraft OSINT tool made using Python

### Sims

* [FlightGear](https://www.flightgear.org/) - Open-source flight simulator
* [AirTrafficSim](https://github.com/HKUST-OCTAD-LAB/AirTrafficSim) - Web-based air traffic simulation and visualization platform for ATM research.

## Learning

### Guide

* [How to take Aerial Photographs of Hong Kong Disneyland](https://github.com/lincolnlychan/How-to-take-Aerial-Photographs-of-Hong-Kong-Disneyland) - Tutorial/Guide on How to take Aerial Photographs of Hong Kong Disneyland
* [Aircraft Flight Mechanics](https://www.aircraftflightmechanics.com/) - Guide on Aircraft Flight Mechanics

## Other Lists

* [awesome-flying](https://github.com/bauidch/awesome-flying) - A curated list of flying/aviation tools

## Data Metadata

Generated table, **do not edit by hand**. Every `raw.githubusercontent.com` link
above ending in `.csv` or `.dat` is picked up automatically, so adding a dataset
to the lists above is all it takes to get it tracked here.

| column | meaning |
|:---|:---|
| `last_modified` | Author date (UTC) of the most recent upstream commit touching the file. |
| `row_count` | Data records, excluding the header row where the format has one. |
| `size` | Uncompressed size of the download. |

Refreshed daily by [`update-metadata.yaml`](.github/workflows/update-metadata.yaml);
to reproduce it locally see
[CONTRIBUTING.md](CONTRIBUTING.md#refreshing-the-metadata-table).

<!-- data-metadata:start -->
| name                                                                                                                      | last_modified       | row_count |     size |
|:--------------------------------------------------------------------------------------------------------------------------|:--------------------|----------:|---------:|
| [airport-comments.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airport-comments.csv)       | 2026-08-20 01:53:15 |    16,385 |   4.5 MB |
| [airports.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airports.csv)                       | 2026-08-20 01:53:15 |    85,936 |  12.1 MB |
| [runways.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/runways.csv)                         | 2026-08-19 01:53:13 |    48,180 |   3.8 MB |
| [airport-frequencies.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airport-frequencies.csv) | 2026-08-18 01:53:14 |    30,339 |   1.2 MB |
| [regions.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/regions.csv)                         | 2026-08-15 01:53:13 |     3,987 | 473.9 KB |
| [navaids.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/navaids.csv)                         | 2026-07-30 01:53:13 |    11,008 |   1.5 MB |
| [countries.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/countries.csv)                     | 2025-02-28 02:53:11 |       249 |  24.0 KB |
| [airports-extended.dat](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports-extended.dat)         | 2019-05-13 11:54:02 |    12,668 |   1.6 MB |
| [airports.dat](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat)                           | 2019-05-13 11:54:02 |     7,698 |   1.1 MB |
| [airlines.dat](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat)                           | 2017-02-02 11:32:12 |     6,162 | 387.6 KB |
| [routes.dat](https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat)                               | 2017-02-02 11:32:12 |    67,663 |   2.3 MB |
<!-- data-metadata:end -->

## License

Everything in this repository -- the curated list and the tooling under
`scripts/`, `tests/` and `.github/` -- is released under
[CC0-1.0](LICENSE), a public domain dedication. No attribution required.

Note that CC0 waives copyright but expressly does not license patent or
trademark rights, and is not OSI-approved.

Linked projects and datasets carry their own licences, check each before use.
