from django.shortcuts import render_to_response, get_object_or_404
from market.models import *

def index(request):
    return render_to_response('market/index.html')

def market(request, market_slug):
    m = get_object_or_404(Market, slug=market_slug)
    return render_to_response('market/market.html', {'market': m})

def trader(request, market_slug, trader_name):
    m = get_object_or_404(Market, slug=market_slug)
    t = get_object_or_404(Trader, name=trader_name)
    return render_to_response('market/trader.html', {'trader': t})
