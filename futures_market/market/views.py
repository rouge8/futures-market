from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.db import transaction
from datetime import datetime
from market.forms import *
from market.models import *
import json, calendar

def index(request):
    markets = Market.objects.all()
    return render_to_response('market/index.html', {'markets': markets })

def market(request, market_slug):
    if request.method == 'POST':
        m = get_object_or_404(Market, slug=market_slug)
        if request.POST.get('open'):
            m.market_open = True
            m.save()
        elif request.POST.get('liquidate'):
            m.market_open = False
            m.save()
            liquidate(m)

        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        m = get_object_or_404(Market, slug=market_slug)
        return render_to_response('market/market.html', {'market': m}, context_instance=RequestContext(request))

@transaction.commit_manually
def liquidate(market):
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
    if request.method == 'POST':
        trader = get_object_or_404(Trader, id=int(request.POST['trader']))
        order = get_object_or_404(Order, id=int(request.POST['order']))
        assert order.trader == trader

        if order.completed == False: # else bad news...
            order.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@transaction.commit_manually
def resolve_order(order):
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

def update_portfolio(request, market_slug, trader_name):
    m = get_object_or_404(Market, slug=market_slug)
    t = get_object_or_404(Trader, name=trader_name, market=m)
    
    if t:
        open_orders = Order.objects.filter(market=m, trader=t, completed=False)
        closed_orders = Order.objects.filter(market=m, trader=t, completed=True)
        form = OrderForm()
        data = {'trader': t, 'open_orders': open_orders, 'closed_orders': closed_orders, 'form': form} 

        return render_to_response('market/portfolio.html', data, context_instance=RequestContext(request))

def trader(request, market_slug, trader_name):
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
            open_orders = Order.objects.filter(market=m, trader=t, completed=False)
            closed_orders = Order.objects.filter(market=m, trader=t, completed=True)
            form = OrderForm()

            data = {'trader': t, 'open_orders': open_orders, 'closed_orders': closed_orders, 'form': form} 

        return render_to_response('market/trader.html', data, context_instance=RequestContext(request))

def latest_prices(request, market_slug):
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

def new_orders(request, market_slug):
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
