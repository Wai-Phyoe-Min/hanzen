from django.core.management.base import BaseCommand
from restaurant.models import SiteSettings, BusinessHours
import datetime

class Command(BaseCommand):
    help = 'Creates SiteSettings and BusinessHours if they do not exist'

    def handle(self, *args, **kwargs):
        # Create SiteSettings
        settings, created = SiteSettings.objects.get_or_create(pk=1)
        if created:
            self.stdout.write(self.style.SUCCESS('SiteSettings created'))
        else:
            self.stdout.write('SiteSettings already exists')

        # Create BusinessHours for all 7 days
        for day in range(7):
            bh, created = BusinessHours.objects.get_or_create(
                day=day,
                defaults={
                    'is_closed': day == 1,  # Tuesday closed
                    'lunch_open': None if day == 1 else datetime.time(11, 30),
                    'lunch_close': None if day == 1 else datetime.time(14, 0),
                    'dinner_open': None if day == 1 else datetime.time(18, 0),
                    'dinner_close': None if day == 1 else datetime.time(22, 30),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'BusinessHours day {day} created'))