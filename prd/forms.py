from django import forms
from .models import Category, Product, Staff, Sale
# forms.py
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit




class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price','first_quantity','customer_name', 'quantity_available','is_loan']

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['user','first_name','email','phone_num','national_id' ,'position', 'profile_picture']

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product','customer_name','staff','partial_amount_paid','quantity_sold','sold_amount','is_loan']
from .models import Credit
class CreditForm(forms.ModelForm):
    class Meta:
        model = Credit
        fields = '__all__'

# forms.py
from django import forms
from .models import Payment

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount_paid']

        
from django import forms
from .models import Salary, BossExpense, Expense

class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = '__all__'

class BossExpenseForm(forms.ModelForm):
    class Meta:
        model = BossExpense
        fields = '__all__'

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = '__all__'
from .models import Salary_Payment

class SalaryPayForm(forms.ModelForm):
    class Meta:
        model = Salary_Payment
        fields = ['amount_paid']
from .models import qrsho_Payment


from .models import qrsho_Payment

class qrshoForm(forms.ModelForm):
    class Meta:
        model = qrsho_Payment
        fields = ['amount_paid']

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, label='Search')

