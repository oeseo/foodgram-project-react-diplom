import csv
import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    FILE_PATH = os.path.join('data', 'ingredients.csv')

    def handle(self, *args, **options):
        if Ingredient.objects.exists():
            print('Данные уже существуют!')
            return

        try:
            self.data_loader()
        except FileNotFoundError:
            print('Файл {} не найден'.format(self.FILE_PATH))
        except Exception as err:
            print('Ошибка при импорте данных: {}'.format(err))
        else:
            print('Данные успешно добавлены в БД!')

    def data_loader(self):
        with open(self.FILE_PATH, encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            ingredients = [Ingredient(
                name=name,
                measurement_unit=measurement_unit)
                for name, measurement_unit in reader]
            Ingredient.objects.bulk_create(ingredients)
