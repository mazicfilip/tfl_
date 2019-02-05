import random
import os
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.urls import reverse
from django.apps import apps

from products_categories.models import ProductCategory
from tfl.utils import unique_slug_generator


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    new_filename = random.randint(1, 3265456541)
    name, ext = get_filename_ext(filename)
    final_name = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return 'products/{new_filename}/{final_name}'.format(
        new_filename=new_filename,
        final_name=final_name
    )


class ProductQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)

    def search(self, query):
        lookups = (Q(title__icontains=query) |
                   Q(description__icontains=query) |
                   Q(price__icontains=query) |
                   Q(tag__title__icontains=query)
                   )
        return self.filter(lookups).distinct()


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id)
        if qs.count() == 1:
            return qs.first()
        return None

    def search(self, query):
        return self.get_queryset().active().search(query)

    def get_choose_quantity(self, cart_obj):
        product_quantity = apps.get_model('product_quantities', 'ProductQuantity')
        quant_obj = product_quantity.get_queryset().get_product_quantity(cart_obj=cart_obj, product_obj=self)
        return quant_obj.quantity


class Product(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(default='abc', blank=True, unique=True)
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    weight = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=0, blank=False, null=False)
    image = models.ImageField(upload_to=upload_image_path, default='products/no-image.jpg')
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ProductManager()

    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title


def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(product_pre_save_receiver, sender=Product)
