import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from typing import Tuple, Any
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import datetime
from urllib import parse
import json
import logging
from slack_webhook import Slack
from linenotipy import Line
from discordwebhook import Discord
import time
import dateutil.parser
import matplotlib.dates as mdates


class Bot(object):
    WINTER_TIME = 21
    SUMMER_TIME = 20

    def __init__(
        self,
        *,
        account_id: str,
        access_token: str,
        environment: str = "practice",
        instrument: str = "EUR_USD",
        granularity: str = "D",
        trading_time: int = SUMMER_TIME,
        slack_webhook_url: str = "",
        discord_webhook_url: str = "",
        line_notify_token: str = "",
    ) -> None:
        self.BUY = 1
        self.SELL = -1
        self.EXIT = False
        self.ENTRY = True
        self.trading_time = trading_time
        self.account_id = account_id
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(access_token),
        }
        if environment == "practice":
            self.base_url = "https://api-fxpractice.oanda.com"
        else:
            self.base_url = "https://api-fxtrade.oanda.com"
        self.sched = BlockingScheduler()
        self.instrument = instrument
        self.granularity = granularity
        if len(granularity) > 1:
            if granularity[0] == "S":
                self.sched.add_job(self._job, "cron", second="*/" + granularity[1:])
            elif granularity[0] == "M":
                self.sched.add_job(self._job, "cron", minute="*/" + granularity[1:])
            elif granularity[0] == "H":
                self.sched.add_job(self._job, "cron", hour="*/" + granularity[1:])
        else:
            if granularity == "D":
                self.sched.add_job(self._job, "cron", day="*")
            elif granularity == "W":
                self.sched.add_job(self._job, "cron", week="*")
            elif granularity == "M":
                self.sched.add_job(self._job, "cron", month="*")
        if slack_webhook_url == "":
            self.slack = None
        else:
            self.slack = Slack(url=slack_webhook_url)
        if line_notify_token == "":
            self.line = None
        else:
            self.line = Line(token=line_notify_token)
        if discord_webhook_url == "":
            self.discord = None
        else:
            self.discord = Discord(url=discord_webhook_url)
        formatter = logging.Formatter(
            "%(asctime)s - %(funcName)s - %(levelname)s - %(message)s"
        )
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)
        self.log.addHandler(handler)
        if "JPY" in self.instrument:
            self.point = 0.01
        else:
            self.point = 0.0001
        self.units = 10000  # currency unit
        self.take_profit = 0
        self.stop_loss = 0
        self.buy_entry = (
            self.buy_exit
        ) = self.sell_entry = self.sell_exit = pd.DataFrame()

    def _candles(
        self, *, from_date: str = "", to_date: str = "", count: str = "5000"
    ) -> pd.DataFrame:
        url = "{}/v3/instruments/{}/candles".format(self.base_url, self.instrument)
        params = {"granularity": self.granularity, "count": count}
        if from_date != "":
            _dt = dateutil.parser.parse(from_date)
            params["from"] = str(
                datetime.datetime(
                    _dt.year, _dt.month, _dt.day, tzinfo=datetime.timezone.utc
                ).date()
            )
        if to_date != "":
            _dt = dateutil.parser.parse(to_date)
            params["to"] = str(
                datetime.datetime(
                    _dt.year, _dt.month, _dt.day, tzinfo=datetime.timezone.utc
                ).date()
            )
        data = []
        if "from" in params and "to" in params:
            _from = params["from"]
            _to = params["to"]
            del params["to"]
            while _to > _from:
                time.sleep(0.5)
                params["from"] = _from
                res = requests.get(url, headers=self.headers, params=params)
                if res.status_code != 200:
                    self._error(
                        "status_code {} - {}".format(res.status_code, res.json())
                    )
                for r in res.json()["candles"]:
                    data.append(
                        [
                            pd.to_datetime(r["time"]),
                            float(r["mid"]["o"]),
                            float(r["mid"]["h"]),
                            float(r["mid"]["l"]),
                            float(r["mid"]["c"]),
                            float(r["volume"]),
                        ]
                    )
                _dt = pd.to_datetime(res.json()["candles"][-1]["time"])
                _from = str(datetime.date(_dt.year, _dt.month, _dt.day))
        else:
            res = requests.get(url, headers=self.headers, params=params)
            if res.status_code != 200:
                self._error("status_code {} - {}".format(res.status_code, res.json()))
            for r in res.json()["candles"]:
                data.append(
                    [
                        pd.to_datetime(r["time"]),
                        float(r["mid"]["o"]),
                        float(r["mid"]["h"]),
                        float(r["mid"]["l"]),
                        float(r["mid"]["c"]),
                        float(r["volume"]),
                    ]
                )
        self.df = (
            pd.DataFrame(data, columns=["T", "O", "H", "L", "C", "V"])
            .set_index("T")
            .drop_duplicates()
        )
        return self.df

    def __accounts(self) -> requests.models.Response:
        url = "{}/v3/accounts/{}".format(self.base_url, self.account_id)
        res = requests.get(url, headers=self.headers)
        if res.status_code != 200:
            self._error("status_code {} - {}".format(res.status_code, res.json()))
        return res

    def _account(self) -> Tuple[bool, bool]:
        buy_position = False
        sell_position = False
        for pos in self.__accounts().json()["account"]["positions"]:
            if pos["instrument"] == self.instrument:
                if pos["long"]["units"] != "0":
                    buy_position = True
                if pos["short"]["units"] != "0":
                    sell_position = True
        return buy_position, sell_position

    def __order(self, data: Any) -> requests.models.Response:
        url = "{}/v3/accounts/{}/orders".format(self.base_url, self.account_id)
        res = requests.post(url, headers=self.headers, data=json.dumps(data))
        if res.status_code != 201:
            self._error("status_code {} - {}".format(res.status_code, res.json()))
        return res

    def _order(self, sign: int, entry: bool = False) -> None:
        order = {}
        order["instrument"] = self.instrument
        order["units"] = str(self.units * sign)
        order["type"] = "MARKET"
        order["positionFill"] = "DEFAULT"
        res = self.__order({"order": order})
        order_id = res.json()["orderFillTransaction"]["id"]
        price = float(res.json()["orderFillTransaction"]["price"])
        if self.stop_loss != 0 and entry:
            stop_loss = {}
            stop_loss["timeInForce"] = "GTC"
            stop_loss["price"] = str(
                round(price + (self.stop_loss * self.point * -sign), 3)
            )
            stop_loss["type"] = "STOP_LOSS"
            stop_loss["tradeID"] = order_id
            self.__order({"order": stop_loss})
        if self.take_profit != 0 and entry:
            take_profit = {}
            take_profit["timeInForce"] = "GTC"
            take_profit["price"] = str(
                round(price + (self.take_profit * self.point * sign), 3)
            )
            take_profit["type"] = "TAKE_PROFIT"
            take_profit["tradeID"] = order_id
            self.__order({"order": take_profit})

    def _is_close(self) -> bool:
        utcnow = datetime.datetime.utcnow()
        hour = utcnow.hour
        weekday = utcnow.weekday()
        if (
            (4 == weekday and self.trading_time < hour)
            or 5 == weekday
            or (6 == weekday and self.trading_time >= hour)
        ):
            return True
        return False

    def _job(self) -> None:
        if self._is_close():
            return None
        self._candles(count="500")
        self.strategy()
        buy_position, sell_position = self._account()
        buy_entry = self.buy_entry[-1]
        sell_entry = self.sell_entry[-1]
        buy_exit = self.buy_exit[-1]
        sell_exit = self.sell_exit[-1]
        # buy entry
        if buy_entry and not buy_position:
            if sell_position:
                self._order(self.BUY)
            self._order(self.BUY, self.ENTRY)
            return None
        # sell entry
        if sell_entry and not sell_position:
            if buy_position:
                self._order(self.SELL)
            self._order(self.SELL, self.ENTRY)
            return None
        # buy exit
        if buy_exit and buy_position:
            self._order(self.SELL)
        # sell exit
        if sell_exit and sell_position:
            self._order(self.BUY)

    def _error(self, message: Any = {}) -> None:
        self.log.error(message)
        if self.slack is not None:
            self.slack.post(text=message)
        if self.line is not None:
            self.line.post(message=message)
        if self.discord is not None:
            self.discord.post(content=message)

    def __transactions(self, params: Any = {}) -> requests.models.Response:
        url = "{}/v3/accounts/{}/transactions".format(self.base_url, self.account_id)
        res = requests.get(url, headers=self.headers, params=params)
        if res.status_code != 200:
            self._error("status_code {} - {}".format(res.status_code, res.json()))
        return res

    def __transactions_sinceid(self, params: Any = {}) -> requests.models.Response:
        url = "{}/v3/accounts/{}/transactions/sinceid".format(
            self.base_url, self.account_id
        )
        res = requests.get(url, headers=self.headers, params=params)
        if res.status_code != 200:
            self._error("status_code {} - {}".format(res.status_code, res.json()))
        return res

    def report(self, *, days: int = -1, filename: str = "",) -> None:
        tran = self.__transactions(
            {
                "from": (
                    datetime.datetime.utcnow().date() + datetime.timedelta(days=days)
                ),
                "type": "ORDER_FILL",
            }
        ).json()
        if len(tran["pages"]) == 0:
            print("Transactions do not exist")
            return None
        id = parse.parse_qs(parse.urlparse(tran["pages"][0]).query)["from"]
        data = []
        for t in self.__transactions_sinceid({"id": id, "type": "ORDER_FILL"}).json()[
            "transactions"
        ]:
            if float(t["pl"]) == 0.0:
                continue
            data.append(
                [
                    pd.to_datetime(t["time"]),
                    t["id"],
                    float(t["pl"]),
                    round(float(t["pl"]), 2),
                    float(t["price"]),
                    float(t["accountBalance"]),
                ]
            )
        df = pd.DataFrame(
            data, columns=["time", "id", "pl", "rr", "price", "accountBalance"]
        ).set_index("time")

        s = pd.Series(dtype="object")
        s.loc["total profit"] = round(df["pl"].sum(), 3)
        s.loc["total trades"] = len(df["pl"])
        s.loc["win rate"] = round(len(df[df["pl"] > 0]) / len(df["pl"]) * 100, 3)
        s.loc["profit factor"] = round(
            df[df["pl"] > 0]["pl"].sum() / df[df["pl"] <= 0]["pl"].sum(), 3
        )
        s.loc["maximum drawdown"] = round(
            (df["accountBalance"].cummax() - df["accountBalance"]).max(), 3
        )
        s.loc["recovery factor"] = round(
            df["pl"].sum()
            / (df["accountBalance"].cummax() - df["accountBalance"]).max(),
            3,
        )
        s.loc["riskreward ratio"] = round(
            (df[df["pl"] > 0]["pl"].sum() / len(df[df["pl"] > 0]))
            / (df[df["pl"] <= 0]["pl"].sum() / len(df[df["pl"] <= 0])),
            3,
        )
        s.loc["sharpe ratio"] = round(df["rr"].mean() / df["rr"].std(), 3)
        s.loc["average return"] = round(df["rr"].mean(), 3)
        print(s)

        fig = plt.figure()
        fig.subplots_adjust(
            wspace=0.2, hspace=0.7, left=0.095, right=0.95, bottom=0.095, top=0.95
        )
        ax1 = fig.add_subplot(3, 1, 1)
        ax1.plot(df["price"], label="price")
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M"))
        ax1.legend()
        ax2 = fig.add_subplot(3, 1, 2)
        ax2.plot(df["accountBalance"], label="accountBalance")
        ax2.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M"))
        ax2.legend()
        ax3 = fig.add_subplot(3, 1, 3)
        ax3.hist(df["rr"], 50, rwidth=0.9)
        ax3.axvline(
            df["rr"].mean(), color="orange", label="average return",
        )
        ax3.legend()
        if filename == "":
            plt.show()
        else:
            plt.savefig(filename)

    def strategy(self) -> None:
        pass

    def backtest(
        self, *, from_date: str = "", to_date: str = "", filename: str = ""
    ) -> None:
        csv = "{}-{}-{}-{}.csv".format(
            self.instrument, self.granularity, from_date, to_date
        )
        if os.path.exists(csv):
            self.df = pd.read_csv(
                csv, index_col=0, parse_dates=True, infer_datetime_format=True
            )
        else:
            self._candles(from_date=from_date, to_date=to_date)
            if from_date != "" and to_date != "":
                self.df.to_csv(csv)
        self.strategy()
        o = self.df.O.values
        L = self.df.L.values
        h = self.df.H.values
        N = len(self.df)
        long_trade = np.zeros(N)
        short_trade = np.zeros(N)

        # buy entry
        buy_entry_s = np.hstack((False, self.buy_entry[:-1]))  # shift
        long_trade[buy_entry_s] = o[buy_entry_s]
        # buy exit
        buy_exit_s = np.hstack((False, self.buy_exit[:-2], True))  # shift
        long_trade[buy_exit_s] = -o[buy_exit_s]
        # sell entry
        sell_entry_s = np.hstack((False, self.sell_entry[:-1]))  # shift
        short_trade[sell_entry_s] = o[sell_entry_s]
        # sell exit
        sell_exit_s = np.hstack((False, self.sell_exit[:-2], True))  # shift
        short_trade[sell_exit_s] = -o[sell_exit_s]

        long_pl = pd.Series(np.zeros(N))  # profit/loss of buy position
        short_pl = pd.Series(np.zeros(N))  # profit/loss of sell position
        buy_price = sell_price = 0
        long_rr = []  # long return rate
        short_rr = []  # short return rate
        stop_loss = take_profit = 0

        for i in range(1, N):
            # buy entry
            if long_trade[i] > 0:
                if buy_price == 0:
                    buy_price = long_trade[i]
                    short_trade[i] = -buy_price  # sell exit
                else:
                    long_trade[i] = 0

            # sell entry
            if short_trade[i] > 0:
                if sell_price == 0:
                    sell_price = short_trade[i]
                    long_trade[i] = -sell_price  # buy exit
                else:
                    short_trade[i] = 0

            # buy exit
            if long_trade[i] < 0:
                if buy_price != 0:
                    long_pl[i] = (
                        -(buy_price + long_trade[i]) * self.units
                    )  # profit/loss fixed
                    long_rr.append(
                        round(long_pl[i] / buy_price * 100, 2)
                    )  # long return rate
                    buy_price = 0
                else:
                    long_trade[i] = 0

            # sell exit
            if short_trade[i] < 0:
                if sell_price != 0:
                    short_pl[i] = (
                        sell_price + short_trade[i]
                    ) * self.units  # profit/loss fixed
                    short_rr.append(
                        round(short_pl[i] / sell_price * 100, 2)
                    )  # short return rate
                    sell_price = 0
                else:
                    short_trade[i] = 0

            # close buy position with stop loss
            if buy_price != 0 and self.stop_loss > 0:
                stop_price = buy_price - self.stop_loss * self.point
                if L[i] <= stop_price:
                    long_trade[i] = -stop_price
                    long_pl[i] = (
                        -(buy_price + long_trade[i]) * self.units
                    )  # profit/loss fixed
                    long_rr.append(
                        round(long_pl[i] / buy_price * 100, 2)
                    )  # long return rate
                    buy_price = 0
                    stop_loss += 1

            # close buy positon with take profit
            if buy_price != 0 and self.take_profit > 0:
                limit_price = buy_price + self.take_profit * self.point
                if h[i] >= limit_price:
                    long_trade[i] = -limit_price
                    long_pl[i] = (
                        -(buy_price + long_trade[i]) * self.units
                    )  # profit/loss fixed
                    long_rr.append(
                        round(long_pl[i] / buy_price * 100, 2)
                    )  # long return rate
                    buy_price = 0
                    take_profit += 1

            # close sell position with stop loss
            if sell_price != 0 and self.stop_loss > 0:
                stop_price = sell_price + self.stop_loss * self.point
                if h[i] >= stop_price:
                    short_trade[i] = -stop_price
                    short_pl[i] = (
                        sell_price + short_trade[i]
                    ) * self.units  # profit/loss fixed
                    short_rr.append(
                        round(short_pl[i] / sell_price * 100, 2)
                    )  # short return rate
                    sell_price = 0
                    stop_loss += 1

            # close sell position with take profit
            if sell_price != 0 and self.take_profit > 0:
                limit_price = sell_price - self.take_profit * self.point
                if L[i] <= limit_price:
                    short_trade[i] = -limit_price
                    short_pl[i] = (
                        sell_price + short_trade[i]
                    ) * self.units  # profit/loss fixed
                    short_rr.append(
                        round(short_pl[i] / sell_price * 100, 2)
                    )  # short return rate
                    sell_price = 0
                    take_profit += 1

        win_trades = np.count_nonzero(long_pl.clip(lower=0)) + np.count_nonzero(
            short_pl.clip(lower=0)
        )
        lose_trades = np.count_nonzero(long_pl.clip(upper=0)) + np.count_nonzero(
            short_pl.clip(upper=0)
        )
        trades = (np.count_nonzero(long_trade) // 2) + (
            np.count_nonzero(short_trade) // 2
        )
        gross_profit = long_pl.clip(lower=0).sum() + short_pl.clip(lower=0).sum()
        gross_loss = long_pl.clip(upper=0).sum() + short_pl.clip(upper=0).sum()
        profit_pl = gross_profit + gross_loss
        self.equity = (long_pl + short_pl).cumsum()
        mdd = (self.equity.cummax() - self.equity).max()
        self.return_rate = pd.Series(short_rr + long_rr)

        s = pd.Series(dtype="object")
        s.loc["total profit"] = round(profit_pl, 3)
        s.loc["total trades"] = trades
        s.loc["win rate"] = round(win_trades / trades * 100, 3)
        s.loc["profit factor"] = round(-gross_profit / gross_loss, 3)
        s.loc["maximum drawdown"] = round(mdd, 3)
        s.loc["recovery factor"] = round(profit_pl / mdd, 3)
        s.loc["riskreward ratio"] = round(
            -(gross_profit / win_trades) / (gross_loss / lose_trades), 3
        )
        s.loc["sharpe ratio"] = round(
            self.return_rate.mean() / self.return_rate.std(), 3
        )
        s.loc["average return"] = round(self.return_rate.mean(), 3)
        s.loc["stop loss"] = stop_loss
        s.loc["take profit"] = take_profit
        print(s)

        fig = plt.figure()
        fig.subplots_adjust(
            wspace=0.2, hspace=0.5, left=0.095, right=0.95, bottom=0.095, top=0.95
        )
        ax1 = fig.add_subplot(3, 1, 1)
        ax1.plot(self.df.C, label="close")
        ax1.legend()
        ax2 = fig.add_subplot(3, 1, 2)
        ax2.plot(self.equity, label="equity")
        ax2.legend()
        ax3 = fig.add_subplot(3, 1, 3)
        ax3.hist(self.return_rate, 50, rwidth=0.9)
        ax3.axvline(
            sum(self.return_rate) / len(self.return_rate),
            color="orange",
            label="average return",
        )
        ax3.legend()
        if filename == "":
            plt.show()
        else:
            plt.savefig(filename)

    def run(self) -> None:
        self.sched.start()

    def sma(self, *, period: int, price: str = "C") -> pd.DataFrame:
        return self.df[price].rolling(period).mean()

    def ema(self, *, period: int, price: str = "C") -> pd.DataFrame:
        return self.df[price].ewm(span=period).mean()

    def bbands(
        self, *, period: int = 20, band: int = 2, price: str = "C"
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        std = self.df[price].rolling(period).std()
        mean = self.df[price].rolling(period).mean()
        return mean + (std * band), mean, mean - (std * band)

    def macd(
        self,
        *,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        price: str = "C",
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        macd = (
            self.df[price].ewm(span=fast_period).mean()
            - self.df[price].ewm(span=slow_period).mean()
        )
        signal = macd.ewm(span=signal_period).mean()
        return macd, signal

    def stoch(
        self, *, k_period: int = 5, d_period: int = 3
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        k = (
            (self.df.C - self.df.L.rolling(k_period).min())
            / (self.df.H.rolling(k_period).max() - self.df.L.rolling(k_period).min())
            * 100
        )
        d = k.rolling(d_period).mean()
        return k, d

    def mom(self, *, period: int = 10, price: str = "C") -> pd.DataFrame:
        return self.df[price].diff(period)

    def rsi(self, *, period: int = 14, price: str = "C") -> pd.DataFrame:
        return 100 - 100 / (
            1
            - self.df[price].diff().clip(lower=0).rolling(period).mean()
            / self.df[price].diff().clip(upper=0).rolling(period).mean()
        )

    def ao(self, *, fast_period: int = 5, slow_period: int = 34) -> pd.DataFrame:
        return ((self.df.H + self.df.L) / 2).rolling(fast_period).mean() - (
            (self.df.H + self.df.L) / 2
        ).rolling(slow_period).mean()
