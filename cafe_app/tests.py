import json
from decimal import Decimal

from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase
from django.urls import reverse

from .models import AdminRegister, CafeItem, CafeTable, ItemOrder, UserRegister


class CafeWorkflowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserRegister.objects.create(
            user_name='Asha',
            mobile_number='9876543210',
            password=make_password('user-pass-123'),
        )
        self.admin = AdminRegister.objects.create(
            name='Cafe Admin',
            admin_id='admin-1',
            password=make_password('admin-pass-123'),
        )
        self.table = CafeTable.objects.create(
            table_name='Table 1', table_type='A/C'
        )
        self.item = CafeItem.objects.create(
            item_code='CF001', item_name='Cappuccino', quantity=8,
            price=Decimal('120.00'), category='food',
        )

    def log_in_user(self):
        session = self.client.session
        session['user_id'] = self.user.pk
        session['user_name'] = self.user.user_name
        session.save()

    def log_in_admin(self):
        session = self.client.session
        session['admin_id'] = self.admin.admin_id
        session['admin_name'] = self.admin.name
        session.save()

    def submit_order(self, bill_no='1001', qty=2, source='user'):
        return self.client.post(
            reverse('save_order_user'),
            data=json.dumps({
                'billDetails': {
                    'table_name': self.table.table_name,
                    'bill_no': bill_no,
                    'bill_date': '2026-10-19',
                    'source': source,
                },
                'billItems': [{
                    'item_code': self.item.item_code,
                    'qty': qty,
                    'gst': 5,
                }],
            }),
            content_type='application/json',
        )

    def test_user_can_choose_table_and_lookup_item_by_code(self):
        self.log_in_user()
        response = self.client.get(reverse('add_order_user'), {
            'table': self.table.table_name,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.table.table_name)

        response = self.client.get(
            reverse('get_item_by_code', args=[self.item.item_code])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['Item_name'], self.item.item_name)
        self.assertEqual(response.json()['Item_price'], '120.00')

        response = self.client.get(reverse('user_menu'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CF001')
        response = self.client.get(reverse('menu'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cappuccino')

    def test_tea_and_coffee_uses_code_101_inventory_without_duplicate_card(self):
        CafeItem.objects.create(
            item_code='101', item_name='Tea and Coffee', quantity=7,
            price=Decimal('30.00'), category='food',
        )

        response = self.client.get(reverse('user_menu'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'alt="Tea and Coffee"')
        self.assertContains(response, "img/1coffee.jpg")
        self.assertContains(response, 'Available stock: 7')
        self.assertNotContains(response, 'alt="Coffee"')

    def test_user_and_admin_login_redirect_to_their_dashboards(self):
        response = self.client.post(reverse('userlogin'), {
            'name': 'Asha', 'password': 'user-pass-123',
        })
        self.assertRedirects(response, reverse('user_home'))
        self.assertEqual(self.client.session['user_id'], self.user.pk)

        response = self.client.post(reverse('admin_login'), {
            'admin_id': self.admin.admin_id, 'password': 'admin-pass-123',
        })
        self.assertRedirects(response, reverse('admin_home'))
        self.assertEqual(
            self.client.session['admin_id'], self.admin.admin_id
        )
        self.assertNotIn('user_id', self.client.session)
        response = self.client.get(reverse('add_order_user'), {
            'table': self.table.table_name,
            'source': 'admin',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('admin_home'))

    def test_order_is_saved_for_user_and_visible_to_admin(self):
        self.log_in_user()
        response = self.submit_order()
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()['bill_total'], '252.00')

        order = ItemOrder.objects.get(bill_no='1001')
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.price, Decimal('120.00'))
        self.assertEqual(order.total, Decimal('252.00'))
        self.assertEqual(CafeItem.objects.get(pk=self.item.pk).quantity, 6)
        self.assertEqual(
            CafeTable.objects.get(pk=self.table.pk).status, 'Occupied'
        )

        self.log_in_admin()
        response = self.client.get(reverse('admin_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1001')
        self.assertContains(response, 'Cappuccino')
        self.assertContains(response, 'Print bill')
        self.assertContains(response, 'Settle')

    def test_admin_can_print_and_settle_without_deleting_bill_history(self):
        self.log_in_user()
        self.assertEqual(self.submit_order().status_code, 200)
        self.log_in_admin()

        response = self.client.get(reverse('print_table'), {'bill_no': '1001'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cappuccino')
        self.assertContains(response, '252.00')

        response = self.client.post(
            reverse('settle_bill', args=['1001'])
        )
        self.assertRedirects(response, reverse('admin_home'))
        self.assertTrue(ItemOrder.objects.filter(bill_no='1001').exists())
        self.assertTrue(ItemOrder.objects.get(bill_no='1001').is_settled)
        self.assertEqual(
            CafeTable.objects.get(pk=self.table.pk).status, 'Available'
        )

    def test_my_orders_shows_only_the_signed_in_users_orders(self):
        self.log_in_user()
        self.assertEqual(self.submit_order().status_code, 200)

        response = self.client.get(reverse('my_order'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1001')
        self.assertContains(response, 'Cappuccino × 2')
        self.assertContains(response, '0.00')

        self.log_in_admin()
        self.client.post(reverse('settle_bill', args=['1001']))
        self.log_in_user()
        response = self.client.get(reverse('my_order'))
        self.assertContains(response, '252.00')

    def test_admin_pages_require_a_real_admin_session(self):
        response = self.client.get(reverse('admin_home'))
        self.assertRedirects(response, reverse('admin_login'))
        response = self.client.post(reverse('settle_bill', args=['1001']))
        self.assertRedirects(response, reverse('admin_login'))

    def test_order_cannot_exceed_stock_or_reuse_a_bill_number(self):
        self.log_in_user()
        response = self.submit_order(bill_no='1001', qty=9)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(ItemOrder.objects.exists())
        self.assertEqual(CafeItem.objects.get(pk=self.item.pk).quantity, 8)

        self.assertEqual(self.submit_order(bill_no='1001').status_code, 200)
        response = self.submit_order(bill_no='1001')
        self.assertEqual(response.status_code, 400)

    def test_purchase_replenishes_the_menu_item_stock(self):
        self.log_in_admin()
        response = self.client.post(reverse('add_purchase'), {
            't1': self.item.item_code,
            't2': self.item.item_name,
            'qty': '5',
            't4': '60.00',
            'selling': '125.00',
            't5': 'food',
        })
        self.assertRedirects(response, reverse('add_purchase'))
        item = CafeItem.objects.get(pk=self.item.pk)
        self.assertEqual(item.quantity, 13)
        self.assertEqual(item.price, Decimal('125.00'))

    def test_admin_management_forms_persist_their_records(self):
        self.log_in_admin()

        response = self.client.post(reverse('add_table'), {
            't1': 'Table 2', 't2': 'Non A/C',
        })
        self.assertRedirects(response, reverse('admin_home'))
        self.assertTrue(CafeTable.objects.filter(table_name='Table 2').exists())

        response = self.client.post(reverse('add_items'), {
            't1': 'CF002', 't2': 'Tea', 'qty': '12',
            't4': '35.00', 't5': 'food',
        })
        self.assertRedirects(response, reverse('add_items'))
        self.assertTrue(CafeItem.objects.filter(item_code='CF002').exists())

        response = self.client.post(reverse('add_staff'), {
            'staff_id': 'S-1', 'staff_name': 'Ravi',
            'mobile_number': '9876543211', 'salary': '18000.00',
        })
        self.assertRedirects(response, reverse('add_staff'))

        response = self.client.post(reverse('add_expenses'), {
            'date': '2026-10-19', 'amount': '250.00',
            'reason': 'Cleaning supplies', 'staff_name': 'Ravi',
        })
        self.assertRedirects(response, reverse('add_expenses'))
        self.assertEqual(self.client.get(reverse('view_staff')).status_code, 200)
        self.assertEqual(self.client.get(reverse('view_expenses')).status_code, 200)

    def test_user_registration_persists_a_hashed_password(self):
        response = self.client.post(reverse('userregister'), {
            'name': 'New User', 'phone': '9123456789',
            'password': 'new-pass-123',
        })
        self.assertRedirects(response, reverse('userlogin'))
        account = UserRegister.objects.get(mobile_number='9123456789')
        self.assertNotEqual(account.password, 'new-pass-123')
