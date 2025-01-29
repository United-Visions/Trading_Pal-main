Forex API Documentation
The Polygon.io Forex API provides REST endpoints that let you query the latest market data for global currency pairs including forex trades and quotes, currency conversion rates, custom aggregate bars, and more.

Documentation
Authentication
Pass your API key in the query string like followsthis is my api key so it should be set in the config
https://api.polygon.io/v2/aggs/ticker/C:EURUSD/range/1/day/2023-01-09/2023-01-09?apiKey=a8waWkOhp6Bz4nZA64jDVqgZN6zm_bh6

Copy
Alternatively, you can add an Authorization header to the request with your API Key as the token in the following form:

Authorization: Bearer a8waWkOhp6Bz4nZA64jDVqgZN6zm_bh6

Copy
Usage
Many of Polygon.io's REST endpoints allow you to extend query parameters with inequalities like date.lt=2023-01-01 (less than) and date.gte=2023-01-01 (greater than or equal to) to search ranges of values. You can also use the field name without any extension to query for exact equality. Fields that support extensions will have an "Additional filter parameters" dropdown beneath them in the docs that detail the supported extensions for that parameter.

Response Types
By default, all endpoints return a JSON response. Users with currencies Starter plan and above can request a CSV response by including 'Accept': 'text/csv' as a request parameter.

Your Plan
Currencies Starter
Unlimited API Calls
Real-time Data
10+ Years Historical Data
Manage Subscription
Client Libraries
Python Logo
Python
client-python
Go Logo
Go
client-go
Javascript Logo
Javascript
client-js
PHP Logo
PHP
client-php
Kotlin Logo
Kotlin
client-jvm
Aggregates (Bars)
get
/v2/aggs/ticker/{forexTicker}/range/{multiplier}/{timespan}/{from}/{to}
Get aggregate bars for a forex pair over a given date range in custom time window sizes.

For example, if timespan = ‘minute’ and multiplier = ‘5’ then 5-minute bars will be returned.

Parameters
forexTicker
*
C:EURUSD
The ticker symbol of the currency pair.

multiplier
*
1
The size of the timespan multiplier.

timespan
*

day
The size of the time window.

from
*
2023-01-09
The start of the aggregate time window. Either a date with the format YYYY-MM-DD or a millisecond timestamp.

to
*
2023-02-10
The end of the aggregate time window. Either a date with the format YYYY-MM-DD or a millisecond timestamp.

adjusted

true
Whether or not the results are adjusted for splits. By default, results are adjusted. Set this to false to get results that are NOT adjusted for splits.

sort

asc
Sort the results by timestamp. asc will return results in ascending order (oldest at the top), desc will return results in descending order (newest at the top).

limit
Limits the number of base aggregates queried to create the aggregate results. Max 50000 and Default 5000. Read more about how limit is used to calculate aggregate results in our article on Aggregate Data API Improvements.

https://api.polygon.io/v2/aggs/ticker/C:EURUSD/range/1/day/2023-01-09/2023-02-10?adjusted=true&sort=asc&apiKey=a8waWkOhp6Bz4nZA64jDVqgZN6zm_bh6

Copy

JSON

Run Query
Response Attributes
ticker*string
The exchange symbol that this item is traded under.

adjusted*boolean
Whether or not this response was adjusted for splits.

queryCount*integer
The number of aggregates (minute or day) used to generate the response.

request_id*string
A request id assigned by the server.

resultsCount*integer
The total number of results for this request.

status*string
The status of this request's response.

resultsarray
c*number
The close price for the symbol in the given time period.

h*number
The highest price for the symbol in the given time period.

l*number
The lowest price for the symbol in the given time period.

ninteger
The number of transactions in the aggregate window.

o*number
The open price for the symbol in the given time period.

t*integer
The Unix Msec timestamp for the start of the aggregate window.

v*number
The trading volume of the symbol in the given time period.

vwnumber
The volume weighted average price.

Was this helpful?
Help us improve

Yes

No
Response Object
{
  "adjusted": true,
  "queryCount": 1,
  "request_id": "79c061995d8b627b736170bc9653f15d",
  "results": [
    {
      "c": 1.17721,
      "h": 1.18305,
      "l": 1.1756,
      "n": 125329,
      "o": 1.17921,
      "t": 1626912000000,
      "v": 125329,
      "vw": 1.1789
    }
  ],
  "resultsCount": 1,
  "status": "OK",
  "ticker": "C:EURUSD"
}
Grouped Daily (Bars)
get
/v2/aggs/grouped/locale/global/market/fx/{date}
Get the daily open, high, low, and close (OHLC) for the entire forex markets.

Parameters
date
*
2023-01-09
The beginning date for the aggregate window.

adjusted

true
Whether or not the results are adjusted for splits. By default, results are adjusted. Set this to false to get results that are NOT adjusted for splits.

https://api.polygon.io/v2/aggs/grouped/locale/global/market/fx/2023-01-09?adjusted=true&apiKey=a8waWkOhp6Bz4nZA64jDVqgZN6zm_bh6

Copy

JSON

Run Query
Response Attributes
adjusted*boolean
Whether or not this response was adjusted for splits.

queryCount*integer
The number of aggregates (minute or day) used to generate the response.

request_id*string
A request id assigned by the server.

resultsCount*integer
The total number of results for this request.

status*string
The status of this request's response.

resultsarray
T*string
The exchange symbol that this item is traded under.

c*number
The close price for the symbol in the given time period.

h*number
The highest price for the symbol in the given time period.

l*number
The lowest price for the symbol in the given time period.

ninteger
The number of transactions in the aggregate window.

o*number
The open price for the symbol in the given time period.

t*integer
The Unix Msec timestamp for the start of the aggregate window.

v*number
The trading volume of the symbol in the given time period.

vwnumber
The volume weighted average price.

Was this helpful?
Help us improve

Yes

No
Response Object
{
  "adjusted": true,
  "queryCount": 3,
  "results": [
    {
      "T": "C:ILSCHF",
      "c": 0.2704,
      "h": 0.2706,
      "l": 0.2693,
      "n": 689,
      "o": 0.2698,
      "t": 1602719999999,
      "v": 689,
      "vw": 0.2702
    },
    {
      "T": "C:GBPCAD",
      "c": 1.71103,
      "h": 1.71642,
      "l": 1.69064,
      "n": 407324,
      "o": 1.69955,
      "t": 1602719999999,
      "v": 407324,
      "vw": 1.7062
    },
    {
      "T": "C:DKKAUD",
      "c": 0.2214,
      "h": 0.2214,
      "l": 0.2195,
      "n": 10639,
      "o": 0.22,
      "t": 1602719999999,
      "v": 10639,
      "vw": 0.2202
    }
  ],
  "resultsCount": 3,
  "status": "OK"
}
Previous Close
get
/v2/aggs/ticker/{forexTicker}/prev
Get the previous day's open, high, low, and close (OHLC) for the specified forex pair.

Parameters
forexTicker
*
C:EURUSD
The ticker symbol of the currency pair.

adjusted

true
Whether or not the results are adjusted for splits. By default, results are adjusted. Set this to false to get results that are NOT adjusted for splits.

https://api.polygon.io/v2/aggs/ticker/C:EURUSD/prev?adjusted=true&apiKey=a8waWkOhp6Bz4nZA64jDVqgZN6zm_bh6

Copy

JSON

Run Query
Response Attributes
ticker*string
The exchange symbol that this item is traded under.

adjusted*boolean
Whether or not this response was adjusted for splits.

queryCount*integer
The number of aggregates (minute or day) used to generate the response.

request_id*string
A request id assigned by the server.

resultsCount*integer
The total number of results for this request.

status*string
The status of this request's response.

resultsarray
T*string
The exchange symbol that this item is traded under.

c*number
The close price for the symbol in the given time period.

h*number
The highest price for the symbol in the given time period.

l*number
The lowest price for the symbol in the given time period.

ninteger
The number of transactions in the aggregate window.

o*number
The open price for the symbol in the given time period.

t*integer
The Unix Msec timestamp for the start of the aggregate window.

v*number
The trading volume of the symbol in the given time period.

vwnumber
The volume weighted average price.

Was this helpful?
Help us improve

Yes

