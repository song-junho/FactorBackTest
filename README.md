# FactorBackTest
> InvestStrategy 의 output인 투자스케줄을 기반으로 백테스트 진행  
> Output: sheet_balance(자산) , sheet_book(북) , sheet_trade(거래)


# Output
### 1. sheet_balance(자산)
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
|date|	item_cd|	book_amt|	book_price|	book_asset|	eval_price|	eval_asset|	pl_chg|	pl_chg_pct|
|---|---|---|---|---|---|---|---|---|
|2006-01-31|	000060|	87	|5788|	503556|	5788|	503556|	0|	0.0|
|2006-01-31|	000220|	58	|8668|	502744|	8668|	502744|	0|	0.0|
|2006-01-31|	000320|	82	|6106|	500692|	6106|	500692|	0|	0.0|
|2006-01-31|	000370|	73	|6833|	498809|	6833|	498809|	0|	0.0|
|2006-01-31|	000490|	221 |2280|	503880|	2280|	503880|	0|	0.0|

### 3. sheet_trade(거래)

|date|	item_cd|	buy_sell|	amt|	price|	asset|
|---|---|---|---|---|---|
|2006-01-31|	000060|	1|	87	|5788|	503556
|2006-01-31|	000220|	1|	58	|8668|	502744
|2006-01-31|	000320|	1|	82	|6106|	500692
|2006-01-31|	000370|	1|	73	|6833|	498809
|2006-01-31|	000490|	1|	221| 2280|	503880
