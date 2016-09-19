queries = ["" for i in range(0, 11)]

### 0. List all airport codes and their cities. Order by the city name in the increasing order.
### Output column order: airportid, city

queries[0] = """
select airportid, city
from airports
order by city;
"""


### 1. Write a query to find the names of the customers whose names are at least 15 characters long, and the second letter in the  name is "l".
### Order by name.
queries[1] = """
select name
from customers
where char_length(name) >= 15
    and substring(name from 2 for 1) = 'l'
order by name;
"""


### 2. Write a query to find any customers who flew on their birthday.  Hint: Use "extract" function that operates on the dates.
### Order output by Customer Name.
### Output columns: all columns from customers
queries[2] = """
select customers.*
from customers
natural join flewon
where extract(month from birthdate) = extract(month from flightdate)
    and extract(day from birthdate) = extract(day from flightdate)
order by name;
"""


### 3. Write a query to generate a list: (source_city, source_airport_code, dest_city, dest_airport_code, number_of_flights) for all source-dest pairs with at least 2 flights.
### Order first by number_of_flights in decreasing order, then source_city in the increasing order, and then dest_city in the increasing order.
### Note: You must generate the source and destination cities along with the airport codes.
queries[3] = """
with source_cities as (
    select city as source_city, source, dest, count(dest) as number_of_flights
    from flights
    inner join airports
        on airportid = source
    group by source, dest, source_city
    having count(dest) >= 2
),
dest_cities as (
    select city as dest_city, source, dest, count(dest) as number_of_flights
    from flights
    inner join airports
        on airportid = dest
    group by source, dest, dest_city
    having count(dest) >= 2
)
select s.source_city, s.source as source_airport_code, d.dest_city,
    s.dest as dest_airport_code, s.number_of_flights
from source_cities s
natural join dest_cities d
order by s.number_of_flights desc, s.source_city, d.dest_city;
"""


### 4. Find the name of the airline with the maximum number of customers registered as frequent fliers.
### Output only the name of the airline. If multiple answers, order by name.
queries[4] = """
with frequent_flier_counts as (
    select airlines.name, count(frequentflieron) as frequent_flier_count
    from airlines
    inner join customers
        on airlineid = frequentflieron
    group by airlines.name
),
max_frequent_fliers as (
    select max(frequent_flier_count) as frequent_flier_count
    from frequent_flier_counts
)
select name as airline_name
from frequent_flier_counts
natural join max_frequent_fliers
order by name;
"""


### 5. For all flights from OAK to ATL, list the flight id, airline name, and the
### duration in hours and minutes. So the output will have 4 fields: flightid, airline name,
### hours, minutes. Order by flightid.
queries[5] = """
select flightid, name as airline_name,
    abs(extract(hour from local_arrival_time) -
        extract(hour from local_departing_time)) as hours,
    abs(extract(minute from local_arrival_time) -
        extract(minute from local_departing_time)) as minutes
from airlines
natural join flights
where source = 'OAK' and dest = 'ATL'
order by flightid;
"""


### 6. Write a query to find all the empty flights (if any); recall that all the flights listed
### in the flights table are daily, and that flewon contains information for a period of 10
### days from Jan 1 to Jan 10, 2010. For each such flight, list the flightid and the date.
### Order by flight id in the increasing order, and then by date in the increasing order.
queries[6] = """
with flight_ids_and_dates as (
    with unique_dates as (
        select flightdate
        from flewon
        group by flightdate
    )
    select flightid, flightdate
    from flights, unique_dates
    group by flightid, flightdate
),
frequent_flier_counts as (
    select flightid, flightdate, count(customerid) as passengers
    from flewon
    group by flightid, flightdate
)
select f.flightid, f.flightdate
from flight_ids_and_dates f
left join frequent_flier_counts ffc
    on f.flightid = ffc.flightid
    and f.flightdate = ffc.flightdate
where passengers is NULL
order by f.flightid, f.flightdate;
"""


### 7. Write a query to generate a list of customers who don't list Southwest as their frequent flier airline, but
### actually flew the most (by number of flights) on that airline.
### Output columns: customerid, customer_name
### Order by: customerid
queries[7] = """
with nonsouthewest_customers as (
    select customerid, name
    from customers
    where frequentflieron <> 'SW'
),
took_southwest_flights_most as (
    with airline_count as (
        select customerid, airlineid, count(airlineid) as count
        from flewon
        natural join flights
        group by customerid, airlineid
    ),
    max_airline_count as (
        select customerid, max(count) as count
        from airline_count
        group by customerid
    )
    select customerid
    from airline_count
    natural join max_airline_count
    where airlineid = 'SW'
)
select n.customerid, name
from nonsouthewest_customers n
natural join took_southwest_flights_most
order by customerid;
"""


### 8. Write a query to generate a list of customers who flew twice on two consecutive days, but did
### not fly otherwise in the 10 day period. The output should be simply a list of customer ids and
### names. Make sure the same customer does not appear multiple times in the answer.
### Order by the customer name.
queries[8] = """
with flew_twice as (
    select customerid, name
    from flewon
    natural join customers
    group by customerid, name
    having count(flightdate) = 2
)
select customerid, name
from flewon
natural join flew_twice
group by customerid, name
having max(flightdate) - min(flightdate) = 1
order by name;
"""


### 9. Write a query to find the names of the customer(s) who visited the most cities in the 10 day
### duration. A customer is considered to have visited a city if he/she took a flight that either
### departed from the city or landed in the city.
### Output columns: name
### Order by: name
queries[9] = """
with total_cities_visited as (
    select customerid, source as city
    from flewon
    natural join flights
    group by customerid, source
    union
    select customerid, dest as city
    from flewon
    natural join flights
    group by customerid, dest
),
city_count as (
    select name, count(city) as count
    from total_cities_visited
    natural join customers
    group by name
),
max_city_count as (
    select max(count) as count
    from city_count
)
select name
from city_count
natural join max_city_count
order by name;
"""


### 10. Write a query that outputs a list: (AirportID, Airport-rank), where we rank the airports
### by the total number of flights that depart that airport. So the airport with the maximum number
### of flights departing gets rank 1, and so on. If two airports tie, then they should
### both get the same rank, and the next rank should be skipped.
### Order the output in the increasing order by rank.
queries[10] = """
with airport_flight_counts as (
    select source as airportid, count(source) as flight_count
    from flights
    group by source
)
select airportid, flight_count, rank() over (order by flight_count desc) as rank
from airport_flight_counts
order by rank;
"""
