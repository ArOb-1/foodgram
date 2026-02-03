import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        path = Path(settings.BASE_DIR) / 'data' / 'ingredients.csv'
        if not path.exists():
            self.stdout.write(self.style.ERROR('Файл ингредиентов не найден'))
            return
        with path.open(encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if not row:
                    continue
                name, measurement_unit = row[0], row[1]
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit
                )
        self.stdout.write(self.style.SUCCESS('Ингредиенты загружены'))
