import pickle
import pandas as pd
from tqdm import tqdm


class AssetPrice:

    def __init__(self, p_date):

        with open(r"D:\MyProject\StockPrice\DictDfStock.pickle", 'rb') as fr:
            self.dict_df_stock = pickle.load(fr)

        with open(r"D:\MyProject\StockPrice\DictDfStockDaily.pickle", 'rb') as fr:
            self.dict_df_stock_daily = pickle.load(fr)

        self.df_stock_daily = pd.DataFrame()
        self.std_date = p_date
        self.dict_sch_price = {} # 가격 hash_table

    def set_dict_sch_price(self, invest_schedule):
        '''
        스케줄링된 종목군들의 가격 HashTable 생성
        :param invest_schedule:
        :return:
        '''

        list_item_cd = invest_schedule["item_cd"].unique()
        list_date = pd.to_datetime(invest_schedule["date"].unique())

        for item_cd in tqdm(list_item_cd):

            if (item_cd in self.dict_sch_price.keys()) == False:
                self.dict_sch_price[item_cd] = {}

            for p_date in list_date:
                try:
                    self.dict_sch_price[item_cd][p_date] = self.dict_df_stock[item_cd].loc[p_date, "Close"]
                except:
                    continue

    def set_stock_daily(self, p_date):

        # self.df_stock_daily = self.dict_df_stock_daily[p_date]
        self.std_date = p_date

    def get_price_by_item_cd(self, item_cd):

        price = self.dict_sch_price[item_cd][self.std_date]
        #
        # df = self.df_stock_daily.loc[self.df_stock_daily["StockCode"] == item_cd]
        #
        # if len(df) == 0:
        #     df = self.dict_df_stock[item_cd].loc[:self.std_date]
        #     fixed_date = df.index[-1]
        #     price = df.iloc[-1]["Close"]
        #     # print(self.std_date, item_cd, "SellNoPrice", fixed_date)
        # else:
        #     price = df["Close"].values[0]

        return price