import pickle
import pandas as pd


class AssetPrice:

    def __init__(self, p_date):

        with open(r"D:\MyProject\StockPrice\DictDfStock.pickle", 'rb') as fr:
            self.dict_df_stock = pickle.load(fr)

        with open(r"D:\MyProject\StockPrice\DictDfStockDaily.pickle", 'rb') as fr:
            self.dict_df_stock_daily = pickle.load(fr)

        self.df_stock_daily = pd.DataFrame()
        self.std_date = p_date

    def set_stock_daily(self, p_date):

        self.df_stock_daily = self.dict_df_stock_daily[p_date]

    def get_price_by_item_cd(self, item_cd):

        df = self.df_stock_daily.loc[self.df_stock_daily["StockCode"] == item_cd]

        if len(df) == 0:
            df = self.dict_df_stock[item_cd].loc[:self.std_date]
            fixed_date = df.index[-1]
            price = df.iloc[-1]["Close"]
            # print(self.std_date, item_cd, "SellNoPrice", fixed_date)
        else:
            price = df["Close"].values[0]

        return price