from django.contrib import admin
from .models import Users, Carts, Finally_carts, Categories, Products
from django.utils.safestring import mark_safe


class UsersAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'user_phone', 'user_telegram')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_category', 'product_price', 'get_photo')

    def get_photo(self, obj):
        return mark_safe(f'<img src="{obj.product_image.url}" width="75">')

    get_photo.short_description = 'Миниатюра'


class CartAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'total_price', 'total_products')


class FinallyCartsAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'product_name', 'product_quantity', 'final_price')


admin.site.register(Users, UsersAdmin)
admin.site.register(Products, ProductAdmin)
admin.site.register(Categories)
admin.site.register(Carts, CartAdmin)
admin.site.register(Finally_carts, FinallyCartsAdmin)
