-- #     'tripduration': line['Trip Duration'],
--                 #     'starttime': line['Start Time'],
--                 #     'stoptime': line['Stop Time'],
--                 #     'start station id': line['Start Station ID'],
--                 #     'start station name': line['Start Station Name'],
--                 #     'start station latitude': line['Start Station Latitude'],
--                 #     'start station longitude': line['Start Station Longitude'],
--                 #     'end station id': line['End Station ID'],
--                 #     'end station name': line['End Station Name'],
--                 #     'end station latitude': line['End Station Latitude'],
--                 #     'end station longitude': line['End Station Longitude'],
--                 #     'bikeid': line['Bike ID'],
--                 #     'birth year': line['Birth Year'],
--                 #     'gender': line['Gender'],

CREATE TABLE records (
    start_time VARCHAR(30),
    start_station VARCHAR(100),
    start_station_id VARCHAR(100),
    birth_year VARCHAR(100),
    trip_duration VARCHAR(100) 
);


CREATE TABLE stations (
    stopname VARCHAR(100),
    longitude VARCHAR(100),
    latitude VARCHAR(100),
    id VARCHAR(100) 
);

-- File path needs to be modified
\COPY records(start_time, start_station, start_station_id, birth_year, trip_duration) FROM '/Users/zejun/Documents/828d/hw3/backend/server/sql/bike_records.csv' DELIMITER ',' CSV;

\COPY stations FROM '/Users/zejun/Documents/828d/hw3/backend/server/sql/stops.csv' DELIMITER ',' CSV;
