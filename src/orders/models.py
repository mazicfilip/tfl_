from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.urls import reverse
from django.db.models import Q

from carts.models import Cart
from tfl.utils import unique_order_id_generator

User = settings.AUTH_USER_MODEL

ORDER_STATUS_CHOICES = (
    ('created', 'Created'),
    ('confirm', 'Confirm'),
    ('canceled', 'Canceled')
)


class OrderQuerySet(models.query.QuerySet):
    def all(self):
        return self.filter(active=True).order_by('-timestamp')

    def my_orders(self, user):
        lookups = (Q(cart__user=user) &
                   Q(active=True)
                   )
        return self.filter(lookups).order_by('-timestamp')

    def company_orders(self, company):
        lookups = (Q(cart__company=company) &
                   Q(active=True)
                   )
        return self.filter(lookups).order_by('-timestamp')

    def by_cart_products(self, cart_products_obj):
        lookups = (Q(cart__products__in=cart_products_obj) &
                   Q(active=True))

        return self.filter(lookups)

    def cp_exist(self, order, cart_product):
        lookups = (Q(id=order.id) & Q(cart__products=cart_product))

        qs = self.filter(lookups)
        if qs.count() == 1:
            return True
        return False


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def my_orders(self, user):
        return self.get_queryset().my_orders(user)

    def company_orders(self, user):
        company = user.company
        return self.get_queryset().company_orders(company)

    def get_by_company(self, company):
        return self.get_queryset().company_orders(company)

    def all(self, user):
        if user.is_staff or user.is_admin:
            return self.get_queryset().all()
        else:
            return self.company_orders(user)

    def get_by_cart_products(self, cart_products_obj):
        return self.get_queryset().by_cart_products(cart_products_obj)

    def cp_exist(self, order, cart_product):
        return self.get_queryset().cp_exist(order, cart_product)


class Order(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    order_id = models.CharField(max_length=120, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    status = models.CharField(max_length=120, default='created', choices=ORDER_STATUS_CHOICES)
    total_price = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    total_weight = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    objects = OrderManager()

    def __str__(self):
        return self.order_id

    def get_absolute_url(self):
        return reverse('orders:detail', kwargs={'id': self.id})

    def update_total(self):
        self.total_price = self.cart.total_price
        self.total_weight = self.cart.total_weight
        self.save()

    def deactivate(self):
        self.active = False
        self.save()


def pre_save_create_order_id(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)


pre_save.connect(pre_save_create_order_id, sender=Order)


def post_save_cart_total(sender, instance, created, *args, **kwargs):
    if not created:
        cart_obj = instance
        cart_id = cart_obj.id
        qs = Order.objects.filter(cart__id=cart_id)
        if qs.count() == 1:
            order_obj = qs.first()
            order_obj.update_total()


post_save.connect(post_save_cart_total, sender=Cart)


def post_save_order(sender, instance, created, *args, **kwargs):
    if created:
        instance.update_total()


post_save.connect(post_save_order, sender=Order)


