from django.contrib import admin
from .models import user_info, order_info, order_details
# Register your models here.

admin.site.register(user_info)
admin.site.register(order_info)
admin.site.register(order_details)