No
Response Object
{
  "adjusted": true,
  "queryCount": 1,
  "request_id": "08ec061fb85115678d68452c0a609cb7",
  "results": [
    {
      "T": "C:EURUSD",
      "c": 1.06206,
      "h": 1.0631,
      "l": 1.0505,
      "n": 180300,
      "o": 1.05252,
      "t": 1651708799999,
      "v": 180300,
      "vw": 1.055
    }
  ],
  "resultsCount": 1,
  "status": "OK",
  "ticker": "C:EURUSD"
}
Quotes (BBO)
get
/v3/quotes/{fxTicker}
Get BBO quotes for a ticker symbol in a given time range.

Parameters
fxTicker
*
C:EUR-USD
The ticker symbol to get quotes for.

timestamp
Query by timestamp. Either a date with the format YYYY-MM-DD or a nanosecond timestamp.


Additional filter parameters
order

Order results based on the sort field.

limit
1000
Limit the number of results returned, default is 1000 and max is 50000.

sort

Sort field used for ordering.

https://api.polygon.io/v3/quotes/C:EUR-USD?limit=1000&apiKey=a8waWkOhp6Bz4nZA64jDVqgZN6zm_bh6

Copy

JSON

Run Query
Response Attributes
next_urlstring
If present, this value can be used to fetch the next page of data.

resultsarray
ask_exchangeinteger
The ask exchange ID

ask_pricenumber
The ask price.

bid_exchangeinteger
The bid exchange ID

bid_pricenumber
The bid price.

participant_timestamp*integer
The nanosecond Exchange Unix Timestamp. This is the timestamp of when the quote was generated at the exchange.

status*string
The status of this request's response.

Was this helpful?
Help us improve

Yes

No
Response Object
{
  "next_url": "https://api.polygon.io/v3/quotes/C:EUR-USD?cursor=YWN0aXZlPXRydWUmZGF0ZT0yMDIxLTA0LTI1JmxpbWl0PTEmb3JkZXI9YXNjJnBhZ2VfbWFya2VyPUElN0M5YWRjMjY0ZTgyM2E1ZjBiOGUyNDc5YmZiOGE1YmYwNDVkYzU0YjgwMDcyMWE2YmI1ZjBjMjQwMjU4MjFmNGZiJnNvcnQ9dGlja2Vy",
  "request_id": "a47d1beb8c11b6ae897ab76cdbbf35a3",
  "results": [
    {
      "ask_exchange": 48,
      "ask_price": 1.18565,
      "bid_exchange": 48,
      "bid_price": 1.18558,
      "participant_timestamp": 1625097600000000000
    },
    {
      "ask_exchange": 48,
      "ask_price": 1.18565,
      "bid_exchange": 48,
      "bid_price": 1.18559,
      "participant_timestamp": 1625097600000000000
    }
  ],
  "status": "OK"
}
Last Quote for a Currency Pair
get
/v1/last_quote/currencies/{from}/{to}
Get the last quote tick for a forex currency pair.

Parameters
from
*
AUD
The "from" symbol of the pair.

to
*
USD
The "to" symbol of the pair.

https://api.polygon.io/v1/last_quote/currencies/AUD/USD?apiKey=a8waWkOhp6Bz4nZA64jDVqgZN6zm_bh6

Copy

JSON

Run Query
Response Attributes
lastobject
ask*number
The ask price.

bid*number
The bid price.

exchange*integer
The exchange ID. See Exchanges for Polygon.io's mapping of exchange IDs.

timestamp*integer
The Unix millisecond timestamp.

request_id*string
A request id assigned by the server.

status*string
The status of this request's response.

symbol*string
The symbol pair that was evaluated from the request.

Was this helpful?
Help us improve

Yes

No
Response Object
{
  "last": {
    "ask": 0.73124,
    "bid": 0.73122,
    "exchange": 48,
    "timestamp": 1605557756000
  },
  "request_id": "a73a29dbcab4613eeaf48583d3baacf0",
  "status": "success",
  "symbol": "AUD/USD"
}
Real-time Currency Conversion
get
/v1/conversion/{from}/{to}
Get currency conversions using the latest market conversion rates. Note than you can convert in both directions. For example USD to CAD or CAD to USD.

Parameters
from
*
AUD
The "from" symbol of the pair.

to
*
USD
The "to" symbol of the pair.

amount
100
The amount to convert, with a decimal.

precision

2
The decimal precision of the conversion. Defaults to 2 which is 2 decimal places accuracy.

https://api.polygon.io/v1/conversion/AUD/USD?amount=100&precision=2&apiKey=a8waWkOhp6Bz4nZA64jDVqgZN6zm_bh6

Copy

JSON

Run Query
Response Attributes
converted*number
The result of the conversion.

from*string
The "from" currency symbol.

initialAmount*number
The amount to convert.

lastobject
ask*number
The ask price.

bid*number
The bid price.

exchange*integer
The exchange ID. See Exchanges for Polygon.io's mapping of exchange IDs.

timestamp*integer
The Unix millisecond timestamp.

request_id*string
A request id assigned by the server.

status*string
The status of this request's response.

symbol*string
The symbol pair that was evaluated from the request.

to*string
The "to" currency symbol.

Was this helpful?
Help us improve

Yes

No
Response Object
{
  "converted": 73.14,
  "from": "AUD",
  "initialAmount": 100,
  "last": {
    "ask": 1.3673344,
    "bid": 1.3672596,
    "exchange": 48,
    "timestamp": 1605555313000
  },
  "request_id": "a73a29dbcab4613eeaf48583d3baacf0",
  "status": "success",
  "symbol": "AUD/USD",
  "to": "USD"
}
All Tickers
get
/v2/snapshot/locale/global/markets/forex/tickers
Get the current minute, day, and previous day’s aggregate, as well as the last trade and quote for all traded forex symbols.

Note: Snapshot data is cleared at 12am EST and gets populated as data is received from the exchanges. This can happen as early as 4am EST.

Parameters
tickers
A case-sensitive comma separated list of tickers to get snapshots for. For example, C:EURUSD, C:GBPCAD, and C:AUDINR. Empty string defaults to querying all tickers.

https://api.polygon.io/v2/snapshot/locale/global/markets/forex/tickers?apiKey=a8waWkOhp6Bz4nZA64jDVqgZN6zm_bh6

Copy

JSON

Run Query
Response Attributes
status*string
The status of this request's response.

tickersarray
day*object
The most recent daily bar for this ticker.

c*number
The close price for the symbol in the given time period.

h*number
The highest price for the symbol in the given time period.

l*number
The lowest price for the symbol in the given time period.

o*number
The open price for the symbol in the given time period.

v*number
The trading volume of the symbol in the given time period.

fmvnumber
Fair market value is only available on Business plans. It is our proprietary algorithm to generate a real-time, accurate, fair market value of a tradable security. For more information, contact us.

lastQuote*object
The most recent quote for this ticker.

a*number
The ask price.

b*number
The bid price.

t*integer
The millisecond accuracy timestamp of the quote.

x*integer
The exchange ID on which this quote happened.

min*object
The most recent minute bar for this ticker.

cnumber
The close price for the symbol in the given time period.

hnumber
The highest price for the symbol in the given time period.

lnumber
The lowest price for the symbol in the given time period.

ninteger
The number of transactions in the aggregate window.

onumber
The open price for the symbol in the given time period.

tinteger
The Unix Msec timestamp for the start of the aggregate window.

vnumber
The trading volume of the symbol in the given time period.

prevDay*object
The previous day's bar for this ticker.

c*number
The close price for the symbol in the given time period.

h*number
The highest price for the symbol in the given time period.

l*number
The lowest price for the symbol in the given time period.

o*number
The open price for the symbol in the given time period.

v*number
The trading volume of the symbol in the given time period.

vw*number
The volume weighted average price.

ticker*string
The exchange symbol that this item is traded under.

todaysChange*number
The value of the change from the previous day.

todaysChangePerc*number
The percentage change since the previous day.

updated*integer
The last updated timestamp.

Was this helpful?
Help us improve

Yes

No
Response Object
{
  "status": "OK",
  "tickers": [
    {
      "day": {
        "c": 0.11778221,
        "h": 0.11812263,
        "l": 0.11766631,
        "o": 0.11797149,
        "v": 77794
      },
      "lastQuote": {
        "a": 0.11780678,
        "b": 0.11777952,
        "t": 1605280919000,
        "x": 48
      },
      "min": {
        "c": 0.117769,
        "h": 0.11779633,
        "l": 0.11773698,
        "n": 1,
        "o": 0.11778,
        "t": 1684422000000,
        "v": 202
      },
      "prevDay": {
        "c": 0.11797258,
        "h": 0.11797258,
        "l": 0.11797149,
        "o": 0.11797149,
        "v": 2,
        "vw": 0
      },
      "ticker": "C:HKDCHF",
      "todaysChange": -0.00019306,
      "todaysChangePerc": -0.1636482,
      "updated": 1605280919000
    }
  ]
}
Gainers/Losers
get
/v2/snapshot/locale/global/markets/forex/{direction}
Get the current top 20 gainers or losers of the day in forex markets.

