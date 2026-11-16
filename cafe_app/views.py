from django.shortcuts import render, get_object_or_404
from datetime import date
from functools import wraps

# Create your views here.

from django.shortcuts import render


def admin_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        admin_id = request.session.get('admin_id')
        if not admin_id or not AdminRegister.objects.filter(admin_id=admin_id).exists():
            messages.error(request, 'Please log in as an administrator to continue.')
            return redirect('admin_login')
        return view(request, *args, **kwargs)
    return wrapped


def home(request):
    return render(request, 'cafe_app/home.html')

def userregister(request):
    return render(request, 'cafe_app/userregister.html')

def userlogin(request):
    if request.session.get("user_id"):
        return redirect("user_home")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        password = request.POST.get("password", "").strip()

        if not name or not password:
            messages.error(request, "Enter your name and password.")
        else:
            # Names are not unique, so check each matching account until the
            # submitted password matches one of them.
            for user in UserRegister.objects.filter(user_name__iexact=name):
                if check_password(password, user.password):
                    request.session.flush()
                    request.session["user_id"] = user.id
                    request.session["user_name"] = user.user_name
                    request.session.set_expiry(60 * 60 * 24 * 14)
                    return redirect("user_home")

            messages.error(request, "Invalid name or password.")

    return render(request, 'cafe_app/userlogin.html')

def admin_register(request):
    return render(request, 'cafe_app/admin_register.html')

def admin_login(request):
    return render(request, 'cafe_app/admin_login.html')

def about(request):
    return render(request, 'cafe_app/about.html')


MENU_CATALOG = [
    # Keep the replacement drink listing separate from the existing coffee inventory code.
    ('101', 'Tea and Coffee', '1coffee.jpg', 30, 5),
    ('102', 'Thali', 'thalinew.jpg', 150, 15),
    ('103', 'Vada', 'vadanew.jpg', 50, 5),
    ('104', 'Fried Rice', '1friedricee.jpg', 100, 10),
    ('105', 'Idli', '1idli.jpg', 35, 5),
    ('106', 'Jeera Rice', '1jeerarice.jpg', 100, 10),
    ('107', 'Gobi Manchuri', '1gobi.jpg', 100, 10),
    ('108', 'Masala Rice', '1masala rice.jpg', 90, 10),
    ('109', 'Paneer Rice', '1paneerrice.jpg', 100, 10),
    ('110', 'Tandoori', '1tandoori.jpg', 20, 10),
    ('111', 'Paneer Masala', '1paneer.jpg', 90, 10),
    ('112', 'Khaju Masala', '1khaju.jpeg', 90, 10),
    ('113', 'Puri', '1puri.jpg', 60, 10),
    ('114', 'Puri Thali', '1purithali.jpg', 100, 15),
    ('115', 'Thali', 'thali.jpg', 150, 15),
    ('116', 'Samosa', 'samosa.jpg', 50, 5),
    ('117', 'Noodles', 'noodle.jpg', 50, 10),
    ('118', 'Pizza', '1pizza.jpg', 150, 10),
    ('119', 'Bisibele Bath', '1bisibele.jpeg', 60, 10),
    ('120', 'Mushroom Masala', '1masarum.jpg', 90, 5),
    ('121', 'Mirchi', '1mirchi.jpg', 30, 5),
    ('122', 'Mango Juice', '1mjuice.jpeg', 50, 5),
    ('123', 'Orange Juice', '1ojuice.jpg', 50, 5),
    ('124', 'Soda', '1soda.jpg', 30, 5),
    ('125', 'Ice Cream', '1ice1.jpeg', 50, 5),
    ('126', 'Cone Ice', '1ice2.jpeg', 30, 5),
    ('127', 'Cup Ice', '1ice3.jpg', 30, 5),
]


def _menu_context(request):
    """Combine the reference menu with live inventory without inventing stock."""
    database_items = list(CafeItem.objects.all())
    by_code = {item.item_code.casefold(): item for item in database_items}
    by_name = {}
    for item in database_items:
        by_name.setdefault(item.item_name.strip().casefold(), item)

    catalog = []
    represented_ids = set()
    for code, name, image, price, preparation_minutes in MENU_CATALOG:
        code_match = by_code.get(code.casefold())
        item = code_match
        # A menu code may have been assigned to a different item already. In
        # that case match by name, never present the conflicting item as food.
        if item and item.item_name.strip().casefold() != name.casefold():
            item = None
        if item is None:
            item = by_name.get(name.casefold())
        if item:
            represented_ids.add(item.pk)
        catalog.append({
            'code': item.item_code if item else code,
            'name': name,
            'image': image,
            'price': item.price if item else price,
            'preparation_minutes': preparation_minutes,
            'item': item,
            'code_conflict': code_match if code_match and item is None else None,
        })

    additional_items = [
        item for item in database_items
        if item.pk not in represented_ids
        and item.item_name.strip().casefold() != 'coffee'
    ]
    if request.session.get('admin_id'):
        menu_target = 'admin_home'
    elif request.session.get('user_id'):
        menu_target = 'user_home'
    else:
        menu_target = 'userlogin'
    return {
        'menu_catalog': catalog,
        'additional_items': additional_items,
        'menu_target': menu_target,
    }


