-- Price Tracker! --
--Queries to be used for the project--

--what was the price of a good on a day?--
Select history as new_today
From History h
Where h.dateid = 19970522;

SELECT MIN( AMZN ) FROM STOCKS s WHERE s.AMZN > 0 AND dateID >= 20200314;
SELECT AMZN FROM Stocks s WHERE s.dateID = 20011105;

SELECT s.chk
FROM Stocks s 
WHERE s.dateID = 20100326;

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

--1. What does this company do?--
SELECT d.descr
FROM Descriptions d 
WHERE d.itemID = AAPL

--2. How much did this stock drop (percentage) on the worst day of the market (3-16-2020)?--
SELECT (t.today_price - x.yesterday_price) price_delta
FROM
(SELECT s.AAPL as today_price
FROM Stocks s 
WHERE s.dateID = 20200316) t,
(SELECT s.AAPL as yesterday_price
FROM Stocks s 
WHERE s.dateID = 20200313) x ;

--3. How much did the stock change when markets reopened after 9/11 (20010917)?--
SELECT (t.today_price - x.yesterday_price) price_delta
FROM
(SELECT s.AAPL as today_price
FROM Stocks s 
WHERE s.dateID = 20010917) t,
(SELECT s.AAPL as yesterday_price
FROM Stocks s 
WHERE s.dateID = 20010910) x ;

--4. what's the average price of a stock adjusted for inflation? (since 2000)--
SELECT AVG(adjusted_value)
FROM (SELECT (AAPL/AMOUNT) as adjusted_value
FROM (SELECT dateID, AAPL
FROM Stocks s
WHERE dateID >= 20000103) a 
JOIN Dates d ON a.dateID = d.dateID
JOIN Inflation i ON d.Year = i.Year);

--5. in the last x days, has this item been trending down or up?--

SELECT (t.today_price - x.yesterday_price) price_delta
FROM
(SELECT s.AAPL as today_price
FROM Stocks s 
WHERE s.dateID = 20200323) t,
(SELECT s.AAPL as yesterday_price
FROM Stocks s 
WHERE s.dateID = 20200313) x ;

--6. How volatile is the price of Super Mario 64 over the last x months? (here x=8)--
SELECT (t.today_value - p.past_value) price_delta
FROM
(SELECT c.MARIO as today_value
FROM Commodities c 
WHERE c.dateID = 20200102) t,
(SELECT c.MARIO as past_value
FROM Commodities c
WHERE c.dateID = 20190502) p ;

--7. Return the higher inflation-adjusted value of _______ or Sears? (in 2006)--
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
SELECT GREATEST(v.adjusted_product, s.adjusted_sears) as higher_value
FROM Sears s, Valentino v;

--8. Has this item's percentage return beat the market from 2017 onwards? --
SELECT ((tm.today_mkt_price - xm.yesterday_mkt_price)/xm.yesterday_mkt_price*100) AS market_return, 
((t.today_item_price - x.yesterday_item_price)/x.yesterday_item_price*100) AS item_return
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

--9. Does this item beat the risk free rate of the market (10 yr T-bills) from 2017 onwards? --
-- https://dqydj.com/treasury-return-calculator/ --
SELECT ((t.today_item_price - x.yesterday_item_price)/x.yesterday_item_price*100) AS item_return, 17.067 AS tbill_return
FROM
(SELECT s.AAPL as today_item_price
FROM Stocks s 
WHERE s.dateID = 20200323) t,
(SELECT s.AAPL as yesterday_item_price
FROM Stocks s 
WHERE s.dateID = 20170103) x