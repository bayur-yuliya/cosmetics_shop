import json
import os
from decimal import Decimal

from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.db import transaction

from cosmetics_shop.models import Brand, Category, GroupProduct, Product, Tag


class Command(BaseCommand):
    help = "Seed database with realistic demo data"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Cleaning cache...")

        try:
            cache.clear()
            self.stdout.write(self.style.SUCCESS("Cleaning cache Done"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to clear cache: {e}"))
            return

        self.stdout.write("Seeding data...")

        # -------- CATEGORIES --------
        categories_data = ["Лицо", "Волосы", "Тело", "Макияж", "Парфюмерия"]
        categories = {
            name: Category.objects.get_or_create(name=name)[0]
            for name in categories_data
        }

        # -------- BRANDS --------
        brands_data = [
            "La Roche-Posay",
            "The Ordinary",
            "CeraVe",
            "Vichy",
            "L'Oreal Professionnel",
            "Maybelline New York",
            "Lancome",
            "Bioderma",
            "Kiehl's",
            "Redken",
            "Matrix",
            "Nyx Professional Makeup",
            "Yves Saint Laurent",
            "Giorgio Armani",
            "Estée Lauder",
            "Clarins",
            "Biotherm",
            "Shu Uemura",
            "Kérastase",
            "Givenchy",
            "Guerlain",
            "Dior",
            "Chanel",
            "Shiseido",
            "Nuxe",
            "L'Occitane",
            "Molton Brown",
            "Hermès",
        ]
        brands = {
            name: Brand.objects.get_or_create(name=name)[0] for name in brands_data
        }

        # -------- GROUPS --------
        groups_config = [
            ("Очищение", "Лицо"),
            ("Увлажнение", "Лицо"),
            ("Сыворотки", "Лицо"),
            ("Крема", "Лицо"),
            ("Лосьоны", "Лицо"),
            ("Патчи", "Лицо"),
            ("Шампуни", "Волосы"),
            ("Кондиционеры", "Волосы"),
            ("Маски для волос", "Волосы"),
            ("Бальзамы для волос", "Волосы"),
            ("Ополаскиватели для волос", "Волосы"),
            ("Против перхоти", "Волосы"),
            ("Солнцезащита", "Тело"),
            ("Кремы для рук", "Тело"),
            ("Кремы для тела", "Тело"),
            ("Мыло", "Тело"),
            ("Пена для ванн", "Тело"),
            ("Скрабы", "Тело"),
            ("Тушь для ресниц", "Макияж"),
            ("Тени для век", "Макияж"),
            ("Помады", "Макияж"),
            ("Румяна", "Макияж"),
            ("Карандаши", "Макияж"),
            ("Подводки", "Макияж"),
            ("Тональные средства", "Макияж"),
            ("Женская парфюмерия", "Парфюмерия"),
            ("Мужская парфюмерия", "Парфюмерия"),
            ("Унисекс парфюмерия", "Парфюмерия"),
            ("Миниатюры", "Парфюмерия"),
        ]
        groups = {
            name: GroupProduct.objects.get_or_create(
                name=name, category=categories[cat]
            )[0]
            for name, cat in groups_config
        }

        # -------- TAGS --------
        tags_data = [
            "Для сухой кожи",
            "Для жирной кожи",
            "Для чувствительной кожи",
            "Без парабенов",
            "Веган",
            "SPF 50",
            "Против выпадения",
            "С ретинолом",
            "С гиалуроновой кислотой",
            "Водостойкий",
            "Для всех типов кожи",
        ]
        tags = {name: Tag.objects.get_or_create(name=name)[0] for name in tags_data}

        # -------- PRODUCTS --------
        file_path = os.getenv("PRODUCTS_FILE")

        if file_path:
            if not os.path.exists(file_path):
                raise FileNotFoundError(
                    "products_data.json not found. Copy products_data_example.json"
                )

            with open(file_path, encoding="utf-8") as f:
                products_list = json.load(f)
                for p_data in products_list:
                    product, created = Product.objects.get_or_create(
                        name=p_data["name"],
                        defaults={
                            "group": groups[p_data["group"]],
                            "brand": brands[p_data["brand"]],
                            "price": Decimal(p_data["price"]),
                            "stock": p_data["stock"],
                            "description": p_data["desc"],
                        },
                    )

                    if created:
                        product.tags.set([tags[t] for t in p_data["tags"]])
        else:
            self.style.ERROR("PRODUCTS_FILE not found.")

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ The database has been successfully populated with "
                f"({len(products_list)} product)"
            )
        )
