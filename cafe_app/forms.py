from django import forms

from .models import CafeItem, CafePurchase, CafeTable, Expenses, Staff


class CafeTableForm(forms.ModelForm):
    class Meta:
        model = CafeTable
        fields = ['table_name', 'table_type', 'status']


class CafeItemForm(forms.ModelForm):
    class Meta:
        model = CafeItem
        fields = ['item_code', 'item_name', 'category', 'quantity', 'price']


class CafePurchaseForm(forms.ModelForm):
    class Meta:
        model = CafePurchase
        fields = ['item_code', 'item_name', 'category', 'quantity', 'purchase_price', 'selling_price']


class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['staff_id', 'staff_name', 'mobile_number', 'salary']


class ExpensesForm(forms.ModelForm):
    class Meta:
        model = Expenses
        fields = ['date', 'reason', 'staff_name', 'amt']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}
