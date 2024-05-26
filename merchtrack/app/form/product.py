from django import forms
from app.models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'productImage']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
