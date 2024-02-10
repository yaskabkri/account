from django.shortcuts import render, get_object_or_404

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the user after registration
            return redirect('home')  # Replace 'home' with the desired redirect path
    else:
        form = UserCreationForm()

    return render(request, 'prd/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid login credentials. Please try again.')

    return render(request, 'prd/login.html')

def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('register')
from prd.models import Product,Sale
def list_product(request):
    prod = Product.objects.all()
    sale = Sale.objects.all()
    return render(request, 'prd/all.html',{'prod':prod,'sale':sale})

# views.py

from django.utils import timezone
from prd.models import Sale, Product

def daily_sales_view(request, date):
    # Convert the date string to a datetime object
    date = timezone.datetime.strptime(date, "%Y-%m-%d").date()

    # Filter sales for the specified date
    daily_sales = Sale.objects.filter(sale_date=date)

    context = {
        'date': date,
        'daily_sales': daily_sales,
    }

    return render(request, 'prd/daily_sales.html', context)

def list_pro_loan(request):
    prod = Product.objects.filter(is_loan=True)
    return render(request, 'prd/pro_loan.html', {'prod':prod})
   
from prd.models import qrsho_Payment
from prd.forms import qrshoForm


def pay_qrsho(request, product_id):
    product = Product.objects.get(id=product_id)
    form = qrshoForm()
    if request.method=='POST':
        form = qrshoForm(request.POST)
        if form.is_valid():
            amount_paid = form.cleaned_data['amount_paid']
            payment = qrsho_Payment.objects.create(product=product, amount_paid=amount_paid)
            return redirect('home')
    else:
        form = qrshoForm()

    return render(request, 'prd/qrsho_pay.html', {'form': form, 'salary': product})

from django.db.models import Sum



from django.shortcuts import render, get_object_or_404


def qrsho_payments_view(request, product_id):
    # Retrieve the product instance or return a 404 error if not found
    product = get_object_or_404(Product, pk=product_id)

    # Calculate total paid amount and remaining balance
    total_paid = product.total_paid()
    remaining_balance = product.remaining_balance()

    context = {
        'product': product,
        'total_paid': total_paid,
        'remaining_balance': remaining_balance,
    }

    

    return render(request, 'prd/qrsho_payments.html', context)
def list_qrsho_detals(request, qrsho_Payment_id):
    payment = get_object_or_404(qrsho_Payment,qrsho_Payment_id)
    return render(request, 'prd/list_qrsho_pay.html',{'payment':payment})

def list_qrsho_pay(request, product_id):
    # Retrieve the product instance or return a 404 error if not found
    product = Product.objects.get(pk=product_id)

    # Query all payments related to the specific product
    product_payments = qrsho_Payment.objects.filter(product=product)

    context = {
        'product': product,
        'product_payments': product_payments,
    }

    

    return render(request, 'prd/list_qrsho_pay.html', context)
    
def sales_dates_view(request):
    # Get unique dates for which sales exist
    sales_dates = Sale.objects.dates('sale_date', 'day', order='DESC')

    context = {
        'sales_dates': sales_dates,
    }

    return render(request, 'prd/sales_dates.html', context)


from django.shortcuts import render
from prd.models import Product, Salary, Staff, Sale, Payment, Salary_Payment
from django.db import models

from django.shortcuts import render
from prd.models import Product, Salary, Staff, Sale
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import F, ExpressionWrapper, DecimalField

def total(request):
    # Default values
    timeframe = request.GET.get('timeframe', 'day')  # Default to 'day' if no timeframe is provided
    today = timezone.now()
    start_date = end_date = today

    # Determine the start and end dates based on the selected timeframe
    if timeframe == 'months':
        start_date = today.replace(day=1)  # First day of the current month
        end_date = start_date.replace(day=1, months=1) - timedelta(days=1)  # Last day of the current month

    # Filter Sale objects based on the selected timeframe
    sales = Sale.objects.filter(sale_date__range=[start_date, end_date])

    # Calculate the total sale amount
    total_sales_amount = sum(sale.sold_amount for sale in sales)
    total_sold_qua = sum(sale.quantity_sold for sale in sales)
    total_sale_credit = sum(sale.sold_amount for sale in sales if sale.is_loan)

    # Fetch other necessary data
    product = Product.objects.all()
    prc_loan = sum(pro.price for pro in product if pro.is_loan)
    qua_loan = sum(pro.first_quantity for pro in product if pro.is_loan)
    
    
    #total_product_loan = prc_loan 
    total_loan_price = Product.objects.filter(is_loan=True).aggregate(total_loan_price=Sum('price'))['total_loan_price'] or 0
    
    # Calculate total price of products where is_loan is False
    total_non_loan_price = Product.objects.filter(is_loan=False).aggregate(total_non_loan_price=Sum('price'))['total_non_loan_price'] or 0

    salaries = Salary_Payment.objects.filter(payment_date__range=[start_date, end_date])
    payments = Payment.objects.filter(payment_date__range=[start_date, end_date])
    total_payment = sum(pay.amount_paid for pay in payments)
    #total_salaries =  sum(pay.withdraw_salary for pay in salaries)
    #total_salary_paid = sum(pay.payment_amount for pay in salaries)
    total_salary_paid = Salary_Payment.objects.aggregate(total_paid=models.Sum('amount_paid'))['total_paid'] or 0
    products = Product.objects.annotate(
        total_price=ExpressionWrapper(
            F('price') * F('first_quantity'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    )

    # Calculate total price of all products
    total_price_all_products = sum(product.total_price for product in products)

    context = {
        
    }



    # Prepare the context to pass to the template
    context = {
        'products': products,
        'total_price_all_products': total_price_all_products,
        
        'sales': sales,
        'salaries': salaries,
        'total_sales_amount': total_sales_amount,
        'total_sold_qua': total_sold_qua,
        'total_sale_credit': total_sale_credit,
        #'total_product_loan': total_product_loan,
        'total_loan_prise':total_loan_price,
        'total_non__loan_price':total_non_loan_price,
        'timeframe': timeframe,
        'start_date': start_date,
        'end_date': end_date,
        'total_payment':total_payment,
        'total_salary_paid ': total_salary_paid ,
    }

    return render(request, 'prd/total.html', context)


from django.db.models import F, ExpressionWrapper, DecimalField, Sum
from django.shortcuts import render

def tot(request):
    # Calculate total price of each product
    products = Product.objects.annotate(
        total_price=ExpressionWrapper(
            F('price') * F('first_quantity'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    )

    # Calculate total price of all products
    total_price_all_products = sum(product.total_price for product in products if product.is_loan==False)

    # Calculate total price of products where is_loan is True
    total_price_loan_products = Product.objects.filter(is_loan=True).aggregate(
        total_loan_price=Sum(F('price') * F('first_quantity'), output_field=DecimalField(max_digits=10, decimal_places=2))
    )['total_loan_price'] or 0

    context = {
        'products': products,
        'total_price_all_products': total_price_all_products,
        'total_price_loan_products': total_price_loan_products,
    }
    return render(request, 'prd/kk.html', context)
