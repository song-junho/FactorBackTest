from sheet import SheetTrade, SheetBalance, SheetBook, save_sheet
from price import AssetPrice
from tqdm import tqdm
import pandas as pd
import pickle
from datetime import datetime
import math
from lib import numeric_pack, utils
from functools import reduce

import warnings
warnings.filterwarnings('ignore')

# 월별 전략 스케줄 생성
with open(r'D:\MyProject\FactorSelection\monthly_invest_strategy.pickle', 'rb') as fr:
    monthly_invest_strategy = pickle.load(fr)

# 전략 선택 및 조합
set_strategy = [

    {
        "asset" : "stock"
        , "factor" : "value"
        , "detaiL_factor" : "por_spr"
        , "w_type" : "equal"
    }
    , {
        "asset" : "stock"
        , "factor" : "size"
        , "detaiL_factor" : "small_cap"
        , "w_type" : "equal"
    }
    , {
        "asset" : "stock"
        , "factor" : "theme"
        , "detaiL_factor" : "3M"
        , "w_type" : "equal"
    }
]
list_strategy = []

# 전략
strategy_nm = ""
for strategy in set_strategy:

    asset = strategy["asset"]
    factor = strategy["factor"]
    detaiL_factor = strategy["detaiL_factor"]
    w_type = strategy["w_type"]

    invest_schedule = monthly_invest_strategy[asset][factor][detaiL_factor]
    invest_schedule = invest_schedule[invest_schedule["w_type"] == w_type]
    list_strategy.append(invest_schedule)
    strategy_nm += asset+"_"+factor+"("+detaiL_factor + ")" + "__"
strategy_nm = strategy_nm[:-2]

# 전략 병합
invest_schedule = reduce(lambda left, right : pd.merge(left, right[["date", "item_cd"]], on=["date","item_cd"], how="inner"), list_strategy)

df_grp_count = invest_schedule.groupby("date").agg({"item_cd": "count"}).rename(columns={"item_cd": "count"}).reset_index()
invest_schedule["weight"] = 0
invest_schedule["weight"] = invest_schedule["date"].apply(lambda x: df_grp_count.loc[df_grp_count["date"] == x, "count"].values[0])
invest_schedule["weight"] = 1 / invest_schedule["weight"]

# 마켓일자로 변경
invest_schedule["date"] = numeric_pack.change_date_to_mkt_date(invest_schedule["date"])

# weight 소수점 내림
# invest_schedule["weight"] = invest_schedule["weight"]*(10**5)
# invest_schedule["weight"] = invest_schedule["weight"].astype('float').round(0) / (10**5)


# 리밸런싱 일자
start_date = datetime(2006, 1, 1)
end_date = datetime(2023, 7, 1)
list_date = pd.date_range(start_date, end_date)
list_date = numeric_pack.get_list_eom_date(list_date)
list_date = numeric_pack.change_date_to_mkt_date(list_date)

list_rebal_date = list_date

# 시작일자 및 시작 현금 초기화
date_start = list_date[0]
asset_start = 10000 * 10000

# 저장 폴더명
dir_nm = r'D:\MyProject\FactorSelection\backtest\{}'.format(strategy_nm)
utils.create_folder(dir_nm)


if __name__ == "__main__":

    # 장부 초기화 (자산, 북, 거래)
    sheet_balance = SheetBalance(asset_start, date_start, date_start)
    sheet_book = SheetBook(date_start, date_start)
    sheet_trade = SheetTrade(date_start, date_start)

    # 가격 호출 클래스 초기화
    asset_price = AssetPrice(date_start)
    asset_price.set_dict_sch_price(invest_schedule)

    # 리밸런싱 일자
    # list_rebal_date = invest_schedule["date"].unique()

    # 리밸런싱 일자에 보유 자산 전부 매도 여부
    is_rebal_reset = True

    # 백테스트 실행
    for p_date in tqdm(pd.to_datetime(list_rebal_date)):

        # 일자 업데이트
        sheet_balance.update_date(p_date)
        sheet_book.update_date(p_date)

        asset_price.set_date(p_date)

        # 거래 첫날은 제외
        if p_date != date_start:

            # 전일자 Book 복제
            sheet_book.duplicate_ex()
            sheet_balance.duplicate_ex()

            # 현일자 데이터 세팅
            sheet_book.set_tr()

            # 자산 평가
            sheet_book.evaluate_asset(asset_price)
            sheet_balance.evaluate_asset(sheet_book.get_book())

        # 현일자 데이터 세팅
        sheet_book.set_tr()

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

                sheet_trade.update_sht()
                sheet_book.update_sht()

            # buy
            if p_date in list_rebal_date:

                df_inv_sch = invest_schedule[invest_schedule["date"] == p_date]
                sheet_book.set_tr()  # 현일자 데이터 세팅

                # 매수 종목이 너무 적은 경우 pass
                if len(df_inv_sch) < 5:
                    pass
                else:
                    for i, rows in df_inv_sch.iterrows():

                        p_date = rows["date"]
                        item_cd = rows["item_cd"]
                        weight = rows["weight"]

                        total_asset = sheet_balance.df_sht.iloc[-1]["asset_total"]
                        asset = math.floor(total_asset * weight)  # 투자할 자산

                        price = asset_price.get_price_by_item_cd(item_cd)
                        if price == 0: # 비상장
                            continue
                        amt = math.floor(asset / price)
                        asset = price * amt

                        sheet_trade.buy(p_date, item_cd, amt, price, asset)
                        sheet_book.buy(p_date, item_cd, amt, price, asset)
                        sheet_balance.buy(asset)

                sheet_trade.update_sht()
                sheet_book.update_sht()

        else:
            pass

    save_sheet(dir_nm, sheet_balance.df_sht, sheet_book.df_sht, sheet_trade.df_sht)