Top gainers are those tickers whose price has increased by the highest percentage since the previous day's close. Top losers are those tickers whose price has decreased by the highest percentage since the previous day's close.

Note: Snapshot data is cleared at 12am EST and gets populated as data is received from the exchanges.

Parameters
direction
*

gainers
The direction of the snapshot results to return.

https://api.polygon.io/v2/snapshot/locale/global/markets/forex/gainers?apiKey=a8waWkOhp6Bz4nZA64jDVqgZN6zm_bh6

Copy

JSON

Run Query
Response Attributes
status*string
The status of this request's response.

tickersarray
day*object
The most recent daily bar for this ticker.

c*number
The close price for the symbol in the given time period.

h*number
The highest price for the symbol in the given time period.

l*number
The lowest price for the symbol in the given time period.

o*number
The open price for the symbol in the given time period.

v*number
The trading volume of the symbol in the given time period.

fmvnumber
Fair market value is only available on Business plans. It is our proprietary algorithm to generate a real-time, accurate, fair market value of a tradable security. For more information, contact us.

lastQuote*object
The most recent quote for this ticker.

a*number
The ask price.

b*number
The bid price.

t*integer
The millisecond accuracy timestamp of the quote.

x*integer
The exchange ID on which this quote happened.

min*object
The most recent minute bar for this ticker.

cnumber
The close price for the symbol in the given time period.

hnumber
The highest price for the symbol in the given time period.

lnumber
The lowest price for the symbol in the given time period.

ninteger
The number of transactions in the aggregate window.

onumber
The open price for the symbol in the given time period.

tinteger
The Unix Msec timestamp for the start of the aggregate window.

vnumber
The trading volume of the symbol in the given time period.

prevDay*object
The previous day's bar for this ticker.

c*number
The close price for the symbol in the given time period.

h*number
The highest price for the symbol in the given time period.

l*number
The lowest price for the symbol in the given time period.

o*number
The open price for the symbol in the given time period.

v*number
The trading volume of the symbol in the given time period.

vw*number
The volume weighted average price.

ticker*string
The exchange symbol that this item is traded under.

todaysChange*number
The value of the change from the previous day.

todaysChangePerc*number
The percentage change since the previous day.

updated*integer
The last updated timestamp.

Was this helpful?
Help us improve

Yes

No
Response Object
{
  "status": "OK",
  "tickers": [
    {
      "day": {
        "c": 0.886156,
        "h": 0.887111,
        "l": 0.8825327,
        "o": 0.8844732,
        "v": 1041
      },
      "lastQuote": {
        "a": 0.8879606,
        "b": 0.886156,
        "t": 1605283204000,
        "x": 48
      },
      "min": {
        "c": 0.886156,
        "h": 0.886156,
        "l": 0.886156,
        "n": 1,
        "o": 0.886156,
        "t": 1684422000000,
        "v": 1
      },
      "prevDay": {
        "c": 0.8428527,
        "h": 0.889773,
        "l": 0.8428527,
        "o": 0.8848539,
        "v": 1078,
        "vw": 0
      },
      "ticker": "C:PLNILS",
      "todaysChange": 0.0433033,
      "todaysChangePerc": 5.13770674,
      "updated": 1605330008999
    }
  ]
}
Ticker
get
/v2/snapshot/locale/global/markets/forex/tickers/{ticker}
Get the current minute, day, and previous day’s aggregate, as well as the last trade and quote for a single traded currency symbol.

Note: Snapshot data is cleared at 12am EST and gets populated as data is received from the exchanges.

Parameters
ticker
*
C:EURUSD
The forex ticker.

https://api.polygon.io/v2/snapshot/locale/global/markets/forex/tickers/C:EURUSD?apiKey=a8waWkOhp6Bz4nZA64jDVqgZN6zm_bh6

Copy

JSON

Run Query
Response Attributes
status*string
The status of this request's response.

request_id*string
A request id assigned by the server.

tickerobject
day*object
The most recent daily bar for this ticker.

c*number
The close price for the symbol in the given time period.

h*number
The highest price for the symbol in the given time period.

l*number
The lowest price for the symbol in the given time period.

o*number
The open price for the symbol in the given time period.

v*number
The trading volume of the symbol in the given time period.

fmvnumber
Fair market value is only available on Business plans. It is our proprietary algorithm to generate a real-time, accurate, fair market value of a tradable security. For more information, contact us.

lastQuote*object
The most recent quote for this ticker.

a*number
The ask price.

b*number
The bid price.

t*integer
The millisecond accuracy timestamp of the quote.

x*integer
The exchange ID on which this quote happened.

min*object
The most recent minute bar for this ticker.

cnumber
The close price for the symbol in the given time period.

hnumber
The highest price for the symbol in the given time period.

lnumber
The lowest price for the symbol in the given time period.

ninteger
The number of transactions in the aggregate window.

onumber
The open price for the symbol in the given time period.

tinteger
The Unix Msec timestamp for the start of the aggregate window.

vnumber
The trading volume of the symbol in the given time period.

prevDay*object
The previous day's bar for this ticker.

c*number
The close price for the symbol in the given time period.

h*number
The highest price for the symbol in the given time period.

l*number
The lowest price for the symbol in the given time period.

o*number
The open price for the symbol in the given time period.

v*number
The trading volume of the symbol in the given time period.

vw*number
The volume weighted average price.

ticker*string
The exchange symbol that this item is traded under.

todaysChange*number
The value of the change from the previous day.

todaysChangePerc*number
The percentage change since the previous day.

updated*integer
The last updated timestamp.

Was this helpful?
Help us improve

Yes

No
Response Object
{
  "request_id": "ad76e76ce183002c5937a7f02dfebde4",
  "status": "OK",
  "ticker": {
    "day": {
      "c": 1.18403,
      "h": 1.1906,
      "l": 1.18001,
      "o": 1.18725,
      "v": 83578
    },
    "lastQuote": {
      "a": 1.18403,
      "b": 1.18398,
      "i": 0,
      "t": 1606163759000,
      "x": 48
    },
    "min": {
      "c": 1.18396,
      "h": 1.18423,
      "l": 1.1838,
      "n": 85,
      "o": 1.18404,
      "t": 1684422000000,
      "v": 41
    },
    "prevDay": {
      "c": 1.18724,
      "h": 1.18727,
      "l": 1.18725,
      "o": 1.18725,
      "v": 5,
      "vw": 0
    },
    "ticker": "C:EURUSD",
    "todaysChange": -0.00316,
    "todaysChangePerc": -0.27458312,
    "updated": 1606163759000
  }
}
Universal Snapshot
get
/v3/snapshot
Get snapshots for assets of all types

Parameters
ticker.any_of
NCLH,O:SPY250321C00380000,C:EURUSD,X:BTCUSD,I:SPX
Comma separated list of tickers, up to a maximum of 250. If no tickers are passed then all results will be returned in a paginated manner.

Warning: The maximum number of characters allowed in a URL are subject to your technology stack.


Additional filter parameters
type

Query by the type of asset.

order

Order results based on the sort field.

limit
10
Limit the number of results returned, default is 10 and max is 250.

sort

Sort field used for ordering.

https://api.polygon.io/v3/snapshot?ticker.any_of=NCLH,O:SPY250321C00380000,C:EURUSD,X:BTCUSD,I:SPX&limit=10&apiKey=a8waWkOhp6Bz4nZA64jDVqgZN6zm_bh6

Copy

Run Query
Response Attributes
next_urlstring
If present, this value can be used to fetch the next page of data.

request_id*string
resultsarray
break_even_pricenumber
The price of the underlying asset for the contract to break even. For a call, this value is (strike price + premium paid). For a put, this value is (strike price - premium paid).

detailsobject
The details for this contract.

contract_type*enum [put, call, other]
The type of contract. Can be "put", "call", or in some rare cases, "other".

exercise_style*enum [american, european, bermudan]
The exercise style of this contract. See this link for more details on exercise styles.

