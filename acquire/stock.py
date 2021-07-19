# -*- coding: utf-8 -*-#
"""
@File    :   stock.py    
@Contact :   sheng_jun@yeah.net
@Author  :   Ace
@Description: 
@Modify Time      @Version    @Desciption
------------      --------    -----------
2021-06-30 0:47    1.0         None
"""
import time

import pandas
import pandas as pd
from acquire.config import api
from datetime import datetime
import os
from util import response
from util import location
from util import location


#
# def _get_from_waditu(api_name, fields: str = '', **kwargs):
#     return response.get_from_waditu(api_name, fields, **kwargs)


class BasicInfo:
    """
    @Desc:描述A股市场的股票基本信息，包括：股票列表
    @Maybe:之后可能会继续增加成分股，上市公司基本信息，交易所日历，IPO等信息
    """

    def __init__(self):
        self.stock_basic = response.get_from_waditu(api_name="stock_basic", fields="ts_code,symbol,name,industry,list_date")
        self.ts_code_list = list(self.stock_basic["ts_code"])
        self.symbol_list = list(self.stock_basic["symbol"])
        self.name_list = list(self.stock_basic["name"])
        self.start_date_list = list(self.stock_basic["list_date"])
        self.code2name = dict(zip(self.ts_code_list, self.name_list))
        self.name2code = dict(zip(self.name_list, self.ts_code_list))
        self.code2symbol = dict(zip(self.ts_code_list, self.symbol_list))
        self.symbol2code = dict(zip(self.symbol_list, self.ts_code_list))
        self.code2start = dict(zip(self.ts_code_list, self.start_date_list))


class History:
    """
    @Desc：获取整个A股市场的历史数据
    数据分两快：basic，price
    """

    def __init__(self, code_date, root):
        self.code_date = code_date
        self.root = root

    def save_basic_price_data(self):
        today = datetime.today().strftime("%Y%m%d")
        for ts_code, start_time in self.code_date.items():
            price_df = response.get_from_waditu(api_name="daily", ts_code=ts_code, start_date=start_time, end_date=today, fields="ts_code,trade_date,open,high,low,close,pre_close,vol,amount")
            last_date = price_df.iloc[-1, 1]
            if last_date > start_time:
                next_df = response.get_from_waditu(api_name="daily", ts_code=ts_code, start_date=start_time, end_date=last_date, fields="ts_code,trade_date,open,high,low,close,pre_close,vol,amount")
                price_df = price_df.append(next_df, ignore_index=True)
            price_df.sort_values(by="trade_date", ascending=True, ignore_index=True, inplace=True)

            basic_df = response.get_from_waditu(api_name="daily_basic", ts_code=ts_code, start_date=start_time, end_date=today)
            last_date = basic_df.iloc[-1, 1]
            if last_date > start_time:
                next_df = response.get_from_waditu(api_name="daily_basic", ts_code=ts_code, start_date=start_time, end_date=last_date)
                basic_df = basic_df.append(next_df, ignore_index=True)
            basic_df.sort_values(by="trade_date", ascending=True, ignore_index=True, inplace=True)
            location.save_csv(ts_code=ts_code, df=price_df, root=self.root)
            location.save_csv(ts_code=ts_code, df=basic_df, root=self.root, kind="daily/basic/")


class Single:
    """
    @Desc：获取个股数据，包括日线数据，曾用名，每日指标
    @Maybe：各种财务数据
    """

    def __init__(self, ts_code, start_date=datetime.today().strftime("%Y%m%d"), end_date=datetime.today().strftime("%Y%m%d")):
        self.start_date = start_date
        self.end_date = end_date
        self.ts_code = ts_code
        # self.daily_price = self._get_daily_price()
        # self.name_change_list = self._get_name_change_list()
        # self.daily_basic = self._get_daily_basic()

    def get_daily_price(self):
        df = response.get_from_waditu(api_name="daily", ts_code=self.ts_code, start_date=self.start_date, end_date=self.end_date, fields="ts_code,trade_date,open,high,low,close,pre_close,vol,amount")
        last_date = df.iloc[-1, 1]
        if last_date > self.start_date:
            next_df = response.get_from_waditu(api_name="daily", ts_code=self.ts_code, start_date=self.start_date, end_date=last_date, fields="ts_code,trade_date,open,high,low,close,pre_close,vol,amount")
            df = df.append(next_df, ignore_index=True)
        df.sort_values(by="trade_date", ascending=True, ignore_index=True, inplace=True)  # 因为获取到的数据是时间倒序的，所以我们要进行时间的重新排列
        return df

    def get_name_change_list(self):
        df = response.get_from_waditu(api_name="namechange", ts_code=self.ts_code, fields="ts_code,name,start_date,end_date")
        # df["start_date"] = pd.to_datetime(df["start_date"])
        df.sort_values(by=["start_date"], inplace=True)
        return df

    def get_daily_basic(self):
        df = response.get_from_waditu(api_name="daily_basic", ts_code=self.ts_code, start_date=self.start_date, end_date=self.end_date)
        last_date = df.iloc[-1, 1]
        if last_date > self.start_date:
            next_df = response.get_from_waditu(api_name="daily_basic", ts_code=self.ts_code, start_date=self.start_date, end_date=last_date)
            df = df.append(next_df, ignore_index=True)
        df.sort_values(by="trade_date", ascending=True, ignore_index=True, inplace=True)  # 因为获取到的数据是时间倒序的，所以我们要进行时间的重新排列
        return df

    def get_recent_price(self, start_date_, end_date_):
        df = response.get_from_waditu(api_name="daily", ts_code=self.ts_code, start_date=start_date_, end_date=end_date_, fields="ts_code,trade_date,open,high,low,close,pre_close,vol,amount")
        df.sort_values(by="trade_date", ascending=True, ignore_index=True, inplace=True)
        return df

    def get_recent_basic(self):
        df = response.get_from_waditu(api_name="daily_basic", ts_code=self.ts_code, start_date=self.start_date, end_date=self.end_date)
        return df


