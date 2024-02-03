from django.urls import path
from .views import  (home, add_product, add_category, add_sale,add_staff,
                    list_staff,list_user,view_attendance,mark_check_in,
                    mark_check_out,staff_detail , plot_cumulative_sales,
                    mark_user_attendance,
                    list_sales,credit_list, update_sale, update_credit,add_payment,
                    credit_detail,create_boss_expense,create_salary, salary_list,Salary_Pay,
                    boss_expense_list,search_view, staff_payments_view,credit_payments_view)
from staf import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home,name='home'),

    path('add_p/', add_product, name='add_p'),
    path('add_cat/', add_category, name='add_cat'),
   
    path('add_sale/', add_sale, name='add_sale'),
    path('add_staff/', add_staff, name='add_staff'),
    path('list_staff/', list_staff, name='list_staff'),
    path('list_user/', list_user, name='list_user'),
    path('staff_detail/<int:staff_id>/', staff_detail, name='staff_detail'),
    path('plot_cumulative_sales/', plot_cumulative_sales, name='plot_cumulative_sales'),
    path('list_sale/', list_sales, name='list_sale'),
    #path('view_loans/', view_loans, name='view_loans'),
    #path('view_credits/', view_credits, name='view_credits'),
    #path('sale_credit/', sale_credit, name='sale_credit'),
    path('mark_check_in/<int:staff_id>/', mark_check_in, name='mark_check_in'),
    path('mark_check_out/<int:staff_id>/', mark_check_out, name='mark_check_out'),
    path('view_attendance/', view_attendance, name='view_attendance'),
    path('mark_user_attendance/', mark_user_attendance, name='mark_user_attendance'),
    path('credits/', credit_list, name='credit_list'),
    path('update_credit/<int:pk>/', update_credit, name='update_credit'),
    path('update-sale/<int:pk>/', update_sale, name='update-sale'),
    path('add-payment/<int:credit_id>/', add_payment, name='add-payment'),
    path('c_detail/<int:credit_id>/', credit_detail, name='c_detail'),
    path('mark_user_attendance/', mark_user_attendance, name='boss_ex'),
    path('boss_ex/',create_boss_expense, name='boss_ex'),
    path('boss_list/',boss_expense_list, name='boss_list'),
    path('create_salary/',create_salary, name='create_salary'),
    path('salary_list/',salary_list, name='salary_list'),
    path('stf_sal_list/<int:salary_id>/',staff_payments_view, name='stf_sal_list'),
    path('salary_pay/<int:salary_id>/', Salary_Pay, name='salary_pay'),
    path('crd_sal_list/<int:credit_id>/',credit_payments_view, name='crd_sal_list'),
    path('search/',search_view, name='search_view'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('list_product/', views.list_product, name='list_product'),
    path('sales/<str:date>/',views.daily_sales_view, name='daily_sales'),
    path('date_sale/', views.sales_dates_view, name='date_sale'),
    path('prod_loan/', views.list_pro_loan, name='prod_loan'),
    path('pay_qrsho/<int:product_id>', views.pay_qrsho, name='pay_qrsho'),
    path('list_qrsho/<int:product_id>', views.list_qrsho_pay, name='list_qrsho'),
    
    #path('create_credit_sale/', create_credit_sale, name='create_credit_sale'),
     #path('credit_sales_list/', list_credit_sales, name='credit_sales_list'),
    # Add
    # Add other URLs as needed
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