expiration_date*string
The contract's expiration date in YYYY-MM-DD format.

shares_per_contract*number
The number of shares per contract for this contract.

strike_price*number
The strike price of the option contract.

errorstring
The error while looking for this ticker.

fmvnumber
Fair market value is only available on Business plans. It's it our proprietary algorithm to generate a real-time, accurate, fair market value of a tradable security. For more information, contact us.

greeksobject
The greeks for this contract. There are certain circumstances where greeks will not be returned, such as options contracts that are deep in the money. See this article for more information.

delta*number
The change in the option's price per $0.01 increment in the price of the underlying asset.

gamma*number
The change in delta per $0.01 change in the price of the underlying asset.

theta*number
The change in the option's price per day.

vega*number
The change in the option's price per 1% increment in volatility.

implied_volatilitynumber
The market's forecast for the volatility of the underlying asset, based on this option's current price.

last_quoteobject
The most recent quote for this contract. This is only returned if your current plan includes quotes.

ask*number
The ask price.

ask_exchangeinteger
The ask side exchange ID. See Exchanges for Polygon.io's mapping of exchange IDs.

ask_sizenumber
The ask size. This represents the number of round lot orders at the given ask price. The normal round lot size is 100 shares. An ask size of 2 means there are 200 shares available to purchase at the given ask price.

bid*number
The bid price.

bid_exchangeinteger
The bid side exchange ID. See Exchanges for Polygon.io's mapping of exchange IDs.

bid_sizenumber
The bid size. This represents the number of round lot orders at the given bid price. The normal round lot size is 100 shares. A bid size of 2 means there are 200 shares for purchase at the given bid price.

last_updated*integer
The nanosecond timestamp of when this information was updated.

midpointnumber
The average of the bid and ask price.

timeframe*enum [DELAYED, REAL-TIME]
The time relevance of the data.

last_tradeobject
The most recent quote for this contract. This is only returned if your current plan includes trades.

conditionsarray [integer]
A list of condition codes.

exchangeinteger
The exchange ID. See Exchanges for Polygon.io's mapping of exchange IDs.

idstring
The Trade ID which uniquely identifies a trade. These are unique per combination of ticker, exchange, and TRF. For example: A trade for AAPL executed on NYSE and a trade for AAPL executed on NASDAQ could potentially have the same Trade ID.

last_updatedinteger
The nanosecond timestamp of when this information was updated.

participant_timestampinteger
The nanosecond Exchange Unix Timestamp. This is the timestamp of when the trade was generated at the exchange.

price*number
The price of the trade. This is the actual dollar value per whole share of this trade. A trade of 100 shares with a price of $2.00 would be worth a total dollar value of $200.00.

sip_timestampinteger
The nanosecond accuracy SIP Unix Timestamp. This is the timestamp of when the SIP received this trade from the exchange which produced it.

size*integer
The size of a trade (also known as volume).

timeframeenum [DELAYED, REAL-TIME]
The time relevance of the data.

market_statusstring
The market status for the market that trades this ticker. Possible values for stocks, options, crypto, and forex snapshots are open, closed, early_trading, or late_trading. Possible values for indices snapshots are regular_trading, closed, early_trading, and late_trading.

messagestring
The error message while looking for this ticker.

namestring
The name of this contract.

open_interestnumber
The quantity of this contract held at the end of the last trading day.

sessionobject
change*number
The value of the price change for the asset from the previous trading day.

change_percent*number
The percent of the price change for the asset from the previous trading day.

close*number
The closing price of the asset for the day.

early_trading_changenumber
Today's early trading change amount, difference between price and previous close if in early trading hours, otherwise difference between last price during early trading and previous close.

early_trading_change_percentnumber
Today's early trading change as a percentage.

high*number
The highest price of the asset for the day.

late_trading_changenumber
Today's late trading change amount, difference between price and today's close if in late trading hours, otherwise difference between last price during late trading and today's close.

late_trading_change_percentnumber
Today's late trading change as a percentage.

low*number
The lowest price of the asset for the day.

open*number
The open price of the asset for the day.

previous_close*number
The closing price of the asset for the previous trading day.

pricenumber
The price of the most recent trade or bid price for this asset.

regular_trading_changenumber
Today's change in regular trading hours, difference between current price and previous trading day's close, otherwise difference between today's close and previous day's close.

regular_trading_change_percentnumber
Today's regular trading change as a percentage.

volumenumber
The trading volume for the asset for the day.

ticker*string
The ticker symbol for the asset.

typeenum [stocks, options, fx, crypto, indices]
The asset class for this ticker.

underlying_assetobject
Information on the underlying stock for this options contract. The market data returned depends on your current stocks plan.

change_to_break_even*number
The change in price for the contract to break even.

last_updatedinteger
The nanosecond timestamp of when this information was updated.

pricenumber
The price of the trade. This is the actual dollar value per whole share of this trade. A trade of 100 shares with a price of $2.00 would be worth a total dollar value of $200.00.

ticker*string
The ticker symbol for the contract's underlying asset.

timeframeenum [DELAYED, REAL-TIME]
The time relevance of the data.

valuenumber
The value of the underlying index.

valuenumber
Value of Index.

status*string
The status of this request's response.

Was this helpful?
Help us improve

Yes

No
Response Object
{
  "request_id": "abc123",
  "results": [
    {
      "break_even_price": 171.075,
      "details": {
        "contract_type": "call",
        "exercise_style": "american",
        "expiration_date": "2022-10-14",
        "shares_per_contract": 100,
        "strike_price": 5,
        "underlying_ticker": "NCLH"
      },
      "fmv": 0.05,
      "greeks": {
        "delta": 0.5520187372272933,
        "gamma": 0.00706756515659829,
        "theta": -0.018532772783847958,
        "vega": 0.7274811132998142
      },
      "implied_volatility": 0.3048997097864957,
      "last_quote": {
        "ask": 21.25,
        "ask_exchange": 12,
        "ask_size": 110,
        "bid": 20.9,
        "bid_exchange": 10,
        "bid_size": 172,
        "last_updated": 1636573458756383500,
        "midpoint": 21.075,
        "timeframe": "REAL-TIME"
      },
      "last_trade": {
        "conditions": [
          209
        ],
        "exchange": 316,
        "price": 0.05,
        "sip_timestamp": 1675280958783136800,
        "size": 2,
        "timeframe": "REAL-TIME"
      },
      "market_status": "closed",
      "name": "NCLH $5 Call",
      "open_interest": 8921,
      "session": {
        "change": -0.05,
        "change_percent": -1.07,
        "close": 6.65,
        "early_trading_change": -0.01,
        "early_trading_change_percent": -0.03,
        "high": 7.01,
        "late_trading_change": -0.4,
        "late_trading_change_percent": -0.02,
        "low": 5.42,
        "open": 6.7,
        "previous_close": 6.71,
        "volume": 67
      },
      "ticker": "O:NCLH221014C00005000",
      "type": "options",
      "underlying_asset": {
        "change_to_break_even": 23.123999999999995,
        "last_updated": 1636573459862384600,
        "price": 147.951,
        "ticker": "AAPL",
        "timeframe": "REAL-TIME"
      }
    },
    {
      "fmv": 0.05,
      "last_quote": {
        "ask": 21.25,
        "ask_exchange": 300,
        "ask_size": 110,
        "bid": 20.9,
        "bid_exchange": 323,
        "bid_size": 172,
        "last_updated": 1636573458756383500,
        "timeframe": "REAL-TIME"
      },
      "last_trade": {
        "conditions": [
          209
        ],
        "exchange": 316,
        "id": "4064",
        "last_updated": 1675280958783136800,
        "price": 0.05,
        "size": 2,
        "timeframe": "REAL-TIME"
      },
      "market_status": "closed",
      "name": "Apple Inc.",
      "session": {
        "change": -1.05,
        "change_percent": -4.67,
        "close": 21.4,
        "early_trading_change": -0.39,
        "early_trading_change_percent": -0.07,
        "high": 22.49,
        "late_trading_change": 1.2,
        "late_trading_change_percent": 3.92,
        "low": 21.35,
        "open": 22.49,
        "previous_close": 22.45,
        "volume": 37
      },
      "ticker": "AAPL",
      "type": "stocks"
    },
    {
      "error": "NOT_FOUND",
      "message": "Ticker not found.",
      "ticker": "TSLAAPL"
    }
  ],
  "status": "OK"
}
Simple Moving Average (SMA)
get
/v1/indicators/sma/{fxTicker}
Get the simple moving average (SMA) for a ticker symbol over a given time range.

