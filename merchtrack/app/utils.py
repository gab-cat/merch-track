from app.models import Customer, Log
from django.utils.timezone import now

def log_action(user, reason, system_text, customer=None):
    log = Log(
        customer=customer if customer else Customer.objects.get(user_id=999),
        created_date=now(),
        created_by=user,
        reason=reason,
        system_text=system_text,
    )
    log.save()