def menu(request):
    return render(request, 'cafe_app/menu.html', _menu_context(request))


def offers(request):
    return render(request, 'cafe_app/offers.html')


def contact(request):
    return render(request, 'cafe_app/contact.html')

@admin_required
def admin_nav(request):
    return render(request, 'cafe_app/admin_nav.html')

@admin_required
def admin_home(request):
    tables = CafeTable.objects.all()
    open_orders = {}
    for item in ItemOrder.objects.filter(is_settled=False).exclude(
        bill_no__isnull=True
    ).order_by('-bill_date', '-bill_time', '-id'):
        order = open_orders.setdefault(item.bill_no, {
            'bill_no': item.bill_no,
            'table_name': item.table_name,
            'bill_date': item.bill_date,
            'total': Decimal('0.00'),
            'items': [],
        })
        order['total'] += item.total or Decimal('0.00')
        order['items'].append(item)
    return render(request, 'cafe_app/admin_home.html', {
        'tdata': tables,
        'open_orders': list(open_orders.values()),
    })

@admin_required
def add_table(request):
    context = {'msg': ''}
    if request.method == 'POST':
        table_name = request.POST.get('t1', '').strip()
        table_type = request.POST.get('t2', '').strip()

        if not table_name:
            context['msg'] = 'Please enter a table name.'
        elif table_type not in {'A/C', 'Non A/C'}:
            context['msg'] = 'Please select a valid table type.'
        elif CafeTable.objects.filter(table_name__iexact=table_name).exists():
            context['msg'] = 'A table with this name already exists.'
        else:
            CafeTable.objects.create(table_name=table_name, table_type=table_type)
            return redirect('admin_home')

    return render(request, 'cafe_app/add_table.html', context)

def add_items(request):
    return render(request, 'cafe_app/add_items.html')

def add_staff(request):
    return render(request, 'cafe_app/add_staff.html')

@admin_required
def add_expenses(request):
    context = {'expenses': Expenses.objects.all(), 'error': ''}
    if request.method == 'POST':
        date_value = request.POST.get('date', '').strip()
        amount = request.POST.get('amount', '').strip()
        reason = request.POST.get('reason', '').strip()
        staff_name = request.POST.get('staff_name', '').strip()
        try:
            expense_date = date.fromisoformat(date_value)
            amount_value = Decimal(amount)
            if not reason or not amount_value.is_finite() or amount_value <= 0:
                raise ValueError
            Expenses.objects.create(date=expense_date, amt=amount_value, reason=reason, staff_name=staff_name)
            return redirect('add_expenses')
        except (ValueError, InvalidOperation):
            context['error'] = 'Enter a valid date, reason, and amount greater than zero.'
    return render(request, 'cafe_app/add_expenses.html', context)


@admin_required
def view_expenses(request):
    expenses = Expenses.objects.all()
    return render(request, 'cafe_app/admin_records.html', {
        'title': 'Expenses', 'description': 'Recorded café expenses.',
        'headers': ['Date', 'Reason', 'Staff', 'Amount'],
        'rows': [[expense.date.strftime('%d %b %Y'), expense.reason, expense.staff_name or '—', expense.amt] for expense in expenses],
        'empty_message': 'No expenses have been recorded yet.',
        'action_url': 'add_expenses', 'action_label': 'Add expense',
        'records': expenses, 'section': 'expenses',
    })

@admin_required
def add_purchase(request):
    return render(request, 'cafe_app/add_purchase.html')

@admin_required
def exchange_tbl(request):
    return redirect(f"{reverse('admin_home')}#tables-panel")

@admin_required
def settle_table(request):
    return redirect(f"{reverse('admin_home')}#open-orders")

@admin_required
def checkTables(request):
    return redirect(f"{reverse('admin_home')}#tables-panel")

def user_home(request):
    user_id = request.session.get("user_id")
    if not user_id or not UserRegister.objects.filter(id=user_id).exists():
        request.session.pop("user_id", None)
        request.session.pop("user_name", None)
        messages.error(request, "Please log in to continue.")
        return redirect("userlogin")
    # Use the same live table records shown on the admin dashboard so any
    # tables added by an administrator are immediately available to users.
    tables = CafeTable.objects.all()
    return render(request, 'cafe_app/user_home.html', {'tdata': tables})


