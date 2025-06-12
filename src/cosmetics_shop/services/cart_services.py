from cosmetics_shop.models import Card, Product, CardItem


def add_product_to_card(user, product_id):
    product = Product.objects.get(id=product_id)
    card, _ = Card.objects.get_or_create(user=user)
    card_item, created = CardItem.objects.get_or_create(card=card, product=product, defaults={'quantity': 1})

    if not created:
        card_item.quantity += 1
        card_item.save()
