| Column Name        | Data Type (Processed) | Derived From        | Description |
|--------------------|----------------------|---------------------|-------------|
| `DayOfMonth`       | INT                  | `DayOfMonth`        | Day of month as integer; preserved from raw. |
| `DayOfWeek`        | INT                  | `DayOfWeek`         | Day of week (1–7) as integer; preserved from raw |
| `FlightDate`       | DATE                 | `Year`,`Month`,`DayOfMonth` | Calendar flight date constructed from year, month, and day-of-month. |
| `UniqueCarrier`    | VARCHAR(10)          | `UniqueCarrier`     | Uppercased, trimmed marketing carrier code. |
| `FlightNum`        | INT                  | `FlightNum`         | Cleaned integer flight number. |
| `TailNum`          | VARCHAR(20)          | `TailNum`           | Trimmed aircraft registration code. |
| `Origin`           | VARCHAR(10)          | `Origin`            | Uppercased, trimmed origin airport IATA code.|
| `Dest`             | VARCHAR(10)          | `Dest`              | Uppercased, trimmed destination airport IATA code.|
| `DepTime`          | INT                  | `DepTime`           | Actual departure time (HHMM) cast to integer; invalid/missing retained as null where present. |
| `CRSDepTime`       | INT                  | `CRSDepTime`        | Scheduled departure time (HHMM) cast to integer. |
| `ArrTime`          | INT                  | `ArrTime`           | Actual arrival time (HHMM) cast to integer. |
| `CRSArrTime`       | INT                  | `CRSArrTime`        | Scheduled arrival time (HHMM) cast to integer. |
| `ActualElapsedTime`| INT                  | `ActualElapsedTime` | Actual elapsed time in minutes|
| `CRSElapsedTime`   | INT                  | `CRSElapsedTime`    | Scheduled elapsed time in minutes. |
| `AirTime`          | INT                  | `AirTime`           | Airborne time in minutes. |
| `ArrDelay`         | INT (non-null)       | `ArrDelay`          | Arrival delay in minutes; nulls replaced with 0 for aggregation robustness. |
| `DepDelay`         | INT (non-null)       | `DepDelay`          | Departure delay in minutes; nulls replaced with 0. |
| `Distance`         | INT                  | `Distance`          | Great-circle distance in miles; filtered to strictly positive values. |
| `TaxiIn`           | INT                  | `TaxiIn`            | Taxi-in time in minutes. |
| `TaxiOut`          | INT                  | `TaxiOut`           | Taxi-out time in minutes. |
| `Cancelled`        | BOOLEAN              | `Cancelled`         | Boolean flag: `TRUE` if `Cancelled > 0`, else `FALSE`. |
| `CancellationCode` | VARCHAR(10)          | `CancellationCode`  | Uppercased, trimmed cancellation reason code. |
| `Diverted`         | BOOLEAN              | `Diverted`          | Boolean flag: `TRUE` if `Diverted > 0`, else `FALSE`. |
| `CarrierDelay`     | INT (non-null)       | `CarrierDelay`      | Carrier-attributed delay minutes; nulls replaced with 0. |
| `WeatherDelay`     | INT (non-null)       | `WeatherDelay`      | Weather-attributed delay minutes; nulls replaced with 0. |
| `NASDelay`         | INT (non-null)       | `NASDelay`          | National Aviation System–attributed delay minutes; nulls replaced with 0. |
| `SecurityDelay`    | INT (non-null)       | `SecurityDelay`     | Security-attributed delay minutes; nulls replaced with 0. |
| `LateAircraftDelay`| INT (non-null)       | `LateAircraftDelay` | Late-arriving aircraft–attributed delay minutes; nulls replaced with 0. |
| `Dep_Scheduled_TS` | TIMESTAMP            | `FlightDate`,`CRSDepTime` | Scheduled departure timestamp at origin in local time; built by combining `FlightDate` and padded `CRSDepTime` (HH:MM). |
| `IsDelayed`        | BOOLEAN              | `ArrDelay`          | On-time performance flag; `TRUE` if arrival delay strictly greater than 15 minutes, otherwise `FALSE` (DOT on-time threshold). |
| `TotalDelay`       | INT                  | `ArrDelay`,`DepDelay` | Aggregate delay metric defined as `DepDelay + ArrDelay`, in minutes. |