from django.contrib import admin

from .models import Customer, Log, CustomerSatisfactionSurvey, Fulfillment, Inventory, Order, OrderItem, Payment, Product, contact_us
# Register your models here.


admin.site.register(Customer)
admin.site.register(Product)

admin.site.register(Order)

admin.site.register(OrderItem)

admin.site.register(Payment)

admin.site.register(Inventory)

admin.site.register(Fulfillment)

admin.site.register(Log)

admin.site.register(CustomerSatisfactionSurvey)

