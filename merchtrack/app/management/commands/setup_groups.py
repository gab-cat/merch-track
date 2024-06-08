from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from app.models import Order, Product, Customer, Fulfillment, Payment, Log  # Adjust as needed

class Command(BaseCommand):
    help = 'Create groups and assign permissions'

    def handle(self, *args, **kwargs):
        groups_permissions = {
            'Customers': [
                'add_order', 'view_order', 'change_order', 'delete_order',
                'add_payment', 'view_payment', 'change_payment', 'delete_payment',
                'view_product',
            ],
            'Staffs': [
                'view_dashboard', 'view_messages', 'add_message', 'change_message', 'delete_message',
                'view_success', 'send_reply_email'
            ],
            'Order-Entry': [
                'add_order', 'view_order', 'change_order', 'delete_order',
                'view_customer', 'view_product'
            ],
            'Collection': [
                'add_payment', 'view_payment', 'change_payment', 'delete_payment',
                'view_order'
            ],
            'Fulfillment': [
                'add_fulfillment', 'view_fulfillment', 'change_fulfillment', 'delete_fulfillment',
                'view_order'
            ],
            'Product': [
                'add_product', 'view_product', 'change_product', 'delete_product'
            ],
            'Report': [
                'view_report'
            ],
            'Admin': [
                'add_user', 'change_user', 'delete_user', 'view_user',
                'add_group', 'change_group', 'delete_group', 'view_group',
                'add_order', 'view_order', 'change_order', 'delete_order',
                'add_product', 'view_product', 'change_product', 'delete_product',
                'add_customer', 'view_customer', 'change_customer', 'delete_customer',
                'add_fulfillment', 'view_fulfillment', 'change_fulfillment', 'delete_fulfillment',
                'add_payment', 'view_payment', 'change_payment', 'delete_payment',
                'view_report', 'add_log', 'view_log', 'change_log', 'delete_log',
            ],
        }

        for group_name, permissions in groups_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            for perm in permissions:
                try:
                    app_label, model_perm = perm.split('_', 1)
                    permission = Permission.objects.get(content_type__app_label=app_label, codename=perm)
                    group.permissions.add(permission)
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Permission '{perm}' does not exist."))
            group.save()
            self.stdout.write(self.style.SUCCESS(f"Group '{group_name}' created/updated with permissions"))
