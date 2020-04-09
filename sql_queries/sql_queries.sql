-- Price Tracker! --
--Queries to be used for the project--

--what was the price of a good on a day?--
SELECT price 
FROM Oil 
WHERE Oil.dateID = 19990605
/* we can replace Oil with another good and the data id with another date. */

--get all of the prices of specific goods from the last x days--
--suppose that the date x days ago has already been calculated, call it --
SELECT o.price as oil_price, b.price as bitcoin_price
FROM Oil o 
FULL OUTER JOIN Bitcoin b 
ON o.dateID = b.dateID
WHERE dateID >= x_days_ago



--given a day, was this a good day, or a bad day?, good day if above average, bad day if below--

--in the last 10 days, have prices been trending down or up?--
