from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from collections import defaultdict
from market.forms import *
from market.models import *
import json, calendar
import yaml

def index(request):
    """Renders an index view listing all of the markets."""
    markets = Market.objects.all()
    form = UploadFileForm()
    return render_to_response('market/index.html', {'markets': markets, 'form': form}, context_instance=RequestContext(request))

def market(request, market_slug):
    """Renders and processes the market manager view, allowing opening
       and liquidating of markets and listing traders."""

    m = get_object_or_404(Market, slug=market_slug)
    if request.method == 'POST':
        if request.POST.get('open'):
            m.market_open = True
            m.save()
        elif request.POST.get('liquidate'):
            m.market_open = False
            m.save()
            liquidate(m)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    else:
        return render_to_response('market/market.html', {'market': m}, context_instance=RequestContext(request))

@transaction.commit_manually
def liquidate(market):
    """Liquidates the market."""
    holdings = Holding.objects.filter(market=market)
    open_orders = Order.objects.filter(market=market,completed=False)
    for h in holdings:
        value = h.shares * h.stock.liquidation_price
        h.trader.cash += value
        h.trader.save()
    holdings.delete()
    open_orders.delete()
    transaction.commit()


def cancel_order(request):
    """Cancels orders."""
    if request.method == 'POST':
        trader = get_object_or_404(Trader, id=int(request.POST['trader']))
        order = get_object_or_404(Order, id=int(request.POST['order']))
        assert order.trader == trader

        if order.completed == False: # else bad news...
            order.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@transaction.commit_manually
