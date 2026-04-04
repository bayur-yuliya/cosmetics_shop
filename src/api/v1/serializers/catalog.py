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


class ProductShortListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
        ]


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


class ProductDetailSerializer(ProductListSerializer):
    group = GroupSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + ["description", "group", "tags"]


class ProductWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())

    class Meta:
        model = Product
        fields = [
            "name",
            "group",
            "brand",
            "price",
            "description",
            "stock",
            "tags",
            "is_active",
        ]