def userlogout(request):
    request.session.pop("user_id", None)
    request.session.pop("user_name", None)
    messages.success(request, "You have been logged out.")
    return redirect("home")

def user_nav(request):
    return render(request, 'cafe_app/user_nav.html')

def my_order(request):
    user_id = request.session.get("user_id")
    if not user_id or not UserRegister.objects.filter(id=user_id).exists():
        request.session.pop("user_id", None)
        request.session.pop("user_name", None)
        messages.error(request, "Please log in to view your orders.")
        return redirect("userlogin")

    lines = ItemOrder.objects.filter(user_id=user_id).order_by(
        '-bill_date', '-bill_time', '-id'
    )
    grouped = {}
    for line in lines:
        order = grouped.setdefault(line.bill_no, {
            'id': line.pk,
            'bill_no': line.bill_no,
            'created_at': line.bill_date,
            'items_summary': [],
            'total_amount': Decimal('0.00'),
            'is_settled': True,
        })
        order['items_summary'].append(f'{line.item_name} × {line.qty}')
        order['total_amount'] += line.total or Decimal('0.00')
        order['is_settled'] = order['is_settled'] and line.is_settled
    orders = list(grouped.values())
    for order in orders:
        order['items_summary'] = ', '.join(order['items_summary'])
        order['status'] = 'Settled' if order['is_settled'] else 'Preparing'
        order['payment_method'] = 'Pay at counter'
    paid_total = sum(
        (order['total_amount'] for order in orders if order['is_settled']),
        Decimal('0.00'),
    )
    return render(request, "cafe_app/my_order.html", {
        'orders': orders,
        'total_orders': len(orders),
        'active_orders': sum(not order['is_settled'] for order in orders),
        'total_spent': paid_total,
    })

# USER REGISTER


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password

from .models import UserRegister


def userregister(request):

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "").strip()

        # Check empty fields
        if not name or not phone or not password:

            messages.error(
                request,
                "Please fill in all fields."
            )

            return redirect("userregister")


        # Check mobile number
        if not phone.isdigit() or len(phone) != 10:

            messages.error(
                request,
                "Please enter a valid 10-digit mobile number."
            )

            return redirect("userregister")


        # Check password length
        if len(password) < 8:

            messages.error(
                request,
                "Password must contain at least 8 characters."
            )

            return redirect("userregister")


        # Check if mobile number already exists
        if UserRegister.objects.filter(
            mobile_number=phone
        ).exists():

            messages.error(
                request,
                "This mobile number is already registered."
            )

            return redirect("userregister")


        # Save user
        UserRegister.objects.create(

            user_name=name,

            mobile_number=phone,

            password=make_password(password)

        )


        # Success message
        messages.success(
            request,
            "Account created successfully! Please log in."
        )


        return redirect("userlogin")


    return render(
        request,
        "cafe_app/userregister.html"
    )


# ADMIN REGISTER

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password

from .models import AdminRegister


# ==========================================================
# ADMIN REGISTER
# ==========================================================