def resolve_order(order):
    """Resolves an order."""
    # find potential orders to resolve
    matches = Order.objects.filter(market=order.market,stock=order.stock)
    matches = matches.filter(completed=False).exclude(trader=order.trader)

    if order.order == 'B':
        matches = matches.filter(order='S')
        matches = matches.filter(price__lte=order.price)
        sorting = ['price']
    elif order.order == 'S':
        matches = matches.filter(order='B')
        matches = matches.filter(price__gte=order.price)
        sorting = ['-price']
    # matches are ordered by highest volume first and creation_time is used
    # to break ties, with older orders being completed first
    sorting += ['-volume', '-creation_time']
    matches = matches.order_by(*sorting)

    for match in matches:
        if order.completed: break

        if order.order == 'B':
            price = min(order.price, match.price)
            buyer = order.trader
            seller = match.trader
        elif order.order == 'S':
            price = max(order.price, match.price)
            buyer = match.trader
            seller = order.trader

        stock = order.stock
        buyer_holding = buyer.holding_set.get(stock=stock)
        seller_holding = seller.holding_set.get(stock=stock)
        volume = min(buyer.cash // price, order.volume, seller_holding.shares, match.volume)
        value = volume * price
        assert volume >= 0
        assert price >= 0

        # update data
        buyer.cash -= value
        seller.cash += value
        stock.last_sale_price = price
        stock.last_sale_time = datetime.now()
        buyer_holding.shares += volume
        seller_holding.shares -= volume

        # save data
        buyer.save()
        seller.save()
        stock.save()
        buyer_holding.save()
        seller_holding.save()

        # update orders
        for o in [order, match]:
            if volume == 0: break

            if o.volume != volume: # order will be split
                done = Order(market=o.market, stock=o.stock, trader=o.trader,
                      order=o.order, creation_time=o.creation_time, price=price,
                      volume=volume, completed=True, completion_time=datetime.now())
                done.save()
                o.volume -= volume
            else:
                o.completed = True
                o.price = price
                o.completion_time=datetime.now()
            o.save()

    transaction.commit()

def get_portfolio_data(market, trader):
    """Returns dictionary of data for a trader view given market and trader.
       Contains a trader, open and closed orders for that trader, and the
       order form."""
    open_orders = Order.objects.filter(market=market, trader=trader, completed=False)
    closed_orders = Order.objects.filter(market=market, trader=trader, completed=True)
    form = OrderForm()
    data = {'trader': trader, 'open_orders': open_orders, 'closed_orders': closed_orders, 'form': form} 

    return data

def update_portfolio(request, market_slug, trader_name):
    """Updates trader portfolio."""
    m = get_object_or_404(Market, slug=market_slug)
    t = get_object_or_404(Trader, name=trader_name, market=m)
    
    if t:
        data = get_portfolio_data(m, t)

        return render_to_response('market/portfolio.html', data, context_instance=RequestContext(request))

def trader(request, market_slug, trader_name):
    """Renders trader view and processes orders."""
    
    m = get_object_or_404(Market, slug=market_slug)
    t = get_object_or_404(Trader, name=trader_name, market=m)
    
    if request.method == 'POST': # Order being placed!
        form = OrderForm(request.POST)

        if form.is_valid():
            order = form.save(commit = False)
            order.market = m
            order.trader = t
            order.save()
            if m.market_open:
                resolve_order(order)

            return HttpResponseRedirect(request.path)
        else:
            pass ## invalid form, how to handle?

    else: # normal GET request
        if t:
            data = get_portfolio_data(m, t)

        return render_to_response('market/trader.html', data, context_instance=RequestContext(request))

def latest_prices(request, market_slug):
    """Gets the latest stock prices and returns them as a list of JSON
       objects."""
    m = get_object_or_404(Market, slug=market_slug)
    stocks = Stock.objects.filter(market=m)
    data = []
    for stock in stocks:
        buy, sell = best_price(stock)
        if stock.last_sale_time:
            data.append({'last_sale_price': unicode(stock.last_sale_price),
                'last_sale_time': stock.last_sale_time.strftime('%d %b %y %H:%M:%S'),
                'best_buy': buy, 'best_sale': sell, 'name': stock.name})
        else:
            data.append({'last_sale_price': unicode(stock.last_sale_price),
                'last_sale_time': unicode(None),
                'best_buy': buy, 'best_sale': sell, 'name': stock.name})
    return HttpResponse(json.dumps(data))

def best_price(stock):
    buy = Order.objects.filter(stock=stock, order='B', completed=False).order_by('-price')
    if buy: buy = buy[0]
    else: buy = None

    sell = Order.objects.filter(stock=stock, order='S', completed=False).order_by('price')
    if sell: sell = sell[0]
    else: sell = None

    return unicode(buy), unicode(sell)

def get_orders(request, market_slug):
    """Returns JSON dictionary of orders on a market. Used to produce
       graphs."""

    m = get_object_or_404(Market, slug=market_slug)
    stocks = Stock.objects.filter(market=m)

    data = []
    for stock in stocks:
        s = {}
        s['label'] = stock.name
        o = Order.objects.filter(market=m, stock=stock, completed=True).values_list('completion_time', 'price')
        orders = []
        for order in o:
            orders.append([js_timestamp_from_datetime(order[0]), float(order[1])])
        s['data'] = orders
        data.append(s)
    return HttpResponse(json.dumps(data))

def js_timestamp_from_datetime(dt):
    return 1000 * calendar.timegm(dt.timetuple())

def validate_data(data):
    question = data.get('question')
    slug = data.get('slug')
    cash_endowment = data.get('cash_endowment')
    stocks_yaml = data.get('stocks')
    traders_yaml = data.get('traders')
    holdings_yaml = data.get('holdings', [])
    assert question and slug and cash_endowment and stocks_yaml and traders_yaml

    # validate traders
    for trader in traders_yaml:
        assert type(trader) == type('') or trader.get('name')

    # validate stocks
    for stock in stocks_yaml:
        assert stock.get('name') and stock.get('liquidation_price') and stock.get('stock_endowment')

    # validate holdings
    for holding in holdings_yaml:
        assert holding.get('trader') and holding.get('stock') and holding.get('shares')

@transaction.commit_manually
def load_data(data):
    validate_data(data)
    question = data.get('question')
    slug = data.get('slug')
    cash_endowment = data.get('cash_endowment')
    stocks = data.get('stocks')
    traders = data.get('traders')
    holdings = data.get('holdings', [])

    m, created = Market.objects.get_or_create(question=question, slug=slug, cash_endowment=cash_endowment, market_open=False)
    if not(created): assert False # already created = bad news
    m.save()

    for stock in stocks:
        name = stock.get('name')
        lp = stock.get('liquidation_price')
        se = stock.get('stock_endowment')
        s = Stock.objects.create(name=name, liquidation_price=lp, stock_endowment=se, market=m)
        s.save()

    for trader in traders:
        if type(trader) == type(''):
            t = Trader.objects.create(name=trader, cash=cash_endowment, market=m)
        else:
            name = trader.get('name')
            cash = trader.get('cash')
            if not(cash): cash = cash_endowment
            t = Trader.objects.create(name=name, cash=cash, market=m)
        t.save()

    for holding in holdings:
        trader = Trader.objects.get(name=holding['trader'])
        stock = Stock.objects.get(name=holding['stock'])
        shares = holding['shares']
        h = Holding.objects.create(trader=trader, stock=stock, shares=shares, market=m)
        h.save()

    # create holdings
    stocks = Stock.objects.filter(market=m)
    traders = Trader.objects.filter(market=m)
    for s in stocks:
        for t in traders:
            print s, t
            try:
                print 'getting...'
                Holding.objects.get(trader=t, stock=s)
                print 'got!'
            except Holding.DoesNotExist:
                h = Holding.objects.create(market=m, trader=t, stock=s,
                        shares = s.stock_endowment)
                h.save()
    transaction.commit()


def upload_data(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            data = yaml.load(f.read())
            load_data(data)
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        else:
            print form.errors

def export_data(request, market_slug):
    m = get_object_or_404(Market, slug=market_slug)
    stocks = Stock.objects.filter(market=m)
    traders = Trader.objects.filter(market=m)
    holdings = Holding.objects.filter(market=m)
    orders = Order.objects.filter(market=m)

    data = defaultdict(list)
    data['question'] = str(m.question)
    data['slug'] = str(m.slug)
    data['cash_endowment'] = float(m.cash_endowment)
    data['market_open'] = m.market_open

    for s in stocks:
        stock = {'name': str(s.name), 'liquidation_price': float(s.liquidation_price),
                'stock_endowment': s.stock_endowment,
                'last_sale_price': s.last_sale_price,
                'last_sale_time': s.last_sale_time}
        if s.last_sale_price:
            stock['last_sale_price'] = float(s.last_sale_price)
            
        data['stocks'].append(stock)

    for t in traders:
        trader = {'name': str(t.name), 'cash': float(t.cash)}
        data['traders'].append(trader)

    for h in holdings:
        holding = {'stock': str(h.stock.name), 'trader': str(h.trader.name),
                    'shares': h.shares}
        data['holdings'].append(holding)

    for o in orders:
        order = {'stock': str(o.stock.name), 'trader': str(o.trader.name),
                'order': str(o.get_order_display()),
                'creation_time': o.creation_time, 'volume': o.volume,
                'price': float(o.price), 'completed': o.completed,
                'completion_time': o.completion_time}
        data['orders'].append(order)

    data = dict(data) # PyYAML can't handle defaultdicts well

    response = HttpResponse(yaml.dump(data, default_flow_style=False),
            mimetype='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s.yaml' %(m.slug)
    return response
