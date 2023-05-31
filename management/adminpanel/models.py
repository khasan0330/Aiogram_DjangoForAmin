from django.db import models


class Users(models.Model):
    """База пользователей"""
    user_name = models.CharField(max_length=150, verbose_name='Имя пользователя' )
    user_telegram = models.BigIntegerField(unique=True, verbose_name='Телеграм ID')
    user_phone = models.CharField(max_length=150, null=True, blank=True, verbose_name='Контактный номер')

    def __str__(self):
        return self.user_name

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Carts(models.Model):
    """Временная корзинка покупателя"""
    user = models.ForeignKey(Users,  on_delete=models.CASCADE, verbose_name='Пользователь')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name='Сумма продуктов')
    total_products = models.IntegerField(null=True, verbose_name='Количество продуктов')

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'Корзинка'
        verbose_name_plural = 'Корзинки'


class Finally_carts(models.Model):
    """Корзинка продуктов для Кассы"""
    cart = models.ForeignKey(Carts, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=150)
    product_quantity = models.IntegerField()
    final_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cart_id', 'product_name'], name='unique_cart_product')
        ]
        verbose_name = 'Касса'
        verbose_name_plural = 'Кассы'

    def __str__(self):
        return str(self.cart)


class Categories(models.Model):
    """Категории продуктов"""
    category_name = models.CharField(max_length=150, unique=True, verbose_name='Категория')

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Products(models.Model):
    """Продукты"""
    product_category = models.ForeignKey(Categories, on_delete=models.CASCADE, verbose_name='Категория')
    product_name = models.CharField(max_length=150, unique=True, verbose_name='Наименования')
    product_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Стоимость')
    product_info = models.TextField(default='Описания продукта...', verbose_name='Описания')
    product_image = models.ImageField(upload_to='photos/', verbose_name='Изображения')

    def __str__(self):
        return self.product_name

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'




