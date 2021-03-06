import random
import string
import datetime

from django.utils.text import slugify
from django.utils.dateparse import parse_date
from django.utils.timezone import make_aware

from companies.models import Company
from django.forms.models import model_to_dict


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_key_generator(instance):
    size = random.randint(30, 45)
    key = random_string_generator(size=size)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(key=key).exists()
    if qs_exists:
        return unique_slug_generator(instance)
    return key


def unique_order_id_generator(instance):
    order_new_id = random_string_generator()
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(order_id=order_new_id).exists()
    if qs_exists:
        return unique_slug_generator(instance)
    return order_new_id


def unique_slug_generator(instance, new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.title)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
                    slug=slug,
                    randstr=random_string_generator(size=4)
                )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug


def get_date_obj(date_value):
        try:
            timestamp = datetime.datetime.strptime(date_value, '%d/%m/%Y %H:%M').timestamp()
            datetime_obj = make_aware(datetime.datetime.fromtimestamp(timestamp))
            datetime_obj = datetime_obj.replace(tzinfo=None)
            error = False
        except ValueError:
            datetime_obj = parse_date(date_value)
            error = True
        return datetime_obj, error

# def format_datetime_obj(datetime_obj):
#     year = datetime_obj.year
#     month = datetime_obj.month
#     day = datetime_obj.day
#     hour = datetime_obj.hour
#     minute = datetime_obj.minute
#
#     datetime_str = datetime.datetime(year, month, day, hour, minute)
#
#     print(x.strftime("%b %d %Y %H:%M:%S"))


def generate_menu(user):
    tfl_company = {
        'id': 4,
        'name': 'TFL'
    }
    data = {
        'companies_menu': []
    }
    if user.is_authenticated:
        if user.is_admin or user.is_staff:
            all_companies = Company.objects.all()
            for c in all_companies:
                company = {
                    'id': c.id,
                    'name': c.name
                }
                data['companies_menu'].append(company)
        elif user.have_company:
            company = {
                'id': user.company.id,
                'name': user.company.name
            }
            data['companies_menu'].append(company)
            data['companies_menu'].append(tfl_company)
        else:
            data['companies_menu'].append(tfl_company)
        return data
    else:
        data['companies_menu'].append(tfl_company)
        return data

