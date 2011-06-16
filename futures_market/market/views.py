from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from market.forms import *
from market.models import *

def index(request):
    return render_to_response('market/index.html')

def market(request, market_slug):
    m = get_object_or_404(Market, slug=market_slug)
    return render_to_response('market/market.html', {'market': m})

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

            return HttpResponseRedirect(request.path)

    else: # normal GET request
        if t:
            open_orders = Order.objects.filter(market=m, trader=t, completed=False)
            closed_orders = Order.objects.filter(market=m, trader=t, completed=True)
            form = OrderForm()

            data = {'trader': t, 'open_orders': open_orders, 'closed_orders': closed_orders, 'form': form} 

        return render_to_response('market/trader.html', data, context_instance=RequestContext(request))