Parameters
fxTicker
*
C:EURUSD
The ticker symbol for which to get simple moving average (SMA) data.

timestamp
Query by timestamp. Either a date with the format YYYY-MM-DD or a millisecond timestamp.


Additional filter parameters
timespan

day
The size of the aggregate time window.

adjusted

true
Whether or not the aggregates used to calculate the simple moving average are adjusted for splits. By default, aggregates are adjusted. Set this to false to get results that are NOT adjusted for splits.

window
50
The window size used to calculate the simple moving average (SMA). i.e. a window size of 10 with daily aggregates would result in a 10 day moving average.

series_type

close
The price in the aggregate which will be used to calculate the simple moving average. i.e. 'close' will result in using close prices to calculate the simple moving average (SMA).

expand_underlying

Whether or not to include the aggregates used to calculate this indicator in the response.

order

desc
The order in which to return the results, ordered by timestamp.

limit
10
Limit the number of results returned, default is 10 and max is 5000

https://api.polygon.io/v1/indicators/sma/C:EURUSD?timespan=day&adjusted=true&window=50&series_type=close&order=desc&limit=10&apiKey=a8waWkOhp6Bz4nZA64jDVqgZN6zm_bh6

Copy

JSON

Run Query
Response Attributes
next_urlstring
If present, this value can be used to fetch the next page of data.

request_idstring
A request id assigned by the server.

resultsobject
underlyingobject
aggregatesarray
c*number
The close price for the symbol in the given time period.

h*number
The highest price for the symbol in the given time period.

l*number
The lowest price for the symbol in the given time period.

n*integer
The number of transactions in the aggregate window.

o*number
The open price for the symbol in the given time period.

otcboolean
Whether or not this aggregate is for an OTC ticker. This field will be left off if false.

t*number
The Unix Msec timestamp for the start of the aggregate window.

v*number
The trading volume of the symbol in the given time period.

vw*number
The volume weighted average price.

urlstring
The URL which can be used to request the underlying aggregates used in this request.

valuesarray
timestampinteger
The Unix Msec timestamp from the last aggregate used in this calculation.

valuenumber
The indicator value for this period.

statusstring
The status of this request's response.

Was this helpful?
Help us improve

Yes

No
Response Object
{
  "next_url": "https://api.polygon.io/v1/indicators/sma/C:USDAUD?cursor=YWN0aXZlPXRydWUmZGF0ZT0yMDIxLTA0LTI1JmxpbWl0PTEmb3JkZXI9YXNjJnBhZ2VfbWFya2VyPUElN0M5YWRjMjY0ZTgyM2E1ZjBiOGUyNDc5YmZiOGE1YmYwNDVkYzU0YjgwMDcyMWE2YmI1ZjBjMjQwMjU4MjFmNGZiJnNvcnQ9dGlja2Vy",
  "request_id": "a47d1beb8c11b6ae897ab76cdbbf35a3",
  "results": {
    "underlying": {
      "aggregates": [
        {
          "c": 75.0875,
          "h": 75.15,
          "l": 73.7975,
          "n": 1,
          "o": 74.06,
          "t": 1577941200000,
          "v": 135647456,
          "vw": 74.6099
        },
        {
          "c": 74.3575,
          "h": 75.145,
          "l": 74.125,
          "n": 1,
          "o": 74.2875,
          "t": 1578027600000,
          "v": 146535512,
          "vw": 74.7026
        }
      ],
      "url": "https://api.polygon.io/v2/aggs/ticker/C:USDAUD/range/1/day/2003-01-01/2022-07-25"
    },
    "values": [
      {
        "timestamp": 1517562000016,
        "value": 140.139
      }
    ]
  },
  "status": "OK"
}
Exponential Moving Average (EMA)
get
/v1/indicators/ema/{fxTicker}
Get the exponential moving average (EMA) for a ticker symbol over a given time range.

Parameters
fxTicker
*
C:EURUSD
The ticker symbol for which to get exponential moving average (EMA) data.

timestamp
Query by timestamp. Either a date with the format YYYY-MM-DD or a millisecond timestamp.


Additional filter parameters
timespan

day
The size of the aggregate time window.

adjusted

true
Whether or not the aggregates used to calculate the exponential moving average are adjusted for splits. By default, aggregates are adjusted. Set this to false to get results that are NOT adjusted for splits.

window
50
The window size used to calculate the exponential moving average (EMA). i.e. a window size of 10 with daily aggregates would result in a 10 day moving average.

series_type

close
The price in the aggregate which will be used to calculate the exponential moving average. i.e. 'close' will result in using close prices to calculate the exponential moving average (EMA).

expand_underlying

Whether or not to include the aggregates used to calculate this indicator in the response.

order

desc
The order in which to return the results, ordered by timestamp.

limit
10
Limit the number of results returned, default is 10 and max is 5000

https://api.polygon.io/v1/indicators/ema/C:EURUSD?timespan=day&adjusted=true&window=50&series_type=close&order=desc&limit=10&apiKey=a8waWkOhp6Bz4nZA64jDVqgZN6zm_bh6

Copy

JSON

Run Query
Response Attributes
next_urlstring
If present, this value can be used to fetch the next page of data.

request_idstring
A request id assigned by the server.

resultsobject
underlyingobject
aggregatesarray
c*number
The close price for the symbol in the given time period.

h*number
The highest price for the symbol in the given time period.

l*number
The lowest price for the symbol in the given time period.

n*integer
The number of transactions in the aggregate window.

o*number
The open price for the symbol in the given time period.

otcboolean
Whether or not this aggregate is for an OTC ticker. This field will be left off if false.

t*number
The Unix Msec timestamp for the start of the aggregate window.

v*number
The trading volume of the symbol in the given time period.

vw*number
The volume weighted average price.

urlstring
The URL which can be used to request the underlying aggregates used in this request.

valuesarray
timestampinteger
The Unix Msec timestamp from the last aggregate used in this calculation.

valuenumber
The indicator value for this period.

statusstring
The status of this request's response.

Was this helpful?
Help us improve

Yes

No
Response Object
{
  "next_url": "https://api.polygon.io/v1/indicators/ema/C:USDAUD?cursor=YWN0aXZlPXRydWUmZGF0ZT0yMDIxLTA0LTI1JmxpbWl0PTEmb3JkZXI9YXNjJnBhZ2VfbWFya2VyPUElN0M5YWRjMjY0ZTgyM2E1ZjBiOGUyNDc5YmZiOGE1YmYwNDVkYzU0YjgwMDcyMWE2YmI1ZjBjMjQwMjU4MjFmNGZiJnNvcnQ9dGlja2Vy",
  "request_id": "a47d1beb8c11b6ae897ab76cdbbf35a3",
  "results": {
    "underlying": {
      "url": "https://api.polygon.io/v2/aggs/ticker/C:USDAUD/range/1/day/2003-01-01/2022-07-25"
    },
    "values": [
      {
        "timestamp": 1517562000016,
        "value": 140.139
      }
    ]
  },
  "status": "OK"
}
Moving Average Convergence/Divergence (MACD)
get
/v1/indicators/macd/{fxTicker}
Get moving average convergence/divergence (MACD) data for a ticker symbol over a given time range.

Parameters
fxTicker
*
C:EURUSD
The ticker symbol for which to get MACD data.

timestamp
Query by timestamp. Either a date with the format YYYY-MM-DD or a millisecond timestamp.


Additional filter parameters
timespan

day
The size of the aggregate time window.

adjusted

true
Whether or not the aggregates used to calculate the MACD are adjusted for splits. By default, aggregates are adjusted. Set this to false to get results that are NOT adjusted for splits.

short_window
12
The short window size used to calculate MACD data.

long_window
26
The long window size used to calculate MACD data.

signal_window
9
The window size used to calculate the MACD signal line.

series_type

close
The price in the aggregate which will be used to calculate the MACD. i.e. 'close' will result in using close prices to calculate the MACD.

expand_underlying

Whether or not to include the aggregates used to calculate this indicator in the response.

order

desc
The order in which to return the results, ordered by timestamp.

limit
10
Limit the number of results returned, default is 10 and max is 5000

https://api.polygon.io/v1/indicators/macd/C:EURUSD?timespan=day&adjusted=true&short_window=12&long_window=26&signal_window=9&series_type=close&order=desc&limit=10&apiKey=a8waWkOhp6Bz4nZA64jDVqgZN6zm_bh6

