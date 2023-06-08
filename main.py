from sheet import SheetTrade, SheetBalance, SheetBook
from price import AssetPrice
from tqdm import tqdm
import pandas as pd
import pickle
from datetime import datetime
import math
from lib import numeric_pack

import warnings
warnings.filterwarnings('ignore')

# 월별 전략 스케줄 생성
with open(r'D:\MyProject\FactorSelection\monthly_invest_strategy.pickle', 'rb') as fr:
    monthly_invest_strategy = pickle.load(fr)


list_date = numeric_pack.get_list_mkt_date(datetime(2019,1,1), datetime(2023,5,1))

invest_schedule = monthly_invest_strategy["stock"]["value"]["por"]
invest_schedule = invest_schedule[invest_schedule["w_type"] == "equal"]
invest_schedule = numeric_pack.change_date_to_mkt_date(invest_schedule)

# 시작일자 및 시작 현금 초기화
date_start = list_date[0]
asset_start = 10000 * 10000

# 장부 초기화 (자산, 북, 거래)
sheet_balance = SheetBalance(date_start, date_start, asset_start)
sheet_book = SheetBook(date_start, date_start)
sheet_trade = SheetTrade(date_start, date_start)

# 가격 호출 클래스 초기화
asset_price = AssetPrice(date_start)

# 리밸런싱 일자
list_rebal_date = invest_schedule["date"].unique()

# 리밸런싱 일자에 보유 자산 전부 매도 여부
is_rebal_reset = True

# 백테스트 실행
for p_date in tqdm(pd.to_datetime(list_rebal_date)):

    # 일자 업데이트
    sheet_balance.update_date(p_date)
    sheet_book.update_date(p_date)

    asset_price.set_stock_daily(p_date)

    # 전일자 Book 복제
    sheet_book.duplicate_ex()
    sheet_balance.duplicate_ex()

    # 자산 평가
    sheet_book.evaluate_asset(asset_price)
    sheet_balance.evaluate_asset(sheet_book.get_book())

    # 리밸런싱 강제 청산 유무
    if is_rebal_reset:

        # sell
        if p_date in list_rebal_date:

            df_sell = sheet_book.get_book()[["date", "item_cd", "book_amt"]]

            for i, rows in df_sell.iterrows():

                item_cd = rows["item_cd"]
                amt = rows["book_amt"]

                price = asset_price.get_price_by_item_cd(item_cd)
                asset = amt * price

                sheet_trade.sell(p_date, item_cd, amt, price, asset)
                sheet_book.sell(i, amt)
                sheet_balance.sell(asset)

        # buy
        if p_date in list_rebal_date:

            df_inv_sch = invest_schedule[invest_schedule["date"] == p_date]
            for i, rows in df_inv_sch.iterrows():

                p_date = rows["date"]
                item_cd = rows["item_cd"]
                weight = rows["weight"]

                total_asset = sheet_balance.df_sht.iloc[-1]["asset_total"]
                asset = math.floor(total_asset * weight)  # 투자할 자산

                price = asset_price.get_price_by_item_cd(item_cd)
                amt = math.floor(asset / price)
                asset = price * amt

                sheet_trade.buy(p_date, item_cd, amt, price, asset)
                sheet_book.buy(p_date, item_cd, amt, price, asset)
                sheet_balance.buy(asset)

    else:
        pass

# save data
with open(r'D:\MyProject\FactorSelection\sheet_balance.pickle', 'wb') as fw:
    pickle.dump(sheet_balance.df_sht, fw)

# save data
with open(r'D:\MyProject\FactorSelection\sheet_book.pickle', 'wb') as fw:
    pickle.dump(sheet_book.df_sht, fw)

# save data
with open(r'D:\MyProject\FactorSelection\sheet_trade.pickle', 'wb') as fw:
    pickle.dump(sheet_trade.df_sht, fw)