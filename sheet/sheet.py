from abc import *
import pandas as pd
from collections import deque
import pickle


def save_sheet(dir_nm, df_balance, df_book, df_trade):
    '''
    sheet 저장
    '''
    # save data
    with open(dir_nm + '\sheet_balance.pickle', 'wb') as fw:
        pickle.dump(df_balance, fw)

    # save data
    with open(dir_nm + '\sheet_book.pickle', 'wb') as fw:
        pickle.dump(df_book, fw)

    # save data
    with open(dir_nm + '\sheet_trade.pickle', 'wb') as fw:
        pickle.dump(df_trade, fw)


class Sheet(metaclass=ABCMeta):

    def __init__(self, *args):

        self.ex_date = args[0]
        self.tr_date = args[1]
        self.df_sht = pd.DataFrame()
        self.update_list = deque([])

    @abstractmethod
    def sell(self, *args):
        pass

    @abstractmethod
    def buy(self, *args):
        pass

    def update_date(self, tr_date):
        self.ex_date = self.tr_date  # 이전 일자 갱신
        self.tr_date = tr_date  # 현재 일자 갱신

    def update_sht(self):

        self.update_list.appendleft(self.df_sht)
        self.df_sht = pd.concat(self.update_list).reset_index(drop=True)
        self.update_list = deque([])


class SheetBalance(Sheet):

    def __init__(self, asset_total, *args):

        super().__init__(*args)

        asset_cash = asset_total
        asset_invest = 0

        self.df_sht = pd.DataFrame({
            "date": [self.ex_date]
            , "asset_total": [asset_total]
            , "asset_invest": [asset_invest]
            , "asset_cash": [asset_cash]
        })

        self.df_ex = pd.DataFrame()
        self.df_tr = pd.DataFrame()

    def duplicate_ex(self):
        # 전일자 book 복제
        df_ex = self.df_sht[self.df_sht["date"] == self.ex_date]
        df_ex.loc[:, "date"] = self.tr_date
        self.df_sht = pd.concat([self.df_sht, df_ex]).reset_index(drop=True)

    def evaluate_asset(self, df_book):

        if len(df_book) > 0:
            last_index = self.df_sht.index[-1]
            invest_asset = df_book["eval_asset"].sum()
            self.df_sht.loc[last_index, "asset_invest"] = invest_asset
            self.df_sht.loc[last_index, "asset_total"] = self.df_sht.loc[last_index, "asset_invest"] + self.df_sht.loc[last_index, "asset_cash"]

    def sell(self, asset):
        # sell 한 asset 만큼 cash 증가 & invest 차감
        last_index = self.df_sht.index[-1]
        self.df_sht.loc[last_index, "asset_cash"] += asset
        self.df_sht.loc[last_index, "asset_invest"] -= asset
        self.df_sht.loc[last_index, "asset_total"] = self.df_sht.loc[last_index, "asset_cash"] + self.df_sht.loc[last_index, "asset_invest"]

    def buy(self, asset):
        # buy 한 asset 만큼 cash 차감 & invest 증가
        last_index = self.df_sht.index[-1]
        self.df_sht.loc[last_index, "asset_cash"] -= asset
        self.df_sht.loc[last_index, "asset_invest"] += asset
        self.df_sht.loc[last_index, "asset_total"] = self.df_sht.loc[last_index, "asset_cash"] + self.df_sht.loc[last_index, "asset_invest"]


