-- Price Tracker! --
--Queries to be used for the project--

--what was the price of a good on a day?--
Select history as new_today
From History h
Where h.dateid = 20080808;

SELECT AAPL 
FROM Stocks s 
WHERE s.dateID = 20200324;
/* we can replace Oil with another good and the data id with another date. */

-- get the price adjusted for inflation (i.e. how much would this cost in 1980?):
SELECT (AAPL / adjustment_rate.AMOUNT) as adjusted_AAPL
FROM Stocks s, (
SELECT Amount 
FROM Inflation i
WHERE i.Year = 1980) adjustment_rate
WHERE s.dateID = 20200324;

--get all of the prices of specific goods from the last x days--
--suppose that the date x days ago has already been calculated, call it --
SELECT s.AAPL as apple_stock, i.nasdaq as nasdaq
FROM Indexes i JOIN Stocks s
ON i.dateID = s.dateID
WHERE i.dateID >= 20200311;

-- given a series of days, see how each day's current events affect the stock prices
SELECT s.AAPL as Apple, s.AMZN as Amazon, s.JCP as JCPenney, s.GE as GE, s.BB as BlackBerry, h.history
FROM Stocks s JOIN History h
ON s.dateID = h.dateID
WHERE s.dateID >= 20200211
AND s.dateID <= 20200320;

-- what's the average price of a stock adjusted for inflation (here we limit to the dates to when apple was a company)
SELECT AVG(adjusted_apple)
FROM (SELECT (AAPL/AMOUNT) as adjusted_apple
FROM (SELECT dateID, AAPL
FROM Stocks s
WHERE dateID >= 19801212) a 
JOIN Dates d ON a.dateID = d.dateID
JOIN Inflation i ON d.Year = i.Year);

--given a day, was this a good day?--
--suppose that in our application, we already have an average--
--good days are where everything is above average--
-- this will be implented later --

--SELECT 1
--FROM Avocado a 
--JOIN Oil o ON a.dateID = o.dateID
--JOIN Bitcoin b ON o.dateID = b.dateID
--JOIN Stocks s ON b.dateID = s.dateID
--WHERE o.dateID = 19991231
--AND a.price > avocado_average
--AND o.price > oil_average
--AND b.price > bitcoin_average
--AND s.super_stock_index > 0

--given a day, was this a bad day?--
--bad days are where everything is below average--
-- this will be implented later --

--SELECT -1
--FROM Avocado a 
--JOIN Oil o ON a.dateID = o.dateID
--JOIN Bitcoin b ON o.dateID = b.dateID
--JOIN Stocks s ON b.dateID = s.dateID
--WHERE o.dateID = 19991231
--AND a.price < avocado_average
--AND o.price < oil_average
--AND b.price < bitcoin_average
--AND s.super_stock_index < 0;


--in the last x days, have prices in my bundle of stocks been trending down or up?--

SELECT (t.today_weighted_price - x.x_days_ago_weighted_price) price_delta
FROM
(SELECT (s.AAPL + s.AMZN)/2 as today_weighted_price
FROM Stocks s 
WHERE s.dateID = 20200323) t,
(SELECT (s.AAPL + s.AMZN)/2 as x_days_ago_weighted_price
FROM Stocks s 
WHERE s.dateID = 20200313) x ;

--How volatile is the price of Super Mario 64 over the last x months? (here x=8)--
SELECT (t.today_mario - p.past_mario) price_delta
FROM
(SELECT c.MARIO as today_mario
FROM Commodities c 
WHERE c.dateID = 20200102) t,
(SELECT c.MARIO as past_mario
FROM Commodities c
WHERE c.dateID = 20190502) p ;

--Return the higher inflation-adjusted value of the Valentino Beanie Baby or Sears? (in 2006)--
WITH Sears AS (SELECT (SHLDQ/AMOUNT) as adjusted_sears
FROM (SELECT dateID, SHLDQ
FROM Stocks s
WHERE dateID = 20060323) a 
JOIN Dates d ON a.dateID = d.dateID
JOIN Inflation i ON d.Year = i.Year),
Valentino AS (SELECT (Valentino/AMOUNT) as adjusted_valentino
FROM (SELECT dateID, Valentino
FROM Commodities c
WHERE dateID = 20060323) a 
JOIN Dates d ON a.dateID = d.dateID
JOIN Inflation i ON d.Year = i.Year)
SELECT GREATEST(v.adjusted_valentino, s.adjusted_sears) as higher_value
FROM Sears s, Valentino v;
