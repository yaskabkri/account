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
