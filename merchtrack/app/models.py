from django.db import models
from django.core.validators import RegexValidator

# Create your database models here.

class user_info(models.Model):
    student_id = models.CharField(max_length=9, validators=[RegexValidator(r'^[0-9]{1,9}$', 'Student ID must be numeric and have at most 9 digits.')])
    student_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    course  = models.CharField(max_length=200)

class order_info(models.Model):
    order_date = models.CharField(max_length=200)
    distribution_date = models.CharField(max_length=200)
    order_status = models.CharField(max_length=200)
    payment_method = models.CharField(max_length=200)
    payment_status = models.CharField(max_length=200)

    order_details_id = models.CharField(max_length=200, default='0')
    user_info_id  = models.CharField(max_length=9, default='000000000')
    
class order_details(models.Model):
    order_details_id = models.CharField(max_length=200)
    item_name = models.CharField(max_length=200)
    item_size = models.CharField(max_length=200)
    item_color = models.CharField(max_length=200)
    item_cost = models.CharField(max_length=200)
    item_quantity = models.CharField(max_length=200)

class contact_us(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    message = models.TextField(max_length=500)