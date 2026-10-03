from django.contrib import admin
from .models import Category, Product, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "price",
        "stock",
        "available",
        "image",
        "created_at",
    )

    list_filter = ("category", "available")
    search_fields = ("name", "description")
    list_editable = ("price", "stock", "available")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "full_name",
        "email",
        "total_amount",
        "status",
        "created_at",
    )

    list_filter = ("status", "created_at")
    search_fields = (
        "full_name",
        "email",
        "phone",
        "user__username",
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "quantity",
        "price",
    )

    search_fields = (
        "product__name",
        "order__full_name",
    )