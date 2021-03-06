"""
    Maps urls to views in market.views.
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('market.views',
    (r'^$', 'index'),
    (r'^cancel/$', 'cancel_order'),
    (r'^upload/$', 'upload_data'),
    (r'^update/(?P<market_slug>[-\w]+)/$', 'update_market_info'),
    (r'^export/(?P<market_slug>[-\w]+)/$', 'export_data'),
    (r'^prices/(?P<market_slug>[-\w]+)/$', 'latest_prices'),
    (r'^orders/(?P<market_slug>[-\w]+)/$', 'get_orders'),
    (r'^portfolio/(?P<market_slug>[-\w]+)/(?P<trader_name>[-\w]+)/$', 'update_portfolio'),
    (r'^(?P<market_slug>[-\w]+)/$', 'market'),
    (r'^(?P<market_slug>[-\w]+)/(?P<trader_name>[-\w]+)/$', 'trader'),
)

