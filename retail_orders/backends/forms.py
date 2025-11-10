from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    """
    Класс для загрузки изображения
    """
    class Meta:
        model = Product
        fields = ['name', 'image']