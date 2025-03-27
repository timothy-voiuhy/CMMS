from django import forms
from .models import InventoryItem

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = [
            'name', 'description', 'category', 'quantity', 
            'minimum_quantity', 'reorder_point', 'unit', 
            'unit_cost', 'location', 'supplier'
        ]
        # Adjust these fields based on your actual model
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        } 