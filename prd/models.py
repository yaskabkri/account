from django.db import models
from PIL import Image
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    first_quantity = models.PositiveIntegerField(default=0)
    quantity_available = models.PositiveIntegerField(default=0)
    customer_name = models.CharField(max_length=255, blank=True)
    is_loan = models.BooleanField(default=False)
    def __str__(self):
        return f'{self.name}'
    def total_qrsho(self):
        return self.price * self.first_quantity
    def total_paid(self):
        return sum(payment.amount_paid for payment in self.qrsho_payment_set.all())

    
    
        


class qrsho_Payment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
         return f'{self.id}, {self.amount_paid}'
    def remaining_balance(self):
        return self.total_qrsho - self.amount_paid
@receiver(post_save, sender=Product)
def create_product_if_loan(sender, instance, created, **kwargs):
    """
    Create a new Product instance if is_loan is True.
    """
    if created and instance.is_loan:
        Product.objects.create(
            name=instance.name,
            category=instance.category,
            description=instance.description,
            price=instance.price,
            first_quantity=instance.first_quantity,
            quantity_available=instance.quantity_available,
            customer_name=instance.customer_name,
            is_loan=False  # Set is_loan to False for the newly created instance
        )


class Staff(models.Model):
    SHOP = 'Shop'
    STORE = 'Store'

    LOCATION_CHOICES = [
        (SHOP, 'Shop'),
        (STORE, 'Store'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    salary = models.PositiveIntegerField(default=0)
    position = models.CharField(
        max_length=5,
        choices=LOCATION_CHOICES,
        default=SHOP,
    )
    phone_num = models.CharField(max_length=10, null=True)
    national_id = models.CharField(max_length=10, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='staff_profile_pics/', blank=True, null=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

from django.db import models
from django.core.exceptions import ValidationError
from .models import Product, Staff
class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    quantity_sold = models.PositiveIntegerField()
    partial_amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sale_date = models.DateField(default=timezone.now)
    sold_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    customer_name = models.CharField(max_length=50, null=True,blank=True)
    is_loan = models.BooleanField(default=False)
    @property
    def remaining_amount(self):
        return self.sold_amount - self.partial_amount_paid
    
    

    def mark_partial_payment(self, amount_paid):
        if amount_paid <= self.remaining_amount:
            self.partial_amount_paid += amount_paid
            self.save()
            return True
        return False
    def save(self, *args, **kwargs):
        # Validate the quantity sold
        if self.quantity_sold > self.product.quantity_available:
            raise ValidationError("Quantity sold cannot exceed available quantity.")

        # Calculate and set the sold_amount before saving
        
        # Decrement the available quantity of the product
        self.product.quantity_available -= self.quantity_sold
        self.product.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale ID: {self.id}, Product: {self.product.name}, Quantity Sold: {self.quantity_sold},{self.partial_amount_paid}, Sale Date: {self.sale_date}, Is Loan: {self.is_loan}"

from django.db.models.signals import post_save
from django.dispatch import receiver

class Credit(models.Model):
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    

    def __str__(self):
        return f"Credit ID: {self.id}, Sale ID: {self.sale.id}, Amount: {self.amount}"
    def total_paid(self):
        return sum(payment.amount_paid for payment in self.payment_set.all())

    def remaining_balance(self):
        return self.amount - self.total_paid()- self.sale.partial_amount_paid


    @receiver(post_save, sender=Sale)
    def create_credit(sender, instance, created, **kwargs):
        if created and instance.is_loan:
            Credit.objects.create(sale=instance, amount=instance.sold_amount)

class Payment(models.Model):
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"Payment ID: {self.id}, Credit ID: {self.credit.id}, Amount Paid: {self.amount_paid}, Payment Date: {self.payment_date}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.credit.save()  # Update the credit's remaining balance after saving the payment


# models.py
        

class Salary(models.Model):
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE,related_name='staff', default=None)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)

    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField(default=timezone.now)
    def __str__(self):
        return f"{self.id} ,{self.staff},  {self.basic_salary}, {self.deductions}, {self.bonuses}"
    def total_paid(self):
        return sum(payment.amount_paid for payment in self.salary_payment_set.all())

    def remaining_balance(self):
        return self.basic_salary - self.total_paid()

    def withdraw_salary(self, amount):
        remaining_salary = self.basic_salary - self.deductions - self.bonuses
        if amount <= remaining_salary:
            self.deductions += amount
            self.save()
            return True
        else:
            return False
class Salary_Payment(models.Model):
    salary = models.ForeignKey(Salary, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"Payment ID: {self.id}, Credit ID: {self.salary.id}, Amount Paid: {self.amount_paid}, Payment Date: {self.payment_date}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.salary.save()  # Up

class BossExpense(models.Model):
    SHOP_EXPENSE = 'shop'
    Family_EXPENSE = 'family'
    Enter_Tr_EXPENSE = 'enter_tr'

    CATEGORY_CHOICES = [
        (SHOP_EXPENSE, 'Shop Expense'),
        (Family_EXPENSE, 'Boss Expense'),
        (Enter_Tr_EXPENSE , 'entertainment'),
    ]

    boss_ex = models.CharField(max_length=255, choices=CATEGORY_CHOICES,default=SHOP_EXPENSE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.boss.name}'s Expense - {self.description}"
    
class Expense(models.Model):

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()

    def __str__(self):
        return self.name

from django.utils import timezone
class Attendance(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)

    def mark_check_in(self):
        self.check_in_time = timezone.now()
        self.save()

    def mark_check_out(self):
        self.check_out_time = timezone.now()
        self.save()

    def is_absent(self):
        return self.check_in_time is None or self.check_out_time is None
# models.py



class Search(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.query}"
