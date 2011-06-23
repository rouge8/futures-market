from django.conf.urls.defaults import *

urlpatterns = patterns('market.views',
    (r'^$', 'index'),
    (r'^cancel/$', 'cancel_order'),
    (r'^prices/(?P<market_slug>[-\w]+)/$', 'latest_prices'),
    (r'^orders/(?P<market_slug>[-\w]+)/$', 'new_orders'),
    (r'^(?P<market_slug>[-\w]+)/$', 'market'),
    (r'^(?P<market_slug>[-\w]+)/(?P<trader_name>[-\w]+)/$', 'trader'),
)

