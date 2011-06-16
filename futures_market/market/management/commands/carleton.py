from futures_market.market.models import *
from django.db import transaction

@transaction.commit_manually
def create():
    stocks = ['ma-accept', 'ma-attend']
    liquidation_prices = [0.71, 0.29]
    traders = ['dlibenno', 'levinew', 'mtie', 'rugglese', 'maurera', 'altschue', 'balls', 'baquiss', 'bentleye', 'brobecke', 'burghare', 'cantors', 'carterj', 'conwayv', 'draperk', 'ellebrep', 'finen', 'fleishem', 'gibsona', 'gilmoreb', 'goodwinh', 'halla', 'hestr', 'johnsoha', 'jonesm', 'kanazama', 'linderr', 'longd', 'luoh', 'mcphersh', 'miyamotk', 'morseje', 'myersg', 'narveyj', 'obrienk', 'oconnelk', 'ogaraa', 'pernellm', 'pittmanj', 'pricea', 'reardonj', 'robertsk', 'sacksd', 'sapsen', 'schumacm', 'seraydab', 'silbigek', 'sinsheic', 'sjobergj', 'sokl', 'suna', 'thomase', 'wangb', 'wint', 'winere', 'yangj', 'zicafook', 'zimmerm', 'ehrenbed', 'aingc', 'nelsonp']

    m = Market(question='Carleton acceptance?', slug='carleton', cash_endowment=100)
    m.save()

    for trader in traders:
        t = Trader(name=trader, market=m, cash=m.cash_endowment)
        t.save()
    for i in range(len(stocks)): 
        s = Stock(market=m, name=stocks[i], slug=stocks[i], liquidation_price=liquidation_prices[i], stock_endowment=100, total_shares=len(traders)*100)
        s.save()

    for trader in traders:
        t = Trader.objects.get(name=trader)
        for stock in stocks:
            s = Stock.objects.get(name=stock)
            h = Holding(market=m, trader=t, stock=s, shares=s.stock_endowment)
            h.save()

    transaction.commit()


