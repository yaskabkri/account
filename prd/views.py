from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse
from .models import Category, Product, Staff, Sale
from .forms import CategoryForm, ProductForm, StaffForm, SaleForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.contrib.auth.decorators import login_required

def home(request):
    form = SaleForm()
    if request.method=='POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            form.save()

    return render(request, 'prd/home.html',{'form':form})

def add_product(request):
    form = ProductForm()
    if request.method=='POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    return render(request, 'prd/add_p.html',{'form':form})        

def add_category(request):
    form = CategoryForm()
    if request.method=='POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    return render(request, 'prd/add_cat.html',{'form':form})        

@login_required
def add_sale(request):
    
    form = SaleForm()
    if request.method=='POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            if form['staff'] == request.user.staff.first_name:
                form.save()

            return redirect('home')
    return render(request, 'prd/add_sale.html',{'form':form})  
def add_staff(request):
    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('add_staff')  # Redirect to the same page after successful submission
    else:
        form = StaffForm()

    return render(request, 'prd/add_staff.html', {'form': form})

 
def list_user(request):
    
    staff_members = User.objects.all()
    return render(request, 'stf/list_user.html', {'staff_members': staff_members})    
def list_staff(request):
    salary = Salary.objects.all()
    staff_members = Staff.objects.all()
    return render(request, 'prd/staff_list.html', {'staff_members': staff_members,'salary':salary})    
from django.db.models import Count
from .models import Staff, Attendance
@login_required
def staff_detail(request, staff_id):
    staff = Staff.objects.get(pk=staff_id)
    sales = Sale.objects.filter(staff=staff)
    # Calculate absent days for each day in the current month
    today = timezone.now()
    first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month % 12 + 1) - timezone.timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)

    total_absent_days = Attendance.objects.filter(
        staff=staff,
        check_in_time__gte=first_day_of_month,
        check_out_time__lte=last_day_of_month
    ).exclude(check_in_time__isnull=False, check_out_time__isnull=False).values('check_in_time__date').distinct().count()
    total_attendance_days = Attendance.objects.filter(
        staff=staff,
        check_in_time__gte=first_day_of_month,
        check_out_time__lte=last_day_of_month,
        check_in_time__isnull=False,
        check_out_time__isnull=False
    ).values('check_in_time__date').distinct().count()
    return render(request, 'prd/staff_detail.html', {'total_attendance_days':total_attendance_days,'staff': staff, 'total_absent_days': total_absent_days, 'sales':sales})



import matplotlib.pyplot as plt
from io import BytesIO
import base64
from .models import Sale

def plot_cumulative_sales(request):
    all_sales = Sale.objects.all().order_by('sale_date')

    # Extracting sales data for plotting
    sale_dates = [sale.sale_date for sale in all_sales]
    cumulative_quantities_sold = [sum(sale.quantity_sold for sale in all_sales if sale.sale_date <= date) for date in sale_dates]

    # Plotting the cumulative sales data
    plt.figure(figsize=(10, 10))
    plt.plot(sale_dates, cumulative_quantities_sold, marker='o')
    plt.title('Cumulative Sales Over Time')
    plt.xlabel('Sale Date')
    plt.ylabel('Cumulative Quantity Sold')

    # Saving the plot to a BytesIO object
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    plt.close()

    # Embedding the plot in the HTML template
    img_str = base64.b64encode(img_buffer.read()).decode('utf-8')
    img_src = f'data:image/png;base64,{img_str}'

    context = {
        'img_src': img_src,
    }

    return render(request, 'prd/plot.html', context)

def list_sales(request):
    sales = Sale.objects.filter(is_loan=False)
    
    
    return render(request, 'prd/list_sale.html',{'sales':sales})

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import  Attendance
@login_required
def mark_check_in(request, staff_id):
    staff = Staff.objects.get(pk=staff_id)

    # Check if there's an existing attendance record for today
    today_attendance = Attendance.objects.filter(staff=staff, check_in_time__date=timezone.now().date()).first()

    if today_attendance:
        return HttpResponse("Check-in already marked for today.")

    # Create a new attendance record for today and mark check-in time
    Attendance.objects.create(staff=staff, check_in_time=timezone.now())
    return HttpResponse(f"Check-in marked for {staff.first_name} {staff.last_name}.")