class SheetBook(Sheet):

    def __init__(self, *args):

        super().__init__(*args)
        self.df_sht = pd.DataFrame(
            columns=["date", "item_cd", "book_amt", "book_price", "book_asset", "eval_price", "eval_asset", "pl_chg",
                     "pl_chg_pct"])

        self.df_tr = pd.DataFrame()

        self.update_list = deque([])

    def set_tr(self):

        self.df_tr = self.df_sht[self.df_sht["date"] == self.tr_date]

    def sell(self, p_index, amt):

        self.df_sht.loc[p_index, "book_amt"] -= amt
        self.df_sht.loc[p_index, "book_asset"] = self.df_sht.loc[p_index, "book_amt"] * self.df_sht.loc[
            p_index, "book_price"]
        self.df_sht.loc[p_index, "eval_asset"] = self.df_sht.loc[p_index, "book_amt"] * self.df_sht.loc[
            p_index, "eval_price"]

        if self.df_sht.loc[p_index, "book_amt"] == 0:

            self.df_sht.loc[p_index, "pl_chg"] = 0
            self.df_sht.loc[p_index, "pl_chg_pct"] = 0
        else:
            self.df_sht.loc[p_index, "pl_chg"] = self.df_sht.loc[p_index, "eval_asset"] - self.df_sht.loc[
                p_index, "book_asset"]
            self.df_sht.loc[p_index, "pl_chg_pct"] = self.df_sht.loc[p_index, "eval_asset"] / self.df_sht.loc[
                p_index, "book_asset"]

    def buy(self, p_date, item_cd, amt, price, asset):

        df = self.df_tr[(self.df_tr["item_cd"] == item_cd) &
                        (self.df_tr["book_amt"] != 0)]

        if len(df) > 0:
            asset += df["book_asset"].values[0]
            amt += df["book_amt"].values[0]
            price = asset / amt  # 평균단가 재연산

        pl_chg = 0  # 이후 평가때 재연산
        pl_chg_pct = 0  # 이후 평가때 재연산

        df = pd.DataFrame([[p_date, item_cd, amt, price, asset, price, asset, pl_chg, pl_chg_pct]]
                          , columns=["date", "item_cd", "book_amt", "book_price", "book_asset", "eval_price",
                                     "eval_asset", "pl_chg", "pl_chg_pct"])

        self.update_list.append(df)

    def duplicate_ex(self):

        # 전일자 book 복제
        df_book_ex = self.df_sht[self.df_sht["date"] == self.ex_date]
        df_book_ex = df_book_ex[df_book_ex["book_amt"] > 0]  # 잔고가 있는것만 경신
        df_book_ex.loc[:, "date"] = self.tr_date
        self.df_sht = pd.concat([self.df_sht, df_book_ex]).reset_index(drop=True)

        self.df_sht["book_asset"] = self.df_sht["book_asset"].astype("int64")
        self.df_sht["eval_asset"] = self.df_sht["eval_asset"].astype("int64")

    def evaluate_asset(self, asset_price):

        # 금일자 평가자산 업데이트
        df_tr = self.df_tr
        for i, rows in df_tr.iterrows():

            item_cd = rows["item_cd"]
            amt = rows["book_amt"]

            price = asset_price.get_price_by_item_cd(item_cd)
            asset = amt * price

            self.df_sht.loc[i, "eval_price"] = price
            self.df_sht.loc[i, "eval_asset"] = asset

            self.df_sht.loc[i, "pl_chg"] = self.df_sht.loc[i, "eval_asset"] - self.df_sht.loc[i, "book_asset"]
            self.df_sht.loc[i, "pl_chg_pct"] = self.df_sht.loc[i, "eval_price"] / self.df_sht.loc[i, "eval_price"]

    def get_book(self):

        return self.df_sht[self.df_sht["date"] == self.tr_date]


class SheetTrade(Sheet):

    def __init__(self, *args):
        super().__init__(*args)

        self.df_sht = pd.DataFrame(columns=["date", "item_cd", "buy_sell", "amt", "price", "asset"])
        self.update_list = deque([])

    def sell(self, p_date, item_cd, amt, price, asset):

        buy_sell = -1
        df = pd.DataFrame([[p_date, item_cd, buy_sell, amt, price, asset]]
                          , columns=["date", "item_cd", "buy_sell", "amt", "price", "asset"])

        self.update_list.append(df)

    def buy(self, p_date, item_cd, amt, price, asset):

        buy_sell = 1
        df = pd.DataFrame([[p_date, item_cd, buy_sell, amt, price, asset]]
                          , columns=["date", "item_cd", "buy_sell", "amt", "price", "asset"])

        self.update_list.append(df)
