from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from futures_market.market.models import *

class Command(BaseCommand):
    args = '<market>'

    @transaction.commit_manually
    def handle(self, *args, **options):
        market = args[0]
        m = Market.objects.get(slug=market)
        m.market_open = False
        m.save()
        holdings = Holding.objects.filter(market=m)
        for h in holdings:
            value = h.shares * h.stock.liquidation_price
            h.trader.cash += value
            h.trader.save()
        holdings.delete()

        transaction.commit()

