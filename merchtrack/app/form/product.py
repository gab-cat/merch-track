from django import forms
from app.models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'productImage']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get distinct categories
        existing_categories = list(Product.objects.values_list('category', flat=True).distinct())
        
        # Get the instance if available
        instance = kwargs.get('instance')
        if instance and instance.category not in existing_categories:
            existing_categories.append(instance.category)

        self.fields['category'] = forms.CharField(
            widget=forms.TextInput(attrs={'list': 'category-list'})
        )
        self.existing_categories = existing_categories