def admin_register(request):

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        admin_id = request.POST.get("admin_id", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # Check empty fields
        if not name or not admin_id or not password:

            messages.error(
                request,
                "Please fill in all required fields."
            )

            return redirect("admin_register")

        # Password length
        if len(password) < 8:

            messages.error(
                request,
                "Password must contain at least 8 characters."
            )

            return redirect("admin_register")

        # Confirm password
        if confirm_password and password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect("admin_register")

        # Check duplicate Admin ID
        if AdminRegister.objects.filter(
            admin_id=admin_id
        ).exists():

            messages.error(
                request,
                "This Admin ID already exists."
            )

            return redirect("admin_register")

        # Create admin
        admin = AdminRegister(
            name=name,
            admin_id=admin_id,
            password=make_password(password)
        )

        admin.save()

        messages.success(
            request,
            "Admin account created successfully. Please login."
        )

        return redirect("admin_login")

    return render(
        request,
        "cafe_app/admin_register.html"
    )


# ==========================================================
# ADMIN LOGIN
# ==========================================================

def admin_login(request):

    if request.method == "POST":

        # IMPORTANT:
        # Login uses admin_id, NOT name
        admin_id = request.POST.get(
            "admin_id",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        # Check empty fields
        if not admin_id or not password:

            messages.error(
                request,
                "Please enter Admin ID and password."
            )

            return redirect("admin_login")

        try:

            admin = AdminRegister.objects.get(
                admin_id=admin_id
            )

            # Check hashed password
            if check_password(
                password,
                admin.password
            ):

                # Create session
                request.session.flush()
                request.session["admin_id"] = admin.admin_id
                request.session["admin_name"] = admin.name

                messages.success(
                    request,
                    f"Welcome, {admin.name}!"
                )

                # IMPORTANT:
                # Redirect to admin home
                return redirect("admin_home")

            else:

                messages.error(
                    request,
                    "Invalid Admin ID or password."
                )

        except AdminRegister.DoesNotExist:

            messages.error(
                request,
                "Invalid Admin ID or password."
            )

    return render(
        request,
        "cafe_app/admin_login.html"
    )


# ==========================================================
# ADMIN LOGOUT
# ==========================================================

def admin_logout(request):

    request.session.flush()

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("admin_login")


#ADD Table


from .models import CafeTable
from django.shortcuts import render


@admin_required
def view_table(request):
    tables = CafeTable.objects.all()

    return render(
        request,
        'cafe_app/admin_records.html',
        {
            'title': 'Tables',
            'description': 'Current café table setup and availability.',
            'headers': ['Table', 'Type', 'Status'],
            'rows': [[table.table_name, table.table_type, table.status] for table in tables],
            'records': tables, 'section': 'tables',
            'empty_message': 'No tables have been added yet.',
        },
    )


@admin_required
def admin_records(request, section):
    """Render working admin list and report destinations used by the navbar."""
    if section == 'items':
        records = CafeItem.objects.all()
        context = {
            'title': 'Items', 'description': 'Items currently in the café menu.',
            'headers': ['Code', 'Name', 'Category', 'Quantity', 'Price'],
            'rows': [[item.item_code, item.item_name, item.get_category_display(), item.quantity, item.price] for item in records],
            'records': records, 'section': section,
            'empty_message': 'No items have been added yet.', 'action_url': 'add_items', 'action_label': 'Add item',
        }
    elif section == 'purchases':
        records = CafePurchase.objects.all()
        context = {
            'title': 'Purchases', 'description': 'Purchase entries recorded for café stock.',
            'headers': ['Date', 'Code', 'Name', 'Category', 'Quantity', 'Cost', 'Selling price'],
            'rows': [[purchase.purchase_date.strftime('%d %b %Y'), purchase.item_code, purchase.item_name, purchase.get_category_display(), purchase.quantity, purchase.purchase_price, purchase.selling_price] for purchase in records],
            'records': records, 'section': section,
            'empty_message': 'No purchases have been recorded yet.', 'action_url': 'add_purchase', 'action_label': 'Add purchase',
        }
    elif section == 'staff':
        records = Staff.objects.all()
        context = {
            'title': 'Staff', 'description': 'Café staff directory.',
            'headers': ['Staff ID', 'Name', 'Mobile', 'Salary'],
            'rows': [[person.staff_id, person.staff_name, person.mobile_number, person.salary] for person in records],
            'records': records, 'section': section,
            'empty_message': 'No staff members have been added yet.', 'action_url': 'add_staff', 'action_label': 'Add staff',
        }
    elif section == 'expenses':
        records = Expenses.objects.all()
        context = {
            'title': 'Expenses', 'description': 'Recorded café expenses.',
            'headers': ['Date', 'Reason', 'Staff', 'Amount'],
            'rows': [[expense.date.strftime('%d %b %Y'), expense.reason, expense.staff_name or '—', expense.amt] for expense in records],
            'records': records, 'section': section,
            'empty_message': 'No expenses have been recorded yet.', 'action_url': 'add_expenses', 'action_label': 'Add expense',
        }
    else:
        context = {
            'title': 'Business report',
            'description': 'A summary of the data currently recorded in the admin panel.',
            'headers': ['Measure', 'Value'],
            'rows': [
                ['Tables', CafeTable.objects.count()],
                ['Menu items', CafeItem.objects.count()],
                ['Staff members', Staff.objects.count()],
                ['Purchase entries', CafePurchase.objects.count()],
                ['Expenses recorded', Expenses.objects.count()],
                ['Units purchased', sum(CafePurchase.objects.values_list('quantity', flat=True))],
                ['Purchase cost', sum((p.purchase_price * p.quantity for p in CafePurchase.objects.all()), Decimal('0.00'))],
            ],
            'empty_message': '', 'action_url': 'admin_home', 'action_label': 'Back to dashboard',
        }
    return render(request, 'cafe_app/admin_records.html', context)


@admin_required
def manage_record(request, section, pk, action):
    """Edit a listed admin record or delete it with a POST confirmation."""
    from .forms import CafeItemForm, CafePurchaseForm, CafeTableForm, ExpensesForm, StaffForm

    configs = {
        'tables': (CafeTable, CafeTableForm, 'view_table'),
        'items': (CafeItem, CafeItemForm, 'view_items'),
        'purchases': (CafePurchase, CafePurchaseForm, 'view_purchases'),
        'staff': (Staff, StaffForm, 'view_staff'),
        'expenses': (Expenses, ExpensesForm, 'view_expenses'),
    }
    if section not in configs or action not in {'edit', 'delete'}:
        return redirect('admin_home')
    model, form_class, list_name = configs[section]
    record = get_object_or_404(model, pk=pk)

    if action == 'delete':
        if request.method == 'POST':
            with transaction.atomic():
                if section == 'purchases':
                    item = CafeItem.objects.filter(item_code__iexact=record.item_code).first()
                    if item:
                        item.quantity = max(0, item.quantity - record.quantity)
                        item.save(update_fields=['quantity'])
                record.delete()
            messages.success(request, 'Record deleted successfully.')
            return redirect(list_name)
        return render(request, 'cafe_app/confirm_delete.html', {'record': record, 'section': section, 'list_name': list_name})

    form = form_class(request.POST or None, instance=record)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            if section == 'purchases':
                old_code, old_qty = record.item_code, record.quantity
                updated = form.save()
                old_item = CafeItem.objects.filter(item_code__iexact=old_code).first()
                if old_item:
                    old_item.quantity = max(0, old_item.quantity - old_qty)
                    old_item.save(update_fields=['quantity'])
                new_item = CafeItem.objects.filter(item_code__iexact=updated.item_code).first()
                if new_item:
                    new_item.quantity += updated.quantity
                    new_item.price = updated.selling_price
                    new_item.save(update_fields=['quantity', 'price'])
                else:
                    CafeItem.objects.create(item_code=updated.item_code, item_name=updated.item_name,
                        quantity=updated.quantity, price=updated.selling_price, category=updated.category)
            else:
                form.save()
        messages.success(request, 'Record updated successfully.')
        return redirect(list_name)
    return render(request, 'cafe_app/manage_record.html', {
        'form': form, 'section': section, 'action': action,
        'list_name': list_name,
    })

#ADD items

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CafeItem
from decimal import Decimal, InvalidOperation


@admin_required
def add_items(request):
    context = {
        'msg': '',
        'item_code': '',
        'item_name': '',
        'quantity': '',
        'price': '',
        'category': '',
    }

    if request.method == 'POST':
        item_code = request.POST.get('t1', '').strip()
        item_name = request.POST.get('t2', '').strip()
        quantity = request.POST.get('qty', '').strip()
        price = request.POST.get('t4', '').strip()
        category = request.POST.get('t5', '').strip()

        context.update({
            'item_code': item_code,
            'item_name': item_name,
            'quantity': quantity,
            'price': price,
            'category': category,
        })

        if not all([item_code, item_name, quantity, price, category]):
            context['msg'] = 'Please fill in all fields.'

        elif category not in ['food', 'alcohol', 'soft_drink']:
            context['msg'] = 'Please select a valid category.'

        elif CafeItem.objects.filter(item_code__iexact=item_code).exists():
            context['msg'] = 'This item code already exists.'

        else:
            try:
                quantity_value = int(quantity)
                price_value = Decimal(price)

                if quantity_value < 0 or price_value < 0:
                    raise ValueError

                CafeItem.objects.create(
                    item_code=item_code,
                    item_name=item_name,
                    quantity=quantity_value,
                    price=price_value,
                    category=category,
                )

                messages.success(
                    request,
                    f'{item_name} added successfully!'
                )
                return redirect('add_items')

            except (ValueError, InvalidOperation):
                context['msg'] = 'Enter a valid quantity and price.'

    return render(request, 'cafe_app/add_items.html', context)

#ADD PURCHASE


from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CafePurchase


@admin_required
def add_purchase(request):
    context = {
        'msg': '',
        'item_code': '',
        'item_name': '',
        'quantity': '',
        'price': '',
        'selling_price': '',
        'category': '',
    }

    if request.method == 'POST':
        item_code = request.POST.get('t1', '').strip()
        item_name = request.POST.get('t2', '').strip()
        quantity = request.POST.get('qty', '').strip()
        price = request.POST.get('t4', '').strip()
        selling_price = request.POST.get('selling', '').strip()
        category = request.POST.get('t5', '').strip()

        context.update({
            'item_code': item_code,
            'item_name': item_name,
            'quantity': quantity,
            'price': price,
            'selling_price': selling_price,
            'category': category,
        })

        if not all([
            item_code, item_name, quantity,
            price, selling_price, category
        ]):
            context['msg'] = 'Please fill in all fields.'

        elif category not in ['food', 'alcohol', 'soft_drink']:
            context['msg'] = 'Please select a valid category.'

        else:
            try:
                quantity_value = int(quantity)
                purchase_value = Decimal(price)
                selling_value = Decimal(selling_price)

                if (
                    quantity_value < 1
                    or not purchase_value.is_finite()
                    or not selling_value.is_finite()
                    or purchase_value < 0
                    or selling_value < 0
                ):
                    raise ValueError

                with transaction.atomic():
                    CafePurchase.objects.create(
                        item_code=item_code,
                        item_name=item_name,
                        quantity=quantity_value,
                        purchase_price=purchase_value,
                        selling_price=selling_value,
                        category=category,
                    )
                    item = CafeItem.objects.filter(
                        item_code__iexact=item_code
                    ).first()
                    if item:
                        item.quantity += quantity_value
                        item.price = selling_value
                        item.save(update_fields=['quantity', 'price'])
                    else:
                        CafeItem.objects.create(
                            item_code=item_code,
                            item_name=item_name,
                            quantity=quantity_value,
                            price=selling_value,
                            category=category,
                        )

                messages.success(
                    request,
                    f'Purchase for {item_name} saved successfully!'
                )
                return redirect('add_purchase')

            except (ValueError, InvalidOperation):
                context['msg'] = (
                    'Enter a valid quantity and non-negative prices.'
                )

    return render(
        request,
        'cafe_app/add_purchase.html',
        context
    )

#add staff

from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Staff
from .models import Expenses


@admin_required
def add_staff(request):
    context = {}

    if request.method == 'POST':
        staff_id = request.POST.get('staff_id', '').strip()
        staff_name = request.POST.get('staff_name', '').strip()
        mobile_number = request.POST.get('mobile_number', '').strip()
        salary = request.POST.get('salary', '').strip()

        context = {
            'staff_id': staff_id,
            'staff_name': staff_name,
            'mobile_number': mobile_number,
            'salary': salary,
        }

        if not all([staff_id, staff_name, mobile_number, salary]):
            context['error'] = 'Please fill in all fields.'

        elif not mobile_number.isdigit() or not 10 <= len(mobile_number) <= 15:
            context['error'] = 'Enter a valid mobile number (10–15 digits).'

        elif Staff.objects.filter(staff_id=staff_id).exists():
            context['error'] = 'This Staff ID already exists.'

        else:
            try:
                salary_value = Decimal(salary)

                if not salary_value.is_finite() or salary_value < 0:
                    raise ValueError

                Staff.objects.create(
                    staff_id=staff_id,
                    staff_name=staff_name,
                    mobile_number=mobile_number,
                    salary=salary_value,
                )

                messages.success(
                    request,
                    'Staff details added successfully!'
                )
                return redirect('add_staff')

            except (InvalidOperation, ValueError):
                context['error'] = 'Please enter a valid, non-negative salary.'

    return render(request, 'cafe_app/add_staff.html', context)

#add expenses

#my order

#my profile

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserRegister


def my_profile(request):
    user_id = request.session.get("user_id")

    if not user_id:
        messages.error(request, "Please log in to view your profile.")
        return redirect("userlogin")

    try:
        profile = UserRegister.objects.get(id=user_id)
    except UserRegister.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect("userlogin")

    if request.method == "POST":
        user_name = request.POST.get("user_name", "").strip()
        mobile_number = request.POST.get("mobile_number", "").strip()

        if not user_name:
            messages.error(request, "Name is required.")
        elif not mobile_number.isdigit() or len(mobile_number) != 10:
            messages.error(request, "Enter a valid 10-digit mobile number.")
        elif UserRegister.objects.filter(mobile_number=mobile_number).exclude(pk=profile.pk).exists():
            messages.error(request, "That mobile number is already registered.")
        else:
            profile.user_name = user_name
            profile.mobile_number = mobile_number
            profile.save(update_fields=["user_name", "mobile_number"])
            request.session["user_name"] = profile.user_name
            messages.success(request, "Your profile was updated successfully.")
            return redirect("my_profile")

    return render(
        request,
        "cafe_app/my_profile.html",
        {"profile": profile}
    )

def user_about(request):
    return render(request, 'cafe_app/user_about.html')

def user_menu(request):
    return render(request, 'cafe_app/user_menu.html', _menu_context(request))

def user_contact(request):
    return render(request, 'cafe_app/user_contact.html')

#add_order_user
import json
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.db import transaction
from django.db.models import F
from django.urls import reverse

from .models import CafeItem, CafeTable, ItemOrder


def add_order_user(request):
    """Display the order-entry page."""

    table_name = request.GET.get("table", "").strip()
    source = "admin" if request.GET.get("source") == "admin" else "user"
    if source == 'admin':
        admin_id = request.session.get('admin_id')
        if not admin_id or not AdminRegister.objects.filter(admin_id=admin_id).exists():
            messages.error(request, 'Please log in as an administrator to continue.')
            return redirect('admin_login')
    else:
        user_id = request.session.get('user_id')
        if not user_id or not UserRegister.objects.filter(id=user_id).exists():
            messages.error(request, 'Please log in to place an order.')
            return redirect('userlogin')
    if not CafeTable.objects.filter(table_name__iexact=table_name).exists():
        messages.error(request, 'Please select a valid café table.')
        return redirect('admin_home' if source == 'admin' else 'user_home')
    home_url = reverse("admin_home" if source == "admin" else "user_home")
    today = timezone.localdate()

    existing_bill_numbers = ItemOrder.objects.exclude(
        bill_no__isnull=True
    ).values_list("bill_no", flat=True)
    numeric_bill_numbers = [
        int(number) for number in existing_bill_numbers
        if number and number.isdigit()
    ]

    context = {
        "Table_name": table_name,
        "Bill_no": str(max(numeric_bill_numbers, default=1000) + 1),
        "today": today.isoformat(),
        "home_url": home_url,
        "source": source,
    }

    return render(request, "cafe_app/add_order_user.html", context)


@require_GET
def get_item_suggestions(request):
    """Return food-item names matching the search text."""

    query = request.GET.get("query", "").strip()

    if len(query) < 2:
        return JsonResponse([], safe=False)

    items = CafeItem.objects.filter(
        item_name__icontains=query
    ).order_by("item_name")[:15]

    data = [
        {
            "Item_code": item.item_code,
            "Item_name": item.item_name,
            "item_cat": item.get_category_display(),
            "Item_price": str(item.price),
        }
        for item in items
    ]

    return JsonResponse(data, safe=False)


@require_GET
def get_item_details(request):
    """Return the details of a food item selected by name."""

    item_name = request.GET.get("item_name", "").strip()

    if not item_name:
        return JsonResponse(
            {"error": "Please provide an item name."},
            status=400
        )

    item = CafeItem.objects.filter(
        item_name__iexact=item_name
    ).first()

    if not item:
        return JsonResponse(
            {"error": "Food item not found."},
            status=404
        )

    return JsonResponse({
        "Item_code": item.item_code,
        "Item_name": item.item_name,
        "item_cat": item.get_category_display(),
        "Item_price": str(item.price),
    })


@require_GET
def get_item_by_code(request, item_code):
    """Return the details of a food item by its code."""

    item = CafeItem.objects.filter(
        item_code__iexact=item_code
    ).first()

    if not item:
        return JsonResponse(
            {"error": "Food item not found."},
            status=404
        )

    return JsonResponse({
        "Item_code": item.item_code,
        "Item_name": item.item_name,
        "item_cat": item.get_category_display(),
        "Item_price": str(item.price),
    })


@require_POST
def save_order_user(request):
    """Save all valid bill rows as ItemOrder records."""

    try:
        payload = json.loads(request.body)
        if not isinstance(payload, dict):
            raise ValueError('Invalid order data.')

        bill_details = payload.get("billDetails", {})
        bill_items = payload.get("billItems", [])
        if not isinstance(bill_details, dict) or not isinstance(bill_items, list):
            raise ValueError('Invalid order data.')
        source = 'admin' if bill_details.get('source') == 'admin' else 'user'

        if source == 'admin':
            admin_id = request.session.get('admin_id')
            if not admin_id or not AdminRegister.objects.filter(admin_id=admin_id).exists():
                return JsonResponse({"success": False, "error": "Admin login required."}, status=403)
            order_user = None
        else:
            user_id = request.session.get('user_id')
            order_user = UserRegister.objects.filter(id=user_id).first() if user_id else None
            if order_user is None:
                return JsonResponse({"success": False, "error": "Please log in to place an order."}, status=403)

        table_name = str(
            bill_details.get("table_name", "")
        ).strip()

        bill_no = str(
            bill_details.get("bill_no", "")
        ).strip()

        bill_date = date.fromisoformat(
            str(bill_details.get("bill_date", ""))
        )

        if not table_name or not bill_no:
            return JsonResponse(
                {"success": False,
                 "error": "Table name and bill number are required."},
                status=400
            )

        if len(table_name) > 100 or len(bill_no) > 10:
            return JsonResponse(
                {"success": False,
                 "error": "Table name or bill number is too long."},
                status=400
            )

        table = CafeTable.objects.filter(table_name__iexact=table_name).first()
        if table is None:
            return JsonResponse(
                {"success": False, "error": "Please select a valid café table."},
                status=400
            )

        if ItemOrder.objects.filter(bill_no=bill_no).exists():
            return JsonResponse(
                {"success": False, "error": "This bill number has already been used."},
                status=400
            )

        if not bill_items:
            return JsonResponse(
                {"success": False,
                 "error": "Add at least one food item."},
                status=400
            )

        records = []
        stock_used = {}
        now = timezone.localtime()

        for row in bill_items:
            if not isinstance(row, dict):
                raise ValueError('Invalid item row.')
            item_code = str(row.get("item_code", "")).strip()

            if not item_code:
                if row.get('item_name'):
                    raise ValueError('Enter a valid item code for every selected item.')
                continue

            item = CafeItem.objects.filter(
                item_code__iexact=item_code
            ).first()

            if not item:
                raise ValueError(
                    f"Food item code {item_code} does not exist."
                )

            try:
                qty = int(row.get("qty", 0))
                gst_rate = Decimal(str(row.get("gst", "0")))
            except (ValueError, InvalidOperation):
                raise ValueError(
                    "Quantity or GST rate is invalid."
                )

            if qty < 1:
                raise ValueError(
                    f"Quantity must be at least 1 for {item.item_name}."
                )

            already_requested = stock_used.get(item.pk, 0)
            if qty + already_requested > item.quantity:
                raise ValueError(
                    f"Only {max(item.quantity - already_requested, 0)} "
                    f"{item.item_name} available in stock."
                )
            stock_used[item.pk] = already_requested + qty

            if gst_rate < 0 or gst_rate > 100:
                raise ValueError("GST must be between 0 and 100.")

            # Always use the current database price, not a browser price.
            price = Decimal(str(item.price))
            subtotal = (price * qty).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            gst_amount = (
                subtotal * gst_rate / Decimal("100")
            ).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            grand_total = subtotal + gst_amount

            records.append(
                ItemOrder(
                    user=order_user,
                    table_name=table_name,
                    bill_no=bill_no,
                    bill_date=bill_date,
                    bill_time=now.time(),
                    item_code=str(item.item_code),
                    item_name=str(item.item_name),
                    item_cat=str(item.get_category_display()),
                    price=price,
                    gst=gst_rate,
                    qty=qty,
                    tax_amt=subtotal,
                    total_gst=gst_amount,
                    total=grand_total,
                )
            )

        if not records:
            return JsonResponse(
                {"success": False,
                 "error": "No valid food items were submitted."},
                status=400
            )

        with transaction.atomic():
            for item_id, quantity in stock_used.items():
                updated = CafeItem.objects.filter(
                    pk=item_id, quantity__gte=quantity
                ).update(quantity=F('quantity') - quantity)
                if updated != 1:
                    raise ValueError('Stock changed while saving. Please try again.')
            ItemOrder.objects.bulk_create(records)
            table.status = "Occupied"
            table.save(update_fields=["status"])

        bill_total = sum(
            (record.total for record in records),
            Decimal("0.00")
        )

        return JsonResponse({
            "success": True,
            "message": "Order saved successfully.",
            "bill_no": bill_no,
            "bill_total": str(bill_total),
        })

    except (ValueError, InvalidOperation, TypeError) as exc:
        return JsonResponse(
            {"success": False, "error": str(exc)},
            status=400
        )
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON data."},
            status=400
        )

# Print and settle bills from the same order records created by users.

@admin_required
@require_GET
def print_table(request):
    bill_no = request.GET.get("bill_no")
    table_name = request.GET.get("table_name")

    orders = ItemOrder.objects.all()

    if bill_no:
        orders = orders.filter(bill_no=bill_no)
    elif table_name:
        latest_order = (
            orders.filter(table_name=table_name)
            .order_by("-bill_date", "-bill_time", "-id")
            .first()
        )

        if latest_order and latest_order.bill_no:
            orders = orders.filter(bill_no=latest_order.bill_no)
        else:
            orders = ItemOrder.objects.none()
    else:
        orders = ItemOrder.objects.none()

    orders = orders.order_by("id")
    items = list(orders)

    if not items:
        return render(
            request,
            "cafe_app/print_bill.html",
            {
                "table_data": {
                    "table_name": table_name or "",
                    "items": [],
                    "total": Decimal("0.00"),
                },
                "company": [],
                "bill_no": bill_no or "",
                "error": "No bill found. Please check the bill number or table name.",
            },
        )

    grand_total = sum(
        (item.total or Decimal("0.00")) for item in items
    )

    table_data = {
        "table_name": items[0].table_name,
        "items": items,
        "total": grand_total,
    }

    context = {
        "table_data": table_data,
        "company": [],
        "bill_no": items[0].bill_no,
    }

    return render(request, "cafe_app/print_bill.html", context)


@admin_required
@require_POST
def settle_bill(request, bill_no):
    bill_items = ItemOrder.objects.filter(bill_no=bill_no, is_settled=False)
    table_name = bill_items.values_list('table_name', flat=True).first()
    if not table_name:
        messages.error(request, 'That open bill could not be found.')
        return redirect('admin_home')

    with transaction.atomic():
        bill_items.update(is_settled=True)
        still_open = ItemOrder.objects.filter(
            table_name=table_name,
            is_settled=False,
        ).exists()
        if not still_open:
            CafeTable.objects.filter(table_name=table_name).update(status='Available')
    messages.success(request, f'Bill {bill_no} settled successfully.')
    return redirect("admin_home")