@login_required
def mark_check_out(request, staff_id):
    staff = Staff.objects.get(pk=staff_id)

    # Retrieve the latest attendance record for today
    today_attendance = Attendance.objects.filter(staff=staff, check_in_time__date=timezone.now().date()).last()

    if not today_attendance or today_attendance.check_out_time:
        return HttpResponse("No valid check-in or check-out record found.")

    # Mark check-out time
    today_attendance.mark_check_out()
    return HttpResponse(f"Check-out marked for {staff.first_name} {staff.last_name}.")
@login_required
def view_attendance(request):
    # Retrieve all staff members and their attendance records for today
    staff_members = Staff.objects.all()
    today_attendance = [
        {'staff': staff, 'attendance': Attendance.objects.filter(staff=staff, check_in_time__date=timezone.now().date()).last()}
        for staff in staff_members
    ]

    return render(request, 'prd/view_attendance.html', {'today_attendance': today_attendance})





def mark_user_attendance(request):
    # Assuming you're using Django's built-in User model
    user = request.user

    # Check if there's an existing attendance record for today
    today_attendance = Attendance.objects.filter(staff__user=user, check_in_time__date=timezone.now().date()).first()

    if today_attendance:
        return HttpResponse("Check-in already marked for today.")

    # Create a new attendance record for today and mark check-in time
    staff = get_object_or_404(Staff, user=user)
    Attendance.objects.create(staff=staff, check_in_time=timezone.now())

    return HttpResponse(f"Check-in marked for {user.username}.")


from .models import Credit
from .forms import CreditForm

def credit_list(request):
    credits = Credit.objects.all()
    loans_with_credit = Credit.objects.select_related('sale').filter(sale__is_loan=True)

    return render(request, 'prd/credit_list.html', {'loans_with_credit': loans_with_credit,'credits':credits})

def update_sale(request, pk):
    sale = Sale.objects.get(pk=pk)
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to the sale list view
    else:
        form = SaleForm(instance=sale)
    return render(request, 'prd/update_sale.html', {'form': form, 'sale': sale})


def update_credit(request, pk):
    credits = Credit.objects.get(pk=pk)
    if request.method == 'POST':
        form = CreditForm(request.POST, instance=credits)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to the sale list view
    else:
        form = CreditForm(instance=credits)
    return render(request, 'prd/update_credit.html', {'form': form, 'credits': credits})
from django.shortcuts import render, redirect
from .models import Credit, Payment
from .forms import PaymentForm

def add_payment(request, credit_id):
    credit = Credit.objects.get(pk=credit_id)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            amount_paid = form.cleaned_data['amount_paid']
            payment = Payment.objects.create(credit=credit, amount_paid=amount_paid)
            return redirect('credit_list')
    else:
        form = PaymentForm()

    return render(request, 'prd/add_payment.html', {'form': form, 'credit': credit})



from django.shortcuts import render, redirect, get_object_or_404
from .models import Salary, BossExpense, Expense, Salary_Payment
from .forms import SalaryForm, BossExpenseForm, ExpenseForm, SalaryPayForm

def create_salary(request):
    if request.method == 'POST':
        form = SalaryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('salary-list')
    else:
        form = SalaryForm()
    return render(request, 'prd/create_update.html', {'form': form})
def create_salpay(request):
    if request.method == 'POST':
        form = SalaryPayForm(request.POST)
        if form.is_valid():
           form.save()
           return redirect('home')
    else:
        form = SalaryPayForm()

    return render(request, 'prd/salary_pay.html', {'form': form})

def Salary_Pay(request, salary_id):
    salary = Salary.objects.get(pk=salary_id)

    if request.method == 'POST':
        form = SalaryPayForm(request.POST)
        if form.is_valid():
            amount_paid = form.cleaned_data['amount_paid']
            payment = Salary_Payment.objects.create(salary=salary, amount_paid=amount_paid)
            return redirect('home')
    else:
        form = SalaryPayForm()

    return render(request, 'prd/salary_pay.html', {'form': form, 'salary': salary})
