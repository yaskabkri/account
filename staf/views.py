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


from django.shortcuts import render
from prd.models import Product, Salary, Staff, Sale, Payment, Salary_Payment
from django.db import models

from django.shortcuts import render
from prd.models import Product, Salary, Staff, Sale
from django.utils import timezone
from datetime import datetime, timedelta

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
    products = Product.objects.all()
    prc_loan = sum(pro.price for pro in products if pro.is_loan)
    qua_loan = sum(pro.first_quantity for pro in products if pro.is_loan)
    total_product_loan = prc_loan * qua_loan
    salaries = Salary_Payment.objects.filter(payment_date__range=[start_date, end_date])
    payments = Payment.objects.filter(payment_date__range=[start_date, end_date])
    total_payment = sum(pay.amount_paid for pay in payments)
    #total_salaries =  sum(pay.withdraw_salary for pay in salaries)
    #total_salary_paid = sum(pay.payment_amount for pay in salaries)
    total_salary_paid = Salary_Payment.objects.aggregate(total_paid=models.Sum('amount_paid'))['total_paid'] or 0




    # Prepare the context to pass to the template
    context = {
        'products': products,
        'sales': sales,
        'salaries': salaries,
        'total_sales_amount': total_sales_amount,
        'total_sold_qua': total_sold_qua,
        'total_sale_credit': total_sale_credit,
        'total_product_loan': total_product_loan,
        'timeframe': timeframe,
        'start_date': start_date,
        'end_date': end_date,
        'total_payment':total_payment,
        'total_salary_paid ': total_salary_paid ,
    }

    return render(request, 'prd/total.html', context)


from django.shortcuts import render
from datetime import datetime, date, timedelta
from prd.models import Salary, Salary_Payment

def total_salary_paid_day(request):
    # Get today's date
    today = datetime.today().date()

    # Calculate total salary paid for today
    total_salary_paid_today = Salary_Payment.objects.filter(payment_date__date=today).aggregate(total=Sum('amount_paid'))['total']
    total_salary_paid_today = total_salary_paid_today or 0

    # Render the HTML template with the calculated data
    return render(request, 'prd/total_salary_paid.html', {'total_salary_paid_today': total_salary_paid_today})

def total_salary_paid_month(request):
    # Get the year and month for the current date
    year = datetime.today().year
    month = datetime.today().month

    # Calculate total salary paid for the current month
    start_date = date(year, month, 1)
    end_date = start_date.replace(day=1, month=1) - timedelta(days=1)
    total_salary_paid_month = Salary_Payment.objects.filter(payment_date__date__range=[start_date, end_date]).aggregate(total=Sum('amount_paid'))['total']
    total_salary_paid_month = total_salary_paid_month or 0

    # Render the HTML template with the calculated data
    return render(request, 'prd/total_salary_paid.html', {'total_salary_paid_month': total_salary_paid_month})


from django.shortcuts import render
from prd.models import Salary
from datetime import date, timedelta

def total_withdrawal_day(request, year, month, day):
    # Create a date object for the specified day
    target_date = date(year, month, day)

    # Filter Salary instances for the specified day and calculate total withdrawal
    total_withdrawal_day = Salary.objects.filter(date=target_date).aggregate(total=Sum('deductions'))['total']
    total_withdrawal_day = total_withdrawal_day or 0

    # Render the HTML template with the calculated total withdrawal for the day
    return render(request, 'prd/withdrawal_day.html', {'total_withdrawal_day': total_withdrawal_day, 'target_date': target_date})

def total_withdrawal_month(request, year, month):
    # Calculate the start and end dates for the specified month
    start_date = date(year, month, 1)
    end_date = start_date.replace(day=1, months=1) - timedelta(days=1)

    # Filter Salary instances for the specified month and calculate total withdrawal
    total_withdrawal_month = Salary.objects.filter(date__range=[start_date, end_date]).aggregate(total=Sum('deductions'))['total']
    total_withdrawal_month = total_withdrawal_month or 0

    # Render the HTML template with the calculated total withdrawal for the month
    return render(request, 'prd/withdraw_month.html', {'total_withdrawal_month': total_withdrawal_month, 'start_date': start_date, 'end_date': end_date})
