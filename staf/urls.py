from django.urls import path
from .views import (register, user_login, user_logout, list_product,
                    daily_sales_view, sales_dates_view, list_pro_loan,
                    pay_qrsho,qrsho_payments_view,list_qrsho_pay, total,total_salary_paid_day,total_salary_paid_month)

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('list_product/', list_product, name='list_product'),
    path('sales/<str:date>/',daily_sales_view, name='daily_sales'),
    path('date_sale/', sales_dates_view, name='date_sale'),
    path('prod_loan/', list_pro_loan, name='prod_loan'),
    path('pay_qrsho/<int:product_id>', pay_qrsho, name='pay_qrsho'),
    path('list_qrsho/<int:product_id>', list_qrsho_pay, name='list_qrsho'),
    path('total/', total, name='total'),
    path('sal_dy/', total_salary_paid_day, name='totl-sal-day'),
    path('sal_mnth/', total_salary_paid_month, name='totl-sal-mnth'),

]
