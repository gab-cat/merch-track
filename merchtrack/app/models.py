from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.utils.timezone import now

# Create your database models here.

class user_info(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    student_id = models.CharField(
        max_length=9, 
        primary_key=True,  # Make student_id the primary key
        unique=True, 
        validators=[RegexValidator(r'^[0-9]{1,9}$', 'Student ID must be numeric and have at most 9 digits.')]
    )
    student_name = models.CharField(max_length=200)
    course = models.CharField(max_length=200)
    email = models.CharField(max_length=200)

    def __str__(self):
        return self.student_id

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
    message = models.TextField(max_length=200)
    created_at = models.DateTimeField(default=now) 



# NEW DATA

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, default=999)
    phone = models.CharField(max_length=15)
    course = models.CharField(max_length=200)

    class Meta:
        db_table = 'customer'
        constraints = [
            models.UniqueConstraint(fields=['user'], name='unique_customer_id')
        ]
        indexes = [
            models.Index(fields=['user'], name='customer_id_idx')
        ]

class Product(models.Model):
    productId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)

    class Meta:
        db_table = 'product'
        constraints = [
            models.UniqueConstraint(fields=['productId'], name='unique_product_id')
        ]
        indexes = [
            models.Index(fields=['productId'], name='product_id_idx')
        ]

class Order(models.Model):
    orderId = models.AutoField(primary_key=True)
    customerId = models.ForeignKey(Customer, on_delete=models.CASCADE, default=999)
    processedBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name='processed_orders', default=999)
    orderDate = models.DateTimeField(default=now)
    status = models.CharField(max_length=50, default="Pending")
    totalAmount = models.FloatField(max_length=10, default=0)
    discountAmount = models.FloatField(max_length=10, default=0)
    estimatedDeliveryDate = models.DateTimeField()

    class Meta:
        db_table = 'order'
        constraints = [
            models.UniqueConstraint(fields=['orderId'], name='unique_order_id')
        ]
        indexes = [
            models.Index(fields=['orderId'], name='order_id_idx')
        ]

class OrderItem(models.Model):
    orderItemId = models.AutoField(primary_key=True)
    orderId = models.ForeignKey(Order, on_delete=models.CASCADE)
    productId = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    customerNote = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'order_item'
        constraints = [
            models.UniqueConstraint(fields=['orderItemId'], name='unique_order_item_id')
        ]
        indexes = [
            models.Index(fields=['orderItemId'], name='order_item_id_idx')
        ]

class Payment(models.Model):
    paymentId = models.AutoField(primary_key=True)
    orderId = models.ForeignKey(Order, on_delete=models.CASCADE)
    customerId = models.ForeignKey(Customer, on_delete=models.CASCADE, default=999)
    processedBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name='processed_payments', default=999)
    paymentDate = models.DateTimeField(default=now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paymentMethod = models.CharField(max_length=50)
    paymentStatus = models.CharField(max_length=50, default="For Verification")
    referenceNumber = models.CharField(max_length=100, default="")

    class Meta:
        db_table = 'payment'
        constraints = [
            models.UniqueConstraint(fields=['paymentId'], name='unique_payment_id')
        ]
        indexes = [
            models.Index(fields=['paymentId'], name='payment_id_idx')
        ]

class Inventory(models.Model):
    inventoryId = models.AutoField(primary_key=True)
    productId = models.OneToOneField(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        db_table = 'inventory'
        constraints = [
            models.UniqueConstraint(fields=['inventoryId'], name='unique_inventory_id')
        ]
        indexes = [
            models.Index(fields=['inventoryId'], name='inventory_id_idx')
        ]

class Fulfillment(models.Model):
    fulfillmentId = models.AutoField(primary_key=True)
    orderId = models.OneToOneField(Order, on_delete=models.CASCADE)
    fulfillmentDate = models.DateTimeField(default=now)
    processedBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name='processed_fulfillments', default=999)
    status = models.CharField(max_length=50, default="Pending")


    class Meta:
        db_table = 'fulfillment'
        constraints = [
            models.UniqueConstraint(fields=['fulfillmentId'], name='unique_fulfillment_id')
        ]
        indexes = [
            models.Index(fields=['fulfillmentId'], name='fulfillment_id_idx')
        ]

class Log(models.Model):
    logId = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=999)
    reason = models.CharField(max_length=255)
    system_text = models.TextField()
    user_text = models.TextField()

    def __str__(self):
        return f"Log for {self.customer.user.username} by {self.created_by.username} on {self.created_date}"
    
    class Meta:
        db_table = 'log'
        constraints = [
            models.UniqueConstraint(fields=['logId'], name='unique_logId_id')
        ]
        indexes = [
            models.Index(fields=['logId'], name='logId_id_idx')
        ]
