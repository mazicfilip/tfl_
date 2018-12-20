# Generated by Django 2.1.3 on 2018-12-19 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart',
            old_name='total',
            new_name='total_price',
        ),
        migrations.AddField(
            model_name='cart',
            name='total_weight',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=100),
        ),
    ]
