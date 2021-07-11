#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : location.py
# @Author: Ace
# @Date  : 2021/7/5
# @Contact : gopheriilidan@yeah.net
# @Desc  :

import os

import pandas as pd


def get_location_all_stock_code_list(path: str):
    ts_code_list = []
    for root, dirs, files in os.walk(path):
        if files:
            for f in files:
                if f.endswith('.csv'):
                    ts_code_list.append(f[:8])
    return sorted(ts_code_list)


def save_csv(ts_code, df: pd.DataFrame, root, kind="daily/price/"):
    file_path = "%s%s%s.csv" % (root, kind, ts_code)
    mode = ""
    header = False
    if os.path.exists(file_path):
        mode = "a"
    else:
        mode = "w"
        header = True
    df.to_csv(path_or_buf=file_path, index=False, mode=mode, header=header)
    print("股票：%s已存入到%s" % (ts_code, file_path))
