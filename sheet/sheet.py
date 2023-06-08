from abc import *
import pandas as pd

class SheetBalance:

    def __init__(self, ex_date, tr_date, asset_total):

        self.ex_date = ex_date
        self.tr_date = tr_date

        asset_cash = asset_total
        asset_invest = 0

        self.df_sht = pd.DataFrame({
            "date": [ex_date]
            , "asset_total": [asset_total]
            , "asset_invest": [asset_invest]
            , "asset_cash": [asset_cash]
        })

        self.df_ex = pd.DataFrame()
        self.df_tr = pd.DataFrame()

    def update_date(self, tr_date):
        self.ex_date = self.tr_date  # 이전 일자 갱신
        self.tr_date = tr_date  # 현재 일자 갱신

    def duplicate_ex(self):
        # 전일자 book 복제
        df_ex = self.df_sht[self.df_sht["date"] == self.ex_date]
        df_ex.loc[:, "date"] = self.tr_date
        self.df_sht = pd.concat([self.df_sht, df_ex]).reset_index(drop=True)

    def evaluate_asset(self, df_book):
        if len(df_book) > 0:
            invest_asset = df_book["eval_asset"].sum()
            self.df_sht.loc[self.df_sht["date"] == self.tr_date, "asset_invest"] = invest_asset
            self.df_sht.loc[self.df_sht["date"] == self.tr_date, "asset_total"] = self.df_sht.loc[self.df_sht[
                                                                                                      "date"] == self.tr_date, "asset_invest"] + \
                                                                                  self.df_sht.loc[self.df_sht[
                                                                                                      "date"] == self.tr_date, "asset_cash"]
    def sell(self, asset):
        # sell 한 asset 만큼 cash 증가 & invest 차감
        self.df_sht.loc[self.df_sht["date"] == self.tr_date, "asset_cash"] += asset
        self.df_sht.loc[self.df_sht["date"] == self.tr_date, "asset_invest"] -= asset

        self.df_sht.loc[self.df_sht["date"] == self.tr_date, "asset_total"] = self.df_sht.loc[self.df_sht[
                                                                                                  "date"] == self.tr_date, "asset_cash"] + \
                                                                              self.df_sht.loc[self.df_sht[
                                                                                                  "date"] == self.tr_date, "asset_invest"]

    def buy(self, asset):
        # buy 한 asset 만큼 cash 차감 & invest 증가
        self.df_sht.loc[self.df_sht["date"] == self.tr_date, "asset_cash"] -= asset
        self.df_sht.loc[self.df_sht["date"] == self.tr_date, "asset_invest"] += asset

        self.df_sht.loc[self.df_sht["date"] == self.tr_date, "asset_total"] = self.df_sht.loc[self.df_sht[
                                                                                                  "date"] == self.tr_date, "asset_cash"] + \
                                                                              self.df_sht.loc[self.df_sht[
                                                                                                  "date"] == self.tr_date, "asset_invest"]


class SheetBook:

    def __init__(self, ex_date, tr_date):

        self.df_sht = pd.DataFrame(
            columns=["date", "item_cd", "book_amt", "book_price", "book_asset", "eval_price", "eval_asset", "pl_chg",
                     "pl_chg_pct"])
        self.ex_date = ex_date
        self.tr_date = tr_date

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

        # 기보유 자산 평균 재연산
        cnt = len(self.df_sht.loc[(self.df_sht["date"] == self.tr_date) &
                                  (self.df_sht["item_cd"] == item_cd) &
                                  (self.df_sht["book_amt"] != 0)]
                  )

        if cnt > 0:
            df = self.df_sht.loc[(self.df_sht["date"] == self.tr_date) & (self.df_sht["item_cd"] == item_cd)]

            asset += df["book_asset"].values[0]
            amt += df["book_amt"].values[0]
            price = asset / amt  # 평균단가 재연산

        pl_chg = 0  # 이후 평가때 재연산
        pl_chg_pct = 0  # 이후 평가때 재연산

        df_buy_asset = pd.DataFrame([[p_date, item_cd, amt, price, asset, price, asset, pl_chg, pl_chg_pct]]
                                    , columns=["date", "item_cd", "book_amt", "book_price", "book_asset", "eval_price",
                                               "eval_asset", "pl_chg", "pl_chg_pct"])

        self.df_sht = pd.concat([self.df_sht, df_buy_asset]).reset_index(drop=True)

    def duplicate_ex(self):

        # 전일자 book 복제
        df_book_ex = self.df_sht[self.df_sht["date"] == self.ex_date]
        df_book_ex = df_book_ex[df_book_ex["book_amt"] > 0]  # 잔고가 있는것만 경신
        df_book_ex.loc[:, "date"] = self.tr_date
        self.df_sht = pd.concat([self.df_sht, df_book_ex]).reset_index(drop=True)

    def evaluate_asset(self, asset_price):

        # 금일자 평가자산 업데이트
        df_tr = self.df_sht[self.df_sht["date"] == self.tr_date]
        for i, rows in df_tr.iterrows():

            item_cd = rows["item_cd"]
            amt = rows["book_amt"]

            price = asset_price.get_price_by_item_cd(item_cd)
            asset = amt * price

            self.df_sht.loc[i, "eval_price"] = price
            self.df_sht.loc[i, "eval_asset"] = asset

            self.df_sht.loc[i, "pl_chg"] = self.df_sht.loc[i, "eval_asset"] - self.df_sht.loc[i, "book_asset"]
            self.df_sht.loc[i, "pl_chg_pct"] = self.df_sht.loc[i, "eval_price"] / self.df_sht.loc[i, "eval_price"]

    def update_date(self, tr_date):

        self.ex_date = self.tr_date  # 이전 일자 갱신
        self.tr_date = tr_date  # 현재 일자 갱신

    def get_book(self):

        df = self.df_sht[self.df_sht["date"] == self.tr_date]

        return df


class SheetTrade:

    def __init__(self, ex_date, tr_date):
        self.df_sht = pd.DataFrame(columns=["date", "item_cd", "buy_sell", "amt", "price", "asset"])
        self.ex_date = ex_date
        self.tr_date = tr_date

    def sell(self, p_date, item_cd, amt, price, asset):
        buy_sell = -1
        df_trade = pd.DataFrame([[p_date, item_cd, buy_sell, amt, price, asset]]
                                , columns=["date", "item_cd", "buy_sell", "amt", "price", "asset"])

        self.df_sht = pd.concat([self.df_sht, df_trade]).reset_index(drop=True)

    def buy(self, p_date, item_cd, amt, price, asset):
        buy_sell = 1
        df_trade = pd.DataFrame([[p_date, item_cd, buy_sell, amt, price, asset]]
                                , columns=["date", "item_cd", "buy_sell", "amt", "price", "asset"])

        self.df_sht = pd.concat([self.df_sht, df_trade]).reset_index(drop=True)