from .models import Salary, Salary_Payment

# Assuming you have a staff member instance named 'staff_member'
from .models import Salary, Salary_Payment

def list_staff_payments(staff_member):
    # Get all payments related to the staff member
    staff_payments = Salary_Payment.objects.filter(salary__staff=staff_member)
    return staff_payments
from django.shortcuts import render, get_object_or_404
from .models import Salary, Salary_Payment
from django.db.models import Sum

def staff_payments_view(request, salary_id):
    # Get the salary object based on the salary_id
    salary = get_object_or_404(Salary, id=salary_id)
    
    # Get all payments related to the salary
    staff_payments = Salary_Payment.objects.filter(salary=salary)
    total_amount_paid = staff_payments.aggregate(total_amount=Sum('amount_paid'))['total_amount']

    context = {
        'staff_payments': staff_payments,
        'total_amount_paid': total_amount_paid
    }
    
    

    return render(request, 'prd/staff_payments.html', context)

def create_boss_expense(request):
    if request.method == 'POST':
        form = BossExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('boss_list')
    else:
        form = BossExpenseForm()
    return render(request, 'prd/create_update.html', {'form': form})

def create_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('expense-list')
    else:
        form = ExpenseForm()
    return render(request, 'prd/create_update.html', {'form': form})

def salary_list(request):
    salaries = Salary.objects.all()
    return render(request, 'prd/salary_list.html', {'salaries': salaries})

def boss_expense_list(request):
    boss_expenses = BossExpense.objects.all()
    return render(request, 'prd/boss_ex.html', {'boss_expenses': boss_expenses})

def expense_list(request):
    expenses = Expense.objects.all()
    return render(request, 'expense_list.html', {'expenses': expenses})

def update_salary(request, pk):
    salary = get_object_or_404(Salary, pk=pk)
    form = SalaryForm(request.POST or None, instance=salary)
    if form.is_valid():
        form.save()
        return redirect('salary-list')
    return render(request, 'create_salary.html', {'form': form})

def update_boss_expense(request, pk):
    boss_expense = get_object_or_404(BossExpense, pk=pk)
    form = BossExpenseForm(request.POST or None, instance=boss_expense)
    if form.is_valid():
        form.save()
        return redirect('boss-expense-list')
    return render(request, 'create_boss_expense.html', {'form': form})

def update_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    form = ExpenseForm(request.POST or None, instance=expense)
    if form.is_valid():
        form.save()
        return redirect('expense-list')
    return render(request, 'create_expense.html', {'form': form})




def credit_detail(request,credit_id):
    c_detail = Credit.objects.filter(pk=credit_id)
    return render(request,'prd/c_detail.html',{'c_detail':c_detail})

from .forms import SearchForm 
from .models import Search




def search_view(request):
    query = request.GET.get('q')
    if query:
        # Perform search across multiple models
        staff = Staff.objects.filter(first_name__icontains=query)
        products = Product.objects.filter(name__icontains=query)
        sale = Sale.objects.filter( sold_amount__icontains=query)
        sale = Sale.objects.filter(customer_name__icontains=query)
        context = {
            'staff': Staff,
            'products': products,
            'sale': sale,
            'query': query,
            'sale':sale,
        }
        return render(request, 'prd/search.html', context)
    else:
        return render(request, 'prd/search_form.html')
    
def credit_payments_view(request, credit_id):
    # Get the salary object based on the salary_id
    credit = get_object_or_404(Credit, id=credit_id)
    
    # Get all payments related to the salary
    credit_payments = Payment.objects.filter(credit=credit)
    total_amount_paid = credit_payments.aggregate(total_amount=Sum('amount_paid'))['total_amount']

    context = {
        'credit_payments': credit_payments,
        'total_amount_paid': total_amount_paid
    }


    return render(request, 'prd/crd_detail.html', context)