Copy

JSON

Run Query
Response Attributes
next_urlstring
If present, this value can be used to fetch the next page of data.

request_idstring
A request id assigned by the server.

resultsobject
underlyingobject
aggregatesarray
c*number
The close price for the symbol in the given time period.

h*number
The highest price for the symbol in the given time period.

l*number
The lowest price for the symbol in the given time period.

n*integer
The number of transactions in the aggregate window.

o*number
The open price for the symbol in the given time period.

otcboolean
Whether or not this aggregate is for an OTC ticker. This field will be left off if false.

t*number
The Unix Msec timestamp for the start of the aggregate window.

v*number
The trading volume of the symbol in the given time period.

vw*number
The volume weighted average price.

urlstring
The URL which can be used to request the underlying aggregates used in this request.

valuesarray
histogramnumber
The indicator value for this period.

signalnumber
The indicator value for this period.

timestampinteger
The Unix Msec timestamp from the last aggregate used in this calculation.

valuenumber
The indicator value for this period.

statusstring
The status of this request's response.

Was this helpful?
Help us improve

Yes

No
Response Object
{
  "next_url": "https://api.polygon.io/v1/indicators/macd/C:USDAUD?cursor=YWN0aXZlPXRydWUmZGF0ZT0yMDIxLTA0LTI1JmxpbWl0PTEmb3JkZXI9YXNjJnBhZ2VfbWFya2VyPUElN0M5YWRjMjY0ZTgyM2E1ZjBiOGUyNDc5YmZiOGE1YmYwNDVkYzU0YjgwMDcyMWE2YmI1ZjBjMjQwMjU4MjFmNGZiJnNvcnQ9dGlja2Vy",
  "request_id": "a47d1beb8c11b6ae897ab76cdbbf35a3",
  "results": {
    "underlying": {
      "url": "https://api.polygon.io/v2/aggs/ticker/C:USDAUD/range/1/day/2003-01-01/2022-07-25"
    },
    "values": [
      {
        "histogram": 38.3801666667,
        "signal": 106.9811666667,
        "timestamp": 1517562000016,
        "value": 145.3613333333
      },
      {
        "histogram": 41.098859136,
        "signal": 102.7386283473,
        "timestamp": 1517562001016,
        "value": 143.8374874833
      }
    ]
  },
  "status": "OK"
}
Relative Strength Index (RSI)
get
/v1/indicators/rsi/{fxTicker}
Get the relative strength index (RSI) for a ticker symbol over a given time range.

Parameters
fxTicker
*
C:EURUSD
The ticker symbol for which to get relative strength index (RSI) data.

timestamp
Query by timestamp. Either a date with the format YYYY-MM-DD or a millisecond timestamp.


Additional filter parameters
timespan

day
The size of the aggregate time window.

adjusted

true
Whether or not the aggregates used to calculate the relative strength index are adjusted for splits. By default, aggregates are adjusted. Set this to false to get results that are NOT adjusted for splits.

window
14
The window size used to calculate the relative strength index (RSI).

series_type

close
The price in the aggregate which will be used to calculate the relative strength index. i.e. 'close' will result in using close prices to calculate the relative strength index (RSI).

expand_underlying

Whether or not to include the aggregates used to calculate this indicator in the response.

order

desc
The order in which to return the results, ordered by timestamp.

limit
10
Limit the number of results returned, default is 10 and max is 5000

https://api.polygon.io/v1/indicators/rsi/C:EURUSD?timespan=day&adjusted=true&window=14&series_type=close&order=desc&limit=10&apiKey=a8waWkOhp6Bz4nZA64jDVqgZN6zm_bh6

Copy

JSON

Run Query
Response Attributes
next_urlstring
If present, this value can be used to fetch the next page of data.

request_idstring
A request id assigned by the server.

resultsobject
underlyingobject
aggregatesarray
c*number
The close price for the symbol in the given time period.

h*number
The highest price for the symbol in the given time period.

l*number
The lowest price for the symbol in the given time period.

n*integer
The number of transactions in the aggregate window.

o*number
The open price for the symbol in the given time period.

otcboolean
Whether or not this aggregate is for an OTC ticker. This field will be left off if false.

t*number
The Unix Msec timestamp for the start of the aggregate window.

v*number
The trading volume of the symbol in the given time period.

vw*number
The volume weighted average price.

urlstring
The URL which can be used to request the underlying aggregates used in this request.

valuesarray
timestampinteger
The Unix Msec timestamp from the last aggregate used in this calculation.

valuenumber
The indicator value for this period.

statusstring
The status of this request's response.

Was this helpful?
Help us improve

Yes

No
Response Object
{
  "next_url": "https://api.polygon.io/v1/indicators/rsi/C:USDAUD?cursor=YWN0aXZlPXRydWUmZGF0ZT0yMDIxLTA0LTI1JmxpbWl0PTEmb3JkZXI9YXNjJnBhZ2VfbWFya2VyPUElN0M5YWRjMjY0ZTgyM2E1ZjBiOGUyNDc5YmZiOGE1YmYwNDVkYzU0YjgwMDcyMWE2YmI1ZjBjMjQwMjU4MjFmNGZiJnNvcnQ9dGlja2Vy",
  "request_id": "a47d1beb8c11b6ae897ab76cdbbf35a3",
  "results": {
    "underlying": {
      "url": "https://api.polygon.io/v2/aggs/ticker/C:USDAUD/range/1/day/2003-01-01/2022-07-25"
    },
    "values": [
      {
        "timestamp": 1517562000016,
        "value": 82.19
      }
    ]
  },
  "status": "OK"
}
Tickers
get
/v3/reference/tickers
Query all ticker symbols which are supported by Polygon.io. This API currently includes Stocks/Equities, Indices, Forex, and Crypto.

Parameters
ticker
Specify a ticker symbol. Defaults to empty string which queries all tickers.


Additional filter parameters
type

Specify the type of the tickers. Find the types that we support via our Ticker Types API. Defaults to empty string which queries all types.

market

Filter by market type. By default all markets are included.

exchange
Specify the primary exchange of the asset in the ISO code format. Find more information about the ISO codes at the ISO org website. Defaults to empty string which queries all exchanges.

cusip
Specify the CUSIP code of the asset you want to search for. Find more information about CUSIP codes at their website. Defaults to empty string which queries all CUSIPs.

Note: Although you can query by CUSIP, due to legal reasons we do not return the CUSIP in the response.

cik
Specify the CIK of the asset you want to search for. Find more information about CIK codes at their website. Defaults to empty string which queries all CIKs.

date

Specify a point in time to retrieve tickers available on that date. Defaults to the most recent available date.

search
Search for terms within the ticker and/or company name.

active

true
Specify if the tickers returned should be actively traded on the queried date. Default is true.

order

Order results based on the sort field.

limit
100
Limit the number of results returned, default is 100 and max is 1000.

sort

Sort field used for ordering.

https://api.polygon.io/v3/reference/tickers?active=true&limit=100&apiKey=a8waWkOhp6Bz4nZA64jDVqgZN6zm_bh6

Copy

JSON

Run Query
Response Attributes
countinteger
The total number of results for this request.

next_urlstring
If present, this value can be used to fetch the next page of data.

request_idstring
A request id assigned by the server.

resultsarray
An array of tickers that match your query.

Note: Although you can query by CUSIP, due to legal reasons we do not return the CUSIP in the response.

activeboolean
Whether or not the asset is actively traded. False means the asset has been delisted.

cikstring
The CIK number for this ticker. Find more information here.

composite_figistring
The composite OpenFIGI number for this ticker. Find more information here

currency_namestring
The name of the currency that this asset is traded with.

delisted_utcstring
The last date that the asset was traded.

last_updated_utcstring
The information is accurate up to this time.

locale*enum [us, global]
The locale of the asset.

market*enum [stocks, crypto, fx, otc, indices]
The market type of the asset.

name*string
The name of the asset. For stocks/equities this will be the companies registered name. For crypto/fx this will be the name of the currency or coin pair.

primary_exchangestring
The ISO code of the primary listing exchange for this asset.

share_class_figistring
The share Class OpenFIGI number for this ticker. Find more information here

ticker*string
The exchange symbol that this item is traded under.

typestring
The type of the asset. Find the types that we support via our Ticker Types API.

statusstring
The status of this request's response.

Was this helpful?
Help us improve

Yes

