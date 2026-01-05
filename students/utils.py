from .models import ActivityLog

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def get_user_agent(request):
    return request.META.get('HTTP_USER_AGENT', '')

def log_activity(user, description, action="OTHER", request=None):
    role = user.groups.first().name if user.groups.exists() else "None"

    ip_address = None
    user_agent = ""

    if request:
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)

    ActivityLog.objects.create(
        user=user,
        action=action,
        description=f"[{role}] {description}",
        ip_address=ip_address,
        user_agent=user_agent
    )
