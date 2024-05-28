from django import forms
from app.models import Order, OrderItem, Customer

class OrderForm(forms.ModelForm):
    estimatedDeliveryDate = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Order
        fields = ['customerId', 'status', 'totalAmount', 'discountAmount', 'estimatedDeliveryDate']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(OrderForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['processedBy'].initial = user

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['productId', 'quantity', 'price', 'customerNote']
