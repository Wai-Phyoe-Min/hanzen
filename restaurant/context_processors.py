from django.utils import timezone
from .models import BusinessHours, SiteSettings


def site_settings_context(request):
    """Make site settings available to all templates"""
    settings_obj = None
    try:
        settings_obj = SiteSettings.objects.get(pk=1)
    except SiteSettings.DoesNotExist:
        pass
    return {
        'site_settings': settings_obj,
    }


def business_hours_footer(request):
    today_hours = None
    preferred_lang = 'ja'
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        if profile and getattr(profile, 'preferred_lang', None) in ['ja', 'en']:
            preferred_lang = profile.preferred_lang
    try:
        today = timezone.localtime(timezone.now()).date()
        today_hours = BusinessHours.objects.filter(day=today.weekday()).first()
    except Exception:
        today_hours = None
    return {
        'business_hours_footer_today': today_hours,
        'preferred_lang': preferred_lang,
    }