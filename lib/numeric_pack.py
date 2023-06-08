import exchange_calendars as ecals
import pandas as pd

# 한국 개장일자
XKRX = ecals.get_calendar("XKRX")


def get_list_mkt_date(date_start, date_end):

    list_date = pd.date_range(date_start, date_end)
    list_date = sorted(set(list_date) & set(XKRX.schedule.index))

    return list_date

def change_date_to_mkt_date(df):

    '''
    DataFrame의 'date' 칼럼의 값을 마켓 일자로 변경
    '''

    df["date"] = df["date"].astype("str")

    list_mkt_date = XKRX.schedule.index.astype("str")
    df["date"] = df["date"].apply(lambda x : sorted([mkt_date for mkt_date in list_mkt_date if mkt_date <= x])[-1])
    df["date"] = pd.to_datetime(df["date"])

    return df