class Indicators:
    """
    @ 从本地获取基础数据数据，根据基础数据获得所需形状的数据，计算adj等
    """

    def __init__(self, df: pandas.DataFrame):
        self.df = df
        self.adj_price = self._calc_adj_data()

    def _calc_adj_data(self):
        """
        计算复权价，复权因子
        :return:含有前复权、后复权“开高低收”，复权因子，涨跌幅的df
        """
        df = self.df
        df["pct_change"] = df["close"] / df["pre_close"] - 1
        df["adj_factor"] = (1 + df["pct_change"]).cumprod()
        df["hfq_close"] = df["adj_factor"] * (df.iloc[0]["close"] / df.iloc[0]["adj_factor"])
        df["qfq_close"] = df["adj_factor"] * (df.iloc[-1]["close"] / df.iloc[-1]["adj_factor"])
        # 复权收盘价 / 复权开盘价 = 收盘价 / 开盘价
        df["qfq_open"] = df["open"] / df["close"] * df["qfq_close"]
        df["qfq_high"] = df["high"] / df["high"] * df["qfq_close"]
        df["qfq_low"] = df["low"] / df["low"] * df["qfq_close"]
        # 同理可以计算后复权
        df["hfq_open"] = df["open"] / df["close"] * df["hfq_close"]
        df["hfq_high"] = df["high"] / df["high"] * df["hfq_close"]
        df["hfq_low"] = df["low"] / df["low"] * df["hfq_close"]
        return df

    def pct_change(self, adj="hfq_", feature="close"):
        assert self.adj_price is not None, "必须使用复权价格计算"
        vector = adj + feature
        vector_pct = vector + "_pct"
        self.adj_price[vector_pct] = self.adj_price[vector] / self.adj_price[vector].shift() - 1
        return self.adj_price


class OneDailyData:
    """
    获取某天的daily和basic基础数据，调用svae2csv()方法存到本地
    默认设置的交易日期为当日交易日期
    """

    def __init__(self, trade_date=datetime.today().strftime("%Y%m%d")):
        self.trade_date = trade_date
        self.one_daily_stock_price = response.get_from_waditu("daily", trade_date=trade_date, fields="ts_code,trade_date,open,high,low,close,pre_close,vol,amount")
        self.one_daily_stock_basic = response.get_from_waditu("daily_basic", trade_date=trade_date)

    def save2csv(self, root):
        count = 0
        for idx in self.one_daily_stock_price.index:
            cur_price_df = self.one_daily_stock_price.iloc[idx:idx + 1, :]
            cur_basic_df = self.one_daily_stock_basic.iloc[idx:idx + 1, :]
            cur_code = cur_price_df.iloc[0]["ts_code"]
            location.save_csv(ts_code=cur_code, df=cur_price_df, root=root)
            location.save_csv(ts_code=cur_code, df=cur_basic_df, root=root, kind="daily/basic/")
            print("%s已存入" % cur_code)
            count += 1
        print(self.trade_date, str(count), "已存入完毕")


class RecentData:
    def __init__(self, start_date, end_date=datetime.today().strftime("%Y%m%d")):
        self.start_date = start_date
        self.end_date = end_date
        stock_basic_df = response.get_from_waditu(api_name="stock_basic", fields="ts_code,name")
        self.ts_code_list = list(stock_basic_df["ts_code"])

    def _get_recent_price(self, ts_code):
        df = response.get_from_waditu("daily", ts_code=ts_code, start_date=self.start_date, end_date=self.end_date, fields="ts_code,trade_date,open,high,low,close,pre_close,vol,amount")
        df.sort_values(by="trade_date", ascending=True, ignore_index=True, inplace=True)
        return df

    def _get_recent_basic(self, ts_code):
        df = response.get_from_waditu("daily_basic", ts_code=ts_code, start_date=self.start_date, end_date=self.end_date)
        df.sort_values(by="trade_date", ascending=True, ignore_index=True, inplace=True)
        return df

    def save2csv(self, root):
        count = 0
        for ts_code in self.ts_code_list[:20]:
            price_df = self._get_recent_price(ts_code=ts_code)
            basic_df = self._get_recent_basic(ts_code=ts_code)
            location.save_csv(ts_code=ts_code, df=price_df, root=root)
            location.save_csv(ts_code=ts_code, df=basic_df, root=root, kind="daily/basic/")
            count += 1
        print(str(count), "已存入完毕")
