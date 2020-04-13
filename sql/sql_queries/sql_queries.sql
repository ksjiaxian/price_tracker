-- Price Tracker! --
--Queries to be used for the project--

--what was the price of a good on a day?--
SELECT price 
FROM Oil 
WHERE Oil.dateID = 19991231
/* we can replace Oil with another good and the data id with another date. */

--get all of the prices of specific goods from the last x days--
--suppose that the date x days ago has already been calculated, call it --
SELECT o.price as oil_price, b.price as bitcoin_price
FROM Oil o 
FULL OUTER JOIN Bitcoin b 
ON o.dateID = b.dateID
WHERE dateID >= x_days_ago


--given a day, was this a good day?--
--suppose that in our application, we already have an average--
--good days are where everything is above average--

SELECT 1
FROM Avocado a 
JOIN Oil o ON a.dateID = o.dateID
JOIN Bitcoin b ON o.dateID = b.dateID
JOIN Stocks s ON b.dateID = s.dateID
WHERE o.dateID = 19991231
AND a.price > avocado_average
AND o.price > oil_average
AND b.price > bitcoin_average
AND s.super_stock_index > 0

--given a day, was this a bad day?--
--bad days are where everything is below average--

SELECT -1
FROM Avocado a 
JOIN Oil o ON a.dateID = o.dateID
JOIN Bitcoin b ON o.dateID = b.dateID
JOIN Stocks s ON b.dateID = s.dateID
WHERE o.dateID = 19991231
AND a.price < avocado_average
AND o.price < oil_average
AND b.price < bitcoin_average
AND s.super_stock_index < 0


--in the last x days, have prices been trending down or up?--
--suppose that we have already calculated the date x days ago--
--returns today avg price - x days ago avg price

SELECT (t.today_weighted_price - x.x_days_ago_weighted_price) price_delta
(SELECT (.07*(a.price) + .08*(b.price) + .35*(o.price) + .5*(s.price)) as today_weighted_price
FROM Avocado a 
JOIN Oil o ON a.dateID = o.dateID
JOIN Bitcoin b ON o.dateID = b.dateID
JOIN Stocks s ON b.dateID = s.dateID
WHERE o.dateID = today) t,
(SELECT (.07*(a.price) + .08*(b.price) + .35*(o.price) + .5*(s.price)) as x_days_ago_weighted_price
FROM Avocado a 
JOIN Oil o ON a.dateID = o.dateID
JOIN Bitcoin b ON o.dateID = b.dateID
JOIN Stocks s ON b.dateID = s.dateID
WHERE o.dateID = x_days_ago) x, 