No
Response Object
{
  "count": 1,
  "next_url": "https://api.polygon.io/v3/reference/tickers?cursor=YWN0aXZlPXRydWUmZGF0ZT0yMDIxLTA0LTI1JmxpbWl0PTEmb3JkZXI9YXNjJnBhZ2VfbWFya2VyPUElN0M5YWRjMjY0ZTgyM2E1ZjBiOGUyNDc5YmZiOGE1YmYwNDVkYzU0YjgwMDcyMWE2YmI1ZjBjMjQwMjU4MjFmNGZiJnNvcnQ9dGlja2Vy",
  "request_id": "e70013d92930de90e089dc8fa098888e",
  "results": [
    {
      "active": true,
      "cik": "0001090872",
      "composite_figi": "BBG000BWQYZ5",
      "currency_name": "usd",
      "last_updated_utc": "2021-04-25T00:00:00Z",
      "locale": "us",
      "market": "stocks",
      "name": "Agilent Technologies Inc.",
      "primary_exchange": "XNYS",
      "share_class_figi": "BBG001SCTQY4",
      "ticker": "A",
      "type": "CS"
    }
  ],
  "status": "OK"
}
Market Holidays
get
/v1/marketstatus/upcoming
Get upcoming market holidays and their open/close times.

https://api.polygon.io/v1/marketstatus/upcoming?apiKey=a8waWkOhp6Bz4nZA64jDVqgZN6zm_bh6

Copy

