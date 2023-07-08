import exchange_calendars as ecals
import pandas as pd
from datetime import datetime

# 한국 개장일자
XKRX = ecals.get_calendar("XKRX")


def get_list_mkt_date(date_start, date_end):

    list_date = pd.date_range(date_start, date_end)
    list_date = sorted(set(list_date) & set(XKRX.schedule.index))

    return list_date

def get_list_eom_date(list_date):

    '''
    list_date 기준 EOM date 반환
    :param list_date:
    :return:
    '''

    list_date_eom = []  # 월말

    year = 0
    month = list_date[0].month
    days = 0

    for p_date in list_date:

        if p_date.month != month:
            list_date_eom.append(datetime(year, month, days))

        year = p_date.year
        month = p_date.month
        days = p_date.day

    return list_date_eom

def change_date_to_mkt_date(list_date):

    '''
    DataFrame의 'date' 칼럼의 값을 마켓 일자로 변경
    '''

    list_date = list(map(lambda x : str(x), list_date))

    list_mkt_date = XKRX.schedule.index.astype("str")
    list_date = list(map(lambda x : sorted([mkt_date for mkt_date in list_mkt_date if mkt_date <= x])[-1], list_date))
    list_date = list(map(lambda x: pd.to_datetime(x), list_date))

    return list_date
