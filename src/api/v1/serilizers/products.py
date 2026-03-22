from rest_framework import serializers

from cosmetics_shop.models import Brand, Category, GroupProduct, Product, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "slug"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class GroupSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = GroupProduct
        fields = ["id", "name", "slug", "category"]


class ProductListSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()
    group = GroupSerializer()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "stock",
            "code",
            "brand",
            "group",
            "is_active",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()
    group = GroupSerializer()
    tags = TagSerializer(many=True)

    class Meta:
        model = Product
        fields = "__all__"


class ProductWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "name",
            "group",
            "brand",
            "price",
            "description",
            "stock",
            "image",
            "tags",
            "is_active",
        ]
