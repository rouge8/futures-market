from market.models import *
from django.contrib import admin

class MarketAdmin(admin.ModelAdmin):
    fields = ['question', 'description', 'cash_endowment', 'market_open']
    readonly_fields = ['creation_date']

admin.site.register(Market, MarketAdmin)
admin.site.register(Stock)
admin.site.register(Trader)
admin.site.register(Holding)
admin.site.register(Order)
