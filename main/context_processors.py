from .models import SiteSettings


def site_settings(request):
    settings = SiteSettings.get_settings()
    return {
        'site_settings': settings,
        'is_member': _is_group_member(request),
    }


def _is_group_member(request):
    from django.conf import settings as django_settings
    if not request.user.is_authenticated:
        return False
    allowed = [e.strip().lower() for e in django_settings.ALLOWED_MEMBER_EMAILS]
    return request.user.email.lower() in allowed