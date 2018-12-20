# Generated by Django 2.1.3 on 2018-12-12 22:58

from django.db import migrations, models
import products.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_auto_20181212_2341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(default='/media/products/no-image.jpg', upload_to=products.models.upload_image_path),
        ),
    ]
