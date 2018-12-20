# Generated by Django 2.1.3 on 2018-12-19 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0017_product_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='weight',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=20),
        ),
    ]
