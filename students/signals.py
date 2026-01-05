from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .models import ActivityLog
from .utils import get_client_ip, get_user_agent

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ActivityLog.objects.create(
        user=user,
        action='LOGIN',
        description='User logged in',
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    ActivityLog.objects.create(
        user=user,
        action='LOGOUT',
        description='User logged out',
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )


@receiver(user_login_failed)
def log_login_failed(sender, credentials, request, **kwargs):
    ActivityLog.objects.create(
        user=None,
        action='FAILED_LOGIN',
        description=f"Failed login attempt for {credentials.get('username')}",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
