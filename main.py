# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import time

from acquire import stock
from datetime import datetime


def get_all_stock_history_data():
    root = "./data_store/"
    code_start_dic = stock.BasicInfo().code2start
    today_str = datetime.today().strftime("%Y%m%d")
    for ts_code, start_date in code_start_dic.items():
        cur_stock = stock.Single(ts_code=ts_code, start_date=start_date, end_date=today_str)
        cur_stock.save_daily_2_location(root=root)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    get_all_stock_history_data()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
