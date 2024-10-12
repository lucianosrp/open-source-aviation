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

## Other Lists
* [awesome-flying](https://github.com/bauidch/awesome-flying) - A curated list of flying/aviation tools

----

# Data Metadata

| name                                                                                                                      | last_modified       | row_count   |
|:--------------------------------------------------------------------------------------------------------------------------|:--------------------|:------------|
| [runways.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/runways.csv)                         | 2024-10-12 07:53:29 | 46,269      |
| [airports.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airports.csv)                       | 2024-10-11 07:53:30 | 80,854      |
| [airport-comments.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airport-comments.csv)       | 2024-10-07 07:53:31 | 15,482      |
| [airport-frequencies.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airport-frequencies.csv) | 2024-09-24 07:53:30 | 29,428      |
| [regions.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/regions.csv)                         | 2024-09-16 07:53:29 | 3,944       |
| [navaids.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/navaids.csv)                         | 2024-08-23 07:53:30 | 11,020      |
| [countries.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/countries.csv)                     | 2022-11-03 07:53:39 | 248         |
| [airports.dat](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat)                           | 2019-05-13 11:54:02 | 7,697       |
| [airports-extended.dat](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports-extended.dat)         | 2019-05-13 11:54:02 | 12,667      |
| [airlines.dat](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat)                           | 2017-02-02 11:32:12 | 6,161       |
| [routes.dat](https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat)                               | 2017-02-02 11:32:12 | 67,662      |