Run Query
Response Attributes
responsearray
closestring
The market close time on the holiday (if it's not closed).

datestring
The date of the holiday.

exchangestring
Which market the record is for.

namestring
The name of the holiday.

openstring
The market open time on the holiday (if it's not closed).

statusstring
The status of the market on the holiday.

Was this helpful?
Help us improve

Yes

No
Response Object
[
  {
    "date": "2020-11-26",
    "exchange": "NYSE",
    "name": "Thanksgiving",
    "status": "closed"
  },
  {
    "date": "2020-11-26",
    "exchange": "NASDAQ",
    "name": "Thanksgiving",
    "status": "closed"
  },
  {
    "date": "2020-11-26",
    "exchange": "OTC",
    "name": "Thanksgiving",
    "status": "closed"
  },
  {
    "close": "2020-11-27T18:00:00.000Z",
    "date": "2020-11-27",
    "exchange": "NASDAQ",
    "name": "Thanksgiving",
    "open": "2020-11-27T14:30:00.000Z",
    "status": "early-close"
  },
  {
    "close": "2020-11-27T18:00:00.000Z",
    "date": "2020-11-27",
    "exchange": "NYSE",
    "name": "Thanksgiving",
    "open": "2020-11-27T14:30:00.000Z",
    "status": "early-close"
  }
]
Market Status
get
/v1/marketstatus/now
Get the current trading status of the exchanges and overall financial markets.

https://api.polygon.io/v1/marketstatus/now?apiKey=a8waWkOhp6Bz4nZA64jDVqgZN6zm_bh6

Copy

Run Query
Response Attributes
afterHoursboolean
Whether or not the market is in post-market hours.

currenciesobject
cryptostring
The status of the crypto market.

fxstring
The status of the forex market.

earlyHoursboolean
Whether or not the market is in pre-market hours.

exchangesobject
nasdaqstring
The status of the Nasdaq market.

nysestring
The status of the NYSE market.

otcstring
The status of the OTC market.

indicesGroupsobject
cccystring
The status of Cboe Streaming Market Indices Cryptocurrency ("CCCY") indices trading hours.

cgistring
The status of Cboe Global Indices ("CGI") trading hours.

dow_jonesstring
The status of Dow Jones indices trading hours

ftse_russellstring
The status of Financial Times Stock Exchange Group ("FTSE") Russell indices trading hours.

mscistring
The status of Morgan Stanley Capital International ("MSCI") indices trading hours.

mstarstring
The status of Morningstar ("MSTAR") indices trading hours.

mstarc
The status of Morningstar Customer ("MSTARC") indices trading hours.

nasdaqstring
The status of National Association of Securities Dealers Automated Quotations ("Nasdaq") indices trading hours.

s_and_pstring
The status of Standard & Poors's ("S&P") indices trading hours.

societe_generalestring
The status of Societe Generale indices trading hours.

marketstring
The status of the market as a whole.

serverTimestring
The current time of the server, returned as a date-time in RFC3339 format.

Was this helpful?
Help us improve

Yes

No
Response Object
{
  "afterHours": true,
  "currencies": {
    "crypto": "open",
    "fx": "open"
  },
  "earlyHours": false,
  "exchanges": {
    "nasdaq": "extended-hours",
    "nyse": "extended-hours",
    "otc": "closed"
  },
  "market": "extended-hours",
  "serverTime": "2020-11-10T17:37:37-05:00"
}
Conditions
get
/v3/reference/conditions
List all conditions that Polygon.io uses.

Parameters
asset_class

fx
Filter for conditions within a given asset class.

data_type

Filter by data type.

id
Filter for conditions with a given ID.

sip

Filter by SIP. If the condition contains a mapping for that SIP, the condition will be returned.

order

Order results based on the sort field.

limit
10
Limit the number of results returned, default is 10 and max is 1000.

sort

Sort field used for ordering.

https://api.polygon.io/v3/reference/conditions?asset_class=fx&limit=10&apiKey=a8waWkOhp6Bz4nZA64jDVqgZN6zm_bh6

Copy

JSON

Run Query
Response Attributes
count*integer
The total number of results for this request.

next_urlstring
If present, this value can be used to fetch the next page of data.

request_id*string
A request ID assigned by the server.

results*array
An array of conditions that match your query.

abbreviationstring
A commonly-used abbreviation for this condition.

asset_class*enum [stocks, options, crypto, fx]
An identifier for a group of similar financial instruments.

data_types*array [string]
Data types that this condition applies to.

descriptionstring
A short description of the semantics of this condition.

exchangeinteger
If present, mapping this condition from a Polygon.io code to a SIP symbol depends on this attribute. In other words, data with this condition attached comes exclusively from the given exchange.

id*integer
An identifier used by Polygon.io for this condition. Unique per data type.

legacyboolean
If true, this condition is from an old version of the SIPs' specs and no longer is used. Other conditions may or may not reuse the same symbol as this one.

name*string
The name of this condition.

sip_mapping*object
A mapping to a symbol for each SIP that has this condition.

CTAstring
OPRAstring
UTPstring
type*enum [sale_condition, quote_condition, sip_generated_flag, financial_status_indicator, short_sale_restriction_indicator, settlement_condition, market_condition, trade_thru_exempt]
An identifier for a collection of related conditions.

update_rulesobject
A list of aggregation rules.

consolidated*object
Describes aggregation rules on a consolidated (all exchanges) basis.

updates_high_low*boolean
Whether or not trades with this condition update the high/low.

updates_open_close*boolean
Whether or not trades with this condition update the open/close.

updates_volume*boolean
Whether or not trades with this condition update the volume.

market_center*object
Describes aggregation rules on a per-market-center basis.

updates_high_low*boolean
Whether or not trades with this condition update the high/low.

updates_open_close*boolean
Whether or not trades with this condition update the open/close.

updates_volume*boolean
Whether or not trades with this condition update the volume.

status*string
The status of this request's response.

Was this helpful?
Help us improve

Yes

No
Response Object
{
  "count": 1,
  "request_id": "31d59dda-80e5-4721-8496-d0d32a654afe",
  "results": [
    {
      "asset_class": "stocks",
      "data_types": [
        "trade"
      ],
      "id": 2,
      "name": "Average Price Trade",
      "sip_mapping": {
        "CTA": "B",
        "UTP": "W"
      },
      "type": "condition",
      "update_rules": {
        "consolidated": {
          "updates_high_low": false,
          "updates_open_close": false,
          "updates_volume": true
        },
        "market_center": {
          "updates_high_low": false,
          "updates_open_close": false,
          "updates_volume": true
        }
      }
    }
  ],
  "status": "OK"
}
Exchanges
get
/v3/reference/exchanges
List all exchanges that Polygon.io knows about.

Parameters
asset_class

fx
Filter by asset class.

locale

Filter by locale.

https://api.polygon.io/v3/reference/exchanges?asset_class=fx&apiKey=a8waWkOhp6Bz4nZA64jDVqgZN6zm_bh6

Copy

JSON

Run Query
Response Attributes
countinteger
The total number of results for this request.

request_id*string
A request ID assigned by the server.

resultsarray
acronymstring
A commonly used abbreviation for this exchange.

asset_class*enum [stocks, options, crypto, fx]
An identifier for a group of similar financial instruments.

id*integer
A unique identifier used by Polygon.io for this exchange.

locale*enum [us, global]
An identifier for a geographical location.

micstring
The Market Identifier Code of this exchange (see ISO 10383).

name*string
Name of this exchange.

operating_micstring
The MIC of the entity that operates this exchange.

participant_idstring
The ID used by SIP's to represent this exchange.

type*enum [exchange, TRF, SIP]
Represents the type of exchange.

urlstring
A link to this exchange's website, if one exists.

status*string
The status of this request's response.

Was this helpful?
Help us improve

Yes

No
Response Object
{
  "count": 1,
  "request_id": "31d59dda-80e5-4721-8496-d0d32a654afe",
  "results": [
    {
      "acronym": "AMEX",
      "asset_class": "stocks",
      "id": 1,
      "locale": "us",
      "mic": "XASE",
      "name": "NYSE American, LLC",
      "operating_mic": "XNYS",
      "participant_id": "A",
      "type": "exchange",
      "url": "https://www.nyse.com/markets/nyse-american"
    }
  ],
  "status": "OK"
}
Forex WebSocket Documentation
The Polygon.io Forex WebSocket API provides streaming access to the latest financial market data for global currency pairs. You can specify which channels you want to consume by sending instructions in the form of actions. Our WebSockets emit events to notify you when an event has occurred in a channel you've subscribed to.

Our WebSocket APIs are based on entitlements that control which WebSocket Clusters you can connect to and which kinds of data you can access. Examples in these docs include your API key, which only you can see, and are personalized based on your entitlements.

Step 1: Connect
Your current plan includes 1 connection to wss://socket.polygon.io/forex. If you attempt additional connections, the existing connection will be disconnected. If you need more simultaneous connections to this cluster, you can contact support.

Connecting to a cluster:

Real-time:wscat -c wss://socket.polygon.io/forex

Copy
On connection you will receive the following message:

[{
	"ev":"status",
	"status":"connected",
	"message": "Connected Successfully"
}]
Step 2: Authenticate
You must authenticate before you can make any other requests.

{"action":"auth","params":"a8waWkOhp6Bz4nZA64jDVqgZN6zm_bh6"}

Copy
On successful authentication you will receive the following message:

[{
	"ev":"status",
	"status":"auth_success",
	"message": "authenticated"
}]
Step 3: Subscribe
Once authenticated, you can request a stream. You can request multiple streams in the same request.

{"action":"subscribe","params":"C.C:EUR-USD"}

Copy
You can also request multiple streams from the same cluster.

{"action":"subscribe","params":"C.C:EUR-USD,C.C:JPY-USD"}

Copy
Usage
Things happen very quickly in the world of finance, which means a Polygon.io WebSocket client must be able to handle many incoming messages per second. Due to the nature of the WebSocket protocol, if a client is slow to consume messages from the server, Polygon.io's server must buffer messages and send them only as fast as the client can consume them. To help prevent the message buffer from getting too long, Polygon.io may send more than one JSON object in a single WebSocket message. We accomplish this by wrapping all messages in a JSON array, and adding more objects to the array if the message buffer is getting longer. For example, consider a WebSocket message with a single trade event in it:

[
    {"ev":"T","sym":"C.C:EUR-USD","i":"50578","x":4,"p":215.9721,"s":100,"t":1611082428813,"z":3}
]
If your client is consuming a bit slow, or 2+ events happened in very short succession, you may receive a single WebSocket message with more than one event inside it, like this:

[
    {"ev":"T","sym":"C.C:EUR-USD","i":"50578","x":4,"p":215.9721,"s":100,"t":1611082428813,"z":3}, 
    {"ev":"T","sym":"C.C:JPY-USD","i":"12856","x":4,"p":215.989,"s":1,"c":[37],"t":1611082428814,"z":3}
]
Note that if a client is consuming messages too slowly for too long, Polygon.io's server-side buffer may get too large. If that happens, Polygon.io will terminate the WebSocket connection. You can check your account dashboard to see if a connection was terminated as a slow consumer. If this happens to you consistently, consider subscribing to fewer symbols or channels.

Your Plan
Currencies Starter
Real-time Data
1 Forex Cluster Connection
Manage Subscription
Client Libraries
Python Logo
Python
client-python
Go Logo
Go
client-go
Javascript Logo
Javascript
client-js
PHP Logo
PHP
client-php
Kotlin Logo
Kotlin
client-jvm
Aggregates (Per Minute)
ws
Real-time:wss://socket.polygon.io/forex
Stream real-time per-minute forex aggregates for a given forex pair.

Parameters
ticker
*
*
Specify a forex pair in the format {from}/{to} or use * to subscribe to all forex pairs. You can also use a comma separated list to subscribe to multiple forex pairs. You can retrieve active forex tickers from our Forex Tickers API.

{"action":"subscribe", "params":"CA.*"}

Copy
Response Attributes
evenum [CA]
The event type.

pairstring
The currency pair.

onumber
The open price for this aggregate window.

cnumber
The close price for this aggregate window.

hnumber
The high price for this aggregate window.

lnumber
The low price for this aggregate window.

vinteger
The volume of trades during this aggregate window.

sinteger
The start timestamp of this aggregate window in Unix Milliseconds.

einteger
The end timestamp of this aggregate window in Unix Milliseconds.

Was this helpful?
Help us improve

Yes

No
Response Object
{
  "ev": "CA",
  "pair": "USD/EUR",
  "o": 0.8687,
  "c": 0.86889,
  "h": 0.86889,
  "l": 0.8686,
  "v": 20,
  "s": 1539145740000
}
Aggregates (Per Second)
ws
Real-time:wss://socket.polygon.io/forex
Stream real-time per-second forex aggregates for a given forex pair.

Parameters
ticker
*
*
Specify a forex pair in the format {from}/{to} or use * to subscribe to all forex pairs. You can also use a comma separated list to subscribe to multiple forex pairs. You can retrieve active forex tickers from our Forex Tickers API.

{"action":"subscribe", "params":"CAS.*"}

Copy
Response Attributes
evenum [CAS]
The event type.

pairstring
The currency pair.

onumber
The open price for this aggregate window.

cnumber
The close price for this aggregate window.

hnumber
The high price for this aggregate window.

lnumber
The low price for this aggregate window.

vinteger
The volume of trades during this aggregate window.

sinteger
The start timestamp of this aggregate window in Unix Milliseconds.

einteger
The end timestamp of this aggregate window in Unix Milliseconds.

Was this helpful?
Help us improve

Yes

No
Response Object
{
  "ev": "CAS",
  "pair": "USD/EUR",
  "o": 0.8687,
  "c": 0.86889,
  "h": 0.86889,
  "l": 0.8686,
  "v": 20,
  "s": 1539145740000
}
Quotes
ws
Real-time:wss://socket.polygon.io/forex
Stream real-time forex quotes for a given forex pair.

Parameters
ticker
*
*
Specify a forex pair in the format {from}/{to} or use * to subscribe to all forex pairs. You can also use a comma separated list to subscribe to multiple forex pairs. You can retrieve active forex tickers from our Forex Tickers API.

{"action":"subscribe", "params":"C.*"}

Copy
Response Attributes
evenum [C]
The event type.

pstring
The current pair.

xinteger
The exchange ID. See Exchanges for Polygon.io's mapping of exchange IDs.

anumber
The ask price.

bnumber
The bid price.

tinteger
The Timestamp in Unix MS.

Was this helpful?
Help us improve

Yes

No
Response Object
{
  "ev": "C",
  "p": "USD/CNH",
  "x": "44",
  "a": 6.83366,
  "b": 6.83363,
  "t": 1536036818784
}
Fair Market Value
ws
Business:wss://business.polygon.io/forex
Real-time fair market value for a given forex ticker symbol.

Requires a "Currencies Enterprise" subscription
Upgrade
Parameters
ticker
*
*
Specify a forex pair in the format {from}/{to} or use * to subscribe to all forex pairs. You can also use a comma separated list to subscribe to multiple forex pairs. You can retrieve active forex tickers from our Forex Tickers API.

{"action":"subscribe", "params":"FMV.*"}

Copy
Response Attributes
evenum [FMV]
The event type.

