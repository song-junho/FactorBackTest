# FactorBackTest
> InvestStrategy 의 output인 투자스케줄을 기반으로 백테스트 진행  
> Output: sheet_balance(자산) , sheet_book(북) , sheet_trade(거래)

1. sheet_balance
   * 월별 전체 자산 , 투자 자산 , 현금 자산 기록
2. sheet_book
   * 월별 보유 자산 현황
3. sheet_trade
   * 거래 기록 

# OutPut Sample
 * item_type
   * 의미: 자산 타입 
   * 종류: stock, bond, commodity  
 * w_type
   * 의미: weight 기준
   * 종류: equal, market_cap, z_score  
 * weight
   * 의미: 투자비중
### 1. sheet_balance(자산)
 * asset_total
   * 의미: 전체 자산
 * asset_invest
   * 의미: 투자 자산
 * asset_cash
   * 의미: 현금 자산 

|date|	asset_total|	asset_invest|	asset_cash|
|---|---|---|---|
|2006-01-31|	100000000|	 96697016|	3302984|
|2006-02-28|	100276187|	 97207630|	3068557|
|2006-03-31|	 99650413|   93413341|	6237072|
|2006-04-28|	104736920|	 98011142|	6725778|
|2006-05-30|	 95725131|   89900472|	5824659|
|2006-06-30|	 91920421|   86252915|	5667506|
|2006-07-31|	 90214614|   84486797|	5727817|
|2006-08-31|	 95806329|   87973814|	7832515|
|2006-09-29|	 99596034|   91736750|	7859284|
|2006-10-31|	100913967|	 92365407|	8548560|
|2006-11-30|	110651208|	104426238|	6224970|
|2006-12-28|	109516560|	103152201|	6364359|

### 2. sheet_book(북)

 * item_cd
   * 의미: 자산 코드
 * book_amt
   * 의미: 매수 수량
 * book_price
   * 의미: 매수 평균 단가 
 * book_asset
   * 의미: 매수 금액  
 * eval_price
   * 의미: 매수 평균 단가 
 * eval_asset
   * 의미: 매수 금액  
 * pl_chg
   * 의미: 손익 금액 
 * pl_chg_pct
   * 의미: 손익률  

|date|	item_cd|	book_amt|	book_price|	book_asset|	eval_price|	eval_asset|	pl_chg|	pl_chg_pct|
|---|---|---|---|---|---|---|---|---|
|2006-01-31|	000060|	87	|5788|	503556|	5788|	503556|	0|	0.0|
|2006-01-31|	000220|	58	|8668|	502744|	8668|	502744|	0|	0.0|
|2006-01-31|	000320|	82	|6106|	500692|	6106|	500692|	0|	0.0|
|2006-01-31|	000370|	73	|6833|	498809|	6833|	498809|	0|	0.0|
|2006-01-31|	000490|	221 |2280|	503880|	2280|	503880|	0|	0.0|

### 3. sheet_trade(거래)


 * item_cd
   * 의미: 자산 코드
 * buy_sell
   * 의미: 매수/매도
 * amt
   * 의미: 매매 수량
 * price
   * 의미: 매매 단가  
 * asset
   * 의미: 매매 금액  


|date|	item_cd|	buy_sell|	amt|	price|	asset|
|---|---|---|---|---|---|
|2006-01-31|	000060|	1|	87	|5788|	503556
|2006-01-31|	000220|	1|	58	|8668|	502744
|2006-01-31|	000320|	1|	82	|6106|	500692
|2006-01-31|	000370|	1|	73	|6833|	498809
|2006-01-31|	000490|	1|	221| 2280|	503880

# Factor Performance Example
```python
folder_nm = "stock_growth"

with open(r'D:\MyProject\FactorSelection\backtest\{}\sheet_balance.pickle'.format(folder_nm), 'rb') as fr:
    df_balance = pickle.load(fr)

df_balance["chg_pct"] = df_balance["asset_total"].pct_change()
df = df_balance[["date", "chg_pct"]].set_index("date")["chg_pct"]

qs.reports.plots(df, mode='full')
```
![image](https://github.com/song-junho/FactorBackTest/assets/67362481/9d1f5af7-d92a-481d-94a5-85e21846022f)
![image](https://github.com/song-junho/FactorBackTest/assets/67362481/e060001d-f3df-4eb2-a774-916b7ed475da)
![image](https://github.com/song-junho/FactorBackTest/assets/67362481/f1169d72-56f5-4f63-9b03-5eb0d34ef525)
![image](https://github.com/song-junho/FactorBackTest/assets/67362481/c72ba87f-0fe2-47fb-b7d0-8f93c5c07941)

# 경기 국면별 Factor Index 상대 강도
> 경기 순환 국면 (Recovery, Expansion, Slowdown, Contraction)  
> 목적: 각 국면별 Facor Index 상대강도 확인  

 * x축: CPI
   * 선정 이유 1: 물가 수준을 판단하는 대표적인 지표
   * 선정 이유 2: 발표 lagging time 짧음(익월 4영업일 이내)  
   * 가공 방식 : z_scoring(look back window: 3y , 경기 변화 반영)
   
 * y축: 수출 데이터
   * 선정 이유 1: 수출 국가인 대한민국의 경기를 가장 잘 나타내는 지표
   * 선정 이유 2: 발표 lagging time 짧음(익월 1일)  
   * 가공 방식 : z_scoring(look back window: 3y , 경기 변화 반영)
   
   
 * 경기 순환 국면 차트 예시
![image](https://github.com/song-junho/FactorBackTest/assets/67362481/6b48faab-8c7c-4e45-98de-d6318f54ea99)

 * 경기 국면별 Factor Index 수익률(월평균) 예시
 
 	|phase	     |value	     |growth	|gold    |
 	|---|---|---|---|
    |contraction |1.263333	 |2.074444	|0.295604|
    |expansion	 |1.103509	 |1.126316	|0.819298|
    |recovery	 |2.941026	 |1.866667	|1.051282|
    |slowdown	 |2.195238	 |2.585714	|2.200000|