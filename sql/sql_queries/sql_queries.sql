-- Price Tracker! --
-- QUERIES FOR ITEM PAGE --
-- 1. Obtain all price data over time - 2.15 sec
SELECT dateID, DOW 
FROM Indexes s
WHERE dateID >= 19700101;

-- 2. What is the current price of the item? - 0.571 sec
SELECT AAPL 
FROM Stocks s 
WHERE s.dateID = 20200409;

-- 3. What was the price of an item on a 
--    specific date (purchasing stock)? - 0.501 sec
SELECT AMZN 
FROM Stocks s 
WHERE s.dateID = 20180514;

-- 4. What is the historical max price? - 0.511 sec
SELECT MAX(AAPL) AS max_price
FROM Stocks s 
WHERE s.AAPL > 0 AND dateID >= 19700101;

-- 5. What is the date of the historical max price? - 0.505 sec
SELECT dateID AS max_date
FROM Stocks s 
WHERE s.AAPL = (
    SELECT MAX(AAPL) 
    FROM Stocks s 
    WHERE s.AAPL > 0 AND dateID >= 19700101)
    AND dateID >= 19700101;

-- 6. What historical event occurred on the max price date?
-- (max_date is the output of the above query) - 0.511 sec
SELECT history AS new_today 
FROM History h 
WHERE h.dateid = 'max_date';

-- 7. What is the historical min price? - 0.49 sec
SELECT MIN(AAPL) AS min_price
FROM Stocks s 
WHERE s.AAPL > 0 AND dateID >= 19700101;

-- 8. What is the date of the historical min price? - 0.512 sec
SELECT dateID AS min_date
FROM Stocks s 
WHERE s.AAPL = (
    SELECT MIN(AAPL) 
    FROM Stocks s 
    WHERE s.AAPL > 0 AND dateID >= 19700101)
    AND dateID >= 19700101;

-- 9. What historical event occurred on the min price date?
-- (max_date is the output of the above query) - 0.513 sec
SELECT history as new_today 
FROM History h 
WHERE h.dateid = 'max_date';

-- QUERIES FOR EXPLORE ITEM PAGE --
--1. What does this company do?-- 0.518 sec
SELECT d.desr
FROM Descriptions d 
WHERE d.itemID = AAPL

--2. How much did this stock drop (percentage) 
--   on the worst day of the market? - 0.955 sec
SELECT ((t.today_price - x.yesterday_price)/
    x.yesterday_price * 100) price_delta
FROM
(SELECT s.AAPL as today_price
FROM Stocks s 
WHERE s.dateID = 20200316) t,
(SELECT s.AAPL as yesterday_price
FROM Stocks s 
WHERE s.dateID = 20200313) x ;

--3. How much did the stock change when markets 
--   reopened after 9/11? - 0.494 sec
SELECT ((t.today_price - x.yesterday_price)/
    (x.yesterday_price+0.0001)) price_delta
FROM
(SELECT s.AAPL as today_price
FROM Stocks s 
WHERE s.dateID = 20010917) t,
(SELECT s.AAPL as yesterday_price
FROM Stocks s 
WHERE s.dateID = 20010910) x ;

--4. What's the average price of a stock adjusted
--   for inflation? (since 2000) - 0.511 sec
SELECT AVG(adjusted_value)
FROM (SELECT (AAPL/AMOUNT) as adjusted_value
FROM (SELECT dateID, AAPL
FROM Stocks s
WHERE dateID >= 20000103) a 
JOIN Dates d ON a.dateID = d.dateID
JOIN Inflation i ON d.Year = i.Year);

--5. In the last 10 days, has this item been 
--   trending down or up? - 0.491 sec

SELECT (t.today_price - x.yesterday_price) price_delta
FROM
(SELECT s.AAPL as today_price
FROM Stocks s 
WHERE s.dateID = 20200323) t,
(SELECT s.AAPL as yesterday_price
FROM Stocks s 
WHERE s.dateID = 20200313) x ;

--6. How volatile is the price of Super Mario 64 over 
--   the last 8 months? - 0.491 sec
SELECT (t.today_value - p.past_value) price_delta
FROM
(SELECT c.MARIO as today_value
FROM Commodities c 
WHERE c.dateID = 20200102) t,
(SELECT c.MARIO as past_value
FROM Commodities c
WHERE c.dateID = 20190502) p ;

--7. Return the difference between the inflation-adjusted 
--   values of Valentino and Sears in 2006. - .502 sec
WITH Sears AS (SELECT (SHLDQ/AMOUNT) as adjusted_sears
FROM (SELECT dateID, SHLDQ
FROM Stocks s
WHERE dateID = 20060323) a 
JOIN Dates d ON a.dateID = d.dateID
JOIN Inflation i ON d.Year = i.Year),
Valentino AS (SELECT (Valentino/AMOUNT) as adjusted_product
FROM (SELECT dateID, Valentino
FROM Commodities c
WHERE dateID = 20060323) a 
JOIN Dates d ON a.dateID = d.dateID
JOIN Inflation i ON d.Year = i.Year)
SELECT v.adjusted_product - s.adjusted_sears as difference
FROM Sears s, Valentino v;

--8. Has this item's percentage return beat 
--   the market from 2017 onwards? - 0.510 sec
SELECT ((tm.today_mkt_price - xm.yesterday_mkt_price)/
    xm.yesterday_mkt_price*100) AS market_return, 
    ((t.today_item_price - x.yesterday_item_price)/
    x.yesterday_item_price*100) AS item_return
FROM
(SELECT s.AAPL as today_item_price
FROM Stocks s 
WHERE s.dateID = 20200323) t,
(SELECT s.AAPL as yesterday_item_price
FROM Stocks s 
WHERE s.dateID = 20170103) x,
(SELECT i.SP as today_mkt_price
FROM Indexes i 
WHERE i.dateID = 20200323) tm,
(SELECT i.SP as yesterday_mkt_price
FROM Indexes i 
WHERE i.dateID = 20170103) xm;

--9. Does this item beat the risk free rate of the 
--   market (10 yr T-bills) from 2017 onwards? - 0.508 sec
-- Source: https://dqydj.com/treasury-return-calculator/
SELECT ((t.today_item_price - x.yesterday_item_price)/
    x.yesterday_item_price*100) AS item_return, 17.067 AS tbill_return
FROM
(SELECT s.AAPL as today_item_price
FROM Stocks s 
WHERE s.dateID = 20200323) t,
(SELECT s.AAPL as yesterday_item_price
FROM Stocks s 
WHERE s.dateID = 20170103) x

--10. How many times was the share price of this item 
--    10 cents within the share price of Apple (limit 2000)? - 0.51 sec
SELECT COUNT(Stocks.dateID) 
FROM Stocks JOIN Commodities ON Stocks.dateID = Commodities.dateID 
    JOIN Indexes ON Stocks.dateID = Indexes.dateID 
WHERE Exists (SELECT dateID, AMZN FROM Stocks s WHERE DateID >= 20100101) 
AND AAPL <> 0 AND Stocks.DateID >= 20100101 
AND Stocks.AAPL - Stocks.AMZN < 0.1
AND ROWNUM <= 2000