from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from market.forms import *
from market.models import *
from datetime import datetime

def index(request):
    return render_to_response('market/index.html')

def market(request, market_slug):
    m = get_object_or_404(Market, slug=market_slug)
    return render_to_response('market/market.html', {'market': m})

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
    matches = list(matches)
    resolved = False

    while not(resolved) and len(matches) > 0 and order.volume > 0:
        match = matches.pop(0)
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
        volume = min(buyer.cash // price, order.volume, seller_holding.shares)
        value = volume * price

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
            if o.volume - volume == 0:
                o.completed = True
                o.completion_time = datetime.now()
                resolved = True
            else:
                o.volume -= volume
                new = Order(market=order.market, stock=order.stock, trader=order.trader,
                    creation_time = order.creation_time, price = order.price,
                    volume=volume, completed=True, completion_time=datetime.now())
                # django has no way to duplicate a model :(
                new.save()
            o.save()
    transaction.commit()


        


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
            resolve_order(order)

            return HttpResponseRedirect(request.path)

    else: # normal GET request
        if t:
            open_orders = Order.objects.filter(market=m, trader=t, completed=False)
            closed_orders = Order.objects.filter(market=m, trader=t, completed=True)
            form = OrderForm()

            data = {'trader': t, 'open_orders': open_orders, 'closed_orders': closed_orders, 'form': form} 

        return render_to_response('market/trader.html', data, context_instance=RequestContext(request))
