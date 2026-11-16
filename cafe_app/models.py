from django.db import models

# Create your models here.

#user register

class UserRegister(models.Model):
    user_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=128)

#ADMIN REGISTER

from django.db import models


class AdminRegister(models.Model):
    name = models.CharField(max_length=100)
    admin_id = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=128)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.admin_id

#add table

from django.db import models


class CafeTable(models.Model):
    table_name = models.CharField(max_length=100, unique=True)
    table_type = models.CharField(
        max_length=20,
        choices=[
            ('A/C', 'A/C'),
            ('Non A/C', 'Non A/C'),
        ]
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('Available', 'Available'),
            ('Occupied', 'Occupied'),
        ],
        default='Available'
    )

    def __str__(self):
        return self.table_name

    class Meta:
        ordering = ['id']

#add items



from django.db import models


class CafeItem(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'Food'),
        ('alcohol', 'Alcohol'),
        ('soft_drink', 'Soft Drink'),
    ]

    item_code = models.CharField(max_length=50, unique=True)
    item_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    def __str__(self):
        return f"{self.item_code} - {self.item_name}"

    class Meta:
        ordering = ['id']

#ADD PURCHASE

from django.db import models


class CafePurchase(models.Model):

    CATEGORY_CHOICES = [
        ('food', 'Food'),
        ('alcohol', 'Alcohol'),
        ('soft_drink', 'Soft Drink'),
    ]

    item_code = models.CharField(max_length=50)
    item_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item_code} - {self.item_name}"

    class Meta:
        ordering = ['-purchase_date']

#add staff

from django.db import models


class Staff(models.Model):
    staff_id = models.CharField(max_length=20, unique=True)
    staff_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.staff_id} - {self.staff_name}"

    class Meta:
        ordering = ['staff_id']


class Expenses(models.Model):
    date = models.DateField()
    amt = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255)
    staff_name = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reason} - {self.amt}"

    class Meta:
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'
        ordering = ['-date', '-created_at']

#ItemOrder

from django.db import models


class ItemOrder(models.Model):
    user = models.ForeignKey(
        UserRegister,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='orders',
    )
    table_name = models.CharField(max_length=100, null=True, blank=True)
    bill_no = models.CharField(max_length=10, null=True, blank=True)
    bill_date = models.DateField()
    bill_time = models.TimeField(null=True, blank=True)

    item_code = models.CharField(max_length=50, null=True, blank=True)
    item_name = models.CharField(max_length=100, null=True, blank=True)

    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    gst = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        default=0
    )
    qty = models.IntegerField(default=1)

    tax_amt = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    total_gst = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    item_cat = models.CharField(max_length=50, null=True, blank=True)
    is_settled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.bill_no} - {self.item_name}"

# cafe_app/models.py

from django.db import models


class Printorders(models.Model):
    table_name = models.CharField(max_length=10, null=True, blank=True)
    bill_no = models.CharField(max_length=10, null=True, blank=True)
    bill_date = models.DateField()
    bill_time = models.TimeField(null=True, blank=True)
    item_code = models.CharField(max_length=10, null=True, blank=True)
    item_name = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    gst = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    qty = models.IntegerField(default=1)
    tax_amt = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    total_gst = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    item_cat = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Bill {self.bill_no} - Table {self.table_name}"
