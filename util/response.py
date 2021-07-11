#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : response.py
# @Author: Ace
# @Date  : 2021/7/5
# @Contact : gopheriilidan@yeah.net
# @Desc  :

from acquire.config import api
import time


def get_from_waditu(api_name, fields: str = '', **kwargs):
    """
    防断网保护
    :param api_name:
    :param fields:
    :param kwargs:
    :return:
    """
    max_try = 15
    sleep_time = 30
    suc = False
    for i in range(max_try):
        try:
            df = api.query(api_name=api_name, fields=fields, **kwargs)
            suc = True
            break
        except Exception as e:
            print("第%d次数据获取失败，报错内容：%s" % (i, e))
            time.sleep(sleep_time)
    if suc:
        return df
    else:
        raise ValueError("从waditu获取失败，尝试次数已达到上限，请尽快解决")
