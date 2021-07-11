#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : elementary.py
# @Author: Ace
# @Date  : 2021/7/3
# @Contact : gopheriilidan@yeah.net
# @Desc  :
import pandas as pd
from util import location
from util import response
from decimal import Decimal, ROUND_HALF_UP


class BasicReduction:
    def __init__(self, price: pd.DataFrame = None, name: pd.DataFrame = None, basic: pd.DataFrame = None):
        assert type(price) is pd.DataFrame and type(name) is pd.DataFrame, "需要合并的两个表格必须是pandas.DataFrame类型"
        price["trade_date"] = pd.to_datetime(price["trade_date"])
        basic["trade_date"] = pd.to_datetime(basic["trade_date"])
        name["start_date"] = pd.to_datetime(name["start_date"])
        name["end_date"] = pd.to_datetime(name["end_date"])
        basic = basic[["trade_date", "total_mv", "circ_mv"]]
        self.price = price
        self.name = name
        self.basic = basic
        self.index_merged = self._merge_price_name_basic_index()

    def _merge_price_name_basic_index(self):
        self.name.iloc[-1, -2]
        self.name.fillna(value=self.name.iloc[-1, -2], inplace=True)
        self.name.drop(labels=["ts_code", "end_date"], axis=1, inplace=True)
        start_date = self.name.iloc[0, -1]
        end_date = self.name.iloc[-1, -1]
        cal = pd.DataFrame(pd.date_range(start=start_date, end=end_date))
        df = pd.merge(left=cal, right=self.name, how="left", left_on=0, right_on="start_date")
        df.fillna(method="ffill", inplace=True)
        df = pd.merge(left=self.price, right=df, how="left", left_on="trade_date", right_on=0)
        df.fillna(method="ffill", inplace=True)
        df.drop(labels=[0, "start_date"], axis=1, inplace=True)
        df = pd.merge(left=df, right=self.basic, how="left", left_on="trade_date", right_on="trade_date")
        # 计算涨停，一字涨停，ST涨停限制
        df["high_limit"] = df["pre_close"] * 1.1
        df.loc[df["name"].str.contains("ST" or "st"), "high_limit"] = df["pre_close"] * 1.05
        # 四舍五入
        df["high_limit"] = df["high_limit"].apply(lambda x: float(Decimal(x * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP) / 100))
        # 判断是否一字涨停
        df["upper_limit"] = False
        df.loc[df["low"] >= df["high_limit"], "upper_limit"] = True
        # 判断是否开盘涨停
        df["open_limit"] = False
        df.loc[df["open"] >= df["high_limit"], "open_limit"] = True
        df["pct_change"] = df["close"] / df["pre_close"] - 1
        df["open_buy_pct_change"] = df["close"] / df["open"] - 1
        index_df = response.get_from_waditu("index_daily", ts_code="000001.SH", start_date="19900101")
        index_df.sort_values(by=["trade_date"], inplace=True, ignore_index=True)
        index_df["trade_date"] = pd.to_datetime(index_df["trade_date"])
        del index_df["change"]
        del index_df["pct_chg"]
        del index_df["vol"]
        del index_df["amount"]
        rename_dic_ = {
            "ts_code": "index_code",
            "close": "index_close",
            "open": "index_open",
            "high": "index_high",
            "low": "index_low",
            "pre_close": "index_pre_close",
        }
        index_df.rename(columns=rename_dic_, inplace=True)
        # return index_df
        df = pd.merge(left=df, right=index_df, on="trade_date", how="right", sort=True, indicator=True)
        df["close"].fillna(method='ffill', inplace=True)
        df["open"].fillna(value=df["close"], inplace=True)
        df["high"].fillna(value=df["close"], inplace=True)
        df["low"].fillna(value=df["close"], inplace=True)
        df["pre_close"].fillna(value=df["close"].shift(), inplace=True)
        fill_0_list = ["vol", "amount", "pct_change", "open_buy_pct_change"]
        df.loc[:, fill_0_list] = df[fill_0_list].fillna(value=0)
        df.fillna(method='ffill', inplace=True)
        df = df[df["ts_code"].notnull()]
        df["traded"] = 1
        df.loc[df["_merge"] == "right_only", "traded"] = 0
        del df["_merge"]
        df.reset_index(drop=True, inplace=True)
        df["next_trade"] = df["traded"].shift(-1)
        df["next_upper_limit"] = df["upper_limit"].shift(-1)
        df["next_open_limit"] = df["open_limit"].shift(-1)
        df["next_name_st"] = df["name"].str.contains('ST').shift(-1)
        df["next_out"] = df["name"].str.contains("退").shift(-1)
        df["next_open_buy_pct_change"] = df["open_buy_pct_change"].shift(-1)
        return df
