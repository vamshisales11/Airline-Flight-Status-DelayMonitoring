| Column Name        | Data Type (Processed) | Derived From        | Description |
|--------------------|----------------------|---------------------|-------------|
| `DayOfMonth`       | INT                  | `DayOfMonth`        | Day of month as integer; preserved from raw.[web:47][web:53] |
| `DayOfWeek`        | INT                  | `DayOfWeek`         | Day of week (1–7) as integer; preserved from raw.[web:47][web:53] |
| `FlightDate`       | DATE                 | `Year`,`Month`,`DayOfMonth` | Calendar flight date constructed from year, month, and day-of-month.[web:47][web:53] |
| `UniqueCarrier`    | VARCHAR(10)          | `UniqueCarrier`     | Uppercased, trimmed marketing carrier code.[web:47][web:50] |
| `FlightNum`        | INT                  | `FlightNum`         | Cleaned integer flight number.[web:47][web:53] |
| `TailNum`          | VARCHAR(20)          | `TailNum`           | Trimmed aircraft registration code.[web:50] |
| `Origin`           | VARCHAR(10)          | `Origin`            | Uppercased, trimmed origin airport IATA code.[web:47][web:50] |
| `Dest`             | VARCHAR(10)          | `Dest`              | Uppercased, trimmed destination airport IATA code.[web:47][web:50] |
| `DepTime`          | INT                  | `DepTime`           | Actual departure time (HHMM) cast to integer; invalid/missing retained as null where present.[web:47][web:53] |
| `CRSDepTime`       | INT                  | `CRSDepTime`        | Scheduled departure time (HHMM) cast to integer.[web:47][web:53] |
| `ArrTime`          | INT                  | `ArrTime`           | Actual arrival time (HHMM) cast to integer.[web:47][web:53] |
| `CRSArrTime`       | INT                  | `CRSArrTime`        | Scheduled arrival time (HHMM) cast to integer.[web:47][web:53] |
| `ActualElapsedTime`| INT                  | `ActualElapsedTime` | Actual elapsed time in minutes.[web:50][web:53] |
| `CRSElapsedTime`   | INT                  | `CRSElapsedTime`    | Scheduled elapsed time in minutes.[web:47][web:53] |
| `AirTime`          | INT                  | `AirTime`           | Airborne time in minutes.[web:50][web:53] |
| `ArrDelay`         | INT (non-null)       | `ArrDelay`          | Arrival delay in minutes; nulls replaced with 0 for aggregation robustness.[web:50][web:62] |
| `DepDelay`         | INT (non-null)       | `DepDelay`          | Departure delay in minutes; nulls replaced with 0.[web:50][web:62] |
| `Distance`         | INT                  | `Distance`          | Great-circle distance in miles; filtered to strictly positive values.[web:50][web:53] |
| `TaxiIn`           | INT                  | `TaxiIn`            | Taxi-in time in minutes.[web:50][web:53] |
| `TaxiOut`          | INT                  | `TaxiOut`           | Taxi-out time in minutes.[web:50][web:53] |
| `Cancelled`        | BOOLEAN              | `Cancelled`         | Boolean flag: `TRUE` if `Cancelled > 0`, else `FALSE`.[web:47][web:50] |
| `CancellationCode` | VARCHAR(10)          | `CancellationCode`  | Uppercased, trimmed cancellation reason code.[web:47][web:53] |
| `Diverted`         | BOOLEAN              | `Diverted`          | Boolean flag: `TRUE` if `Diverted > 0`, else `FALSE`.[web:47][web:50] |
| `CarrierDelay`     | INT (non-null)       | `CarrierDelay`      | Carrier-attributed delay minutes; nulls replaced with 0.[web:50][web:62] |
| `WeatherDelay`     | INT (non-null)       | `WeatherDelay`      | Weather-attributed delay minutes; nulls replaced with 0.[web:50][web:62] |
| `NASDelay`         | INT (non-null)       | `NASDelay`          | National Aviation System–attributed delay minutes; nulls replaced with 0.[web:50][web:62] |
| `SecurityDelay`    | INT (non-null)       | `SecurityDelay`     | Security-attributed delay minutes; nulls replaced with 0.[web:50][web:62] |
| `LateAircraftDelay`| INT (non-null)       | `LateAircraftDelay` | Late-arriving aircraft–attributed delay minutes; nulls replaced with 0.[web:50][web:62] |
| `Dep_Scheduled_TS` | TIMESTAMP            | `FlightDate`,`CRSDepTime` | Scheduled departure timestamp at origin in local time; built by combining `FlightDate` and padded `CRSDepTime` (HH:MM).[web:26][web:35] |
| `IsDelayed`        | BOOLEAN              | `ArrDelay`          | On-time performance flag; `TRUE` if arrival delay strictly greater than 15 minutes, otherwise `FALSE` (DOT on-time threshold).[web:51][web:52] |
| `TotalDelay`       | INT                  | `ArrDelay`,`DepDelay` | Aggregate delay metric defined as `DepDelay + ArrDelay`, in minutes.[web:26][web:29] |