"""
    Registers database models with the django admin interface.
"""

from market.models import *
from django.contrib import admin

class StockInline(admin.StackedInline):
    model = Stock
    extra = 1

class MarketAdmin(admin.ModelAdmin):
    fields = ['question', 'slug', 'cash_endowment', 'market_open']
    readonly_fields = ['creation_date']
    inlines = [StockInline]

admin.site.register(Market, MarketAdmin)
admin.site.register(Stock)
admin.site.register(Trader)
admin.site.register(Holding)
admin.site.register(Order)
