
from django.urls import path
from . import views

urlpatterns = [
    # Home and user authentication
    path('', views.home, name='home'),
    path('userregister/', views.userregister, name='userregister'),
    path('userlogin/', views.userlogin, name='userlogin'),
    path('userlogout/', views.userlogout, name='userlogout'),

    # Public pages
    path('about/', views.about, name='about'),
    path('menu/', views.menu, name='menu'),
    path('offers/', views.offers, name='offers'),
    path('contact/', views.contact, name='contact'),

    # Admin authentication
    path('admin_register/', views.admin_register, name='admin_register'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),

    # Admin navigation and dashboard
    path('admin_nav/', views.admin_nav, name='admin_nav'),
    path('admin_home/', views.admin_home, name='admin_home'),

    # Admin management
    path('add_table/', views.add_table, name='add_table'),
    path('add_items/', views.add_items, name='add_items'),
    path('add_staff/', views.add_staff, name='add_staff'),
    path('add_expenses/', views.add_expenses, name='add_expenses'),
    path('add_purchase/', views.add_purchase, name='add_purchase'),

    # Admin records
    path('view_tables/', views.view_table, name='view_table'),
    path(
        'view_items/',
        views.admin_records,
        {'section': 'items'},
        name='view_items'
    ),
    path(
        'view_purchases/',
        views.admin_records,
        {'section': 'purchases'},
        name='view_purchases'
    ),
    path(
        'view_staff/',
        views.admin_records,
        {'section': 'staff'},
        name='view_staff'
    ),
    path(
        'admin_report/',
        views.admin_records,
        {'section': 'report'},
        name='admin_report'
    ),
    path('view_expenses/', views.view_expenses, name='view_expenses'),
    path('records/<str:section>/<int:pk>/<str:action>/', views.manage_record, name='manage_record'),

    # Table actions
    path('exchange_tbl/', views.exchange_tbl, name='exchange_tbl'),
    path('settle_table/', views.settle_table, name='settle_table'),
    path('checkTables/', views.checkTables, name='checkTables'),
    path('add_order/', views.add_order_user, name='add_order'),

    # User dashboard and navigation
    path('user_home/', views.user_home, name='user_home'),
    path('user_nav/', views.user_nav, name='user_nav'),
    path('my_order/', views.my_order, name='my_order'),
    path('my_profile/', views.my_profile, name='my_profile'),

    # User pages
    path('user_about/', views.user_about, name='user_about'),
    path('user_menu/', views.user_menu, name='user_menu'),
    path('user_contact/', views.user_contact, name='user_contact'),

    # User order page
    path(
        'add_order_user/',
        views.add_order_user,
        name='add_order_user'
    ),

    # Food item search and details
    path(
        'get-item-suggestions/',
        views.get_item_suggestions,
        name='get_item_suggestions'
    ),
    path(
        'get-item-details/',
        views.get_item_details,
        name='get_item_details'
    ),
    path(
        'item/<str:item_code>/',
        views.get_item_by_code,
        name='get_item_by_code'
    ),

    # Save bill and order items
    path(
        'save_order_user/',
        views.save_order_user,
        name='save_order_user'
    ),

    path(
        "print_table/",
        views.print_table,
        name="print_table",
    ),

    path(
        "settle_bill/<str:bill_no>/",
        views.settle_bill,
        name="settle_bill",
    ),
]
