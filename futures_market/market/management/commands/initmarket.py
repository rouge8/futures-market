from django.core.management.base import BaseCommand, CommandError
from futures_market.market.models import *

class Command(BaseCommand):
    args = '<market>'

    def handle(self, *args, **options):
        market = args[0]
        if market == 'carleton':
            import carleton
            carleton.create()
