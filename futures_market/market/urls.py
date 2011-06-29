"""
    Maps urls to views in market.views.
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('market.views',
    (r'^$', 'index'),
    (r'^cancel/$', 'cancel_order'),
    (r'^prices/(?P<market_slug>[-\w]+)/$', 'latest_prices'),
    (r'^orders/(?P<market_slug>[-\w]+)/$', 'get_orders'),
    (r'^portfolio/(?P<market_slug>[-\w]+)/(?P<trader_name>[-\w]+)/$', 'update_portfolio'),
    (r'^(?P<market_slug>[-\w]+)/$', 'market'),
    (r'^(?P<market_slug>[-\w]+)/(?P<trader_name>[-\w]+)/$', 'trader'),
)

