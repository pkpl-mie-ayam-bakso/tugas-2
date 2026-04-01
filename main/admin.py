from django.contrib import admin
from .models import SiteSettings, AuditLog


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'primary_color',
        'font_family',
        'font_size_base',
        'last_modified_by',
        'updated_at'
    ]
    readonly_fields = ['last_modified_by', 'updated_at']

    def has_add_permission(self, request):
        """Prevent adding new settings objects (only one should exist)."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deleting settings."""
        return False

    def has_change_permission(self, request, obj=None):
        """Only superusers can modify settings."""
        return request.user.is_superuser

    def get_queryset(self, request):
        """Filter queryset based on user role."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.none()  # Non-superuser staff sees nothing


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user_email', 'timestamp', 'success', 'ip_address']
    list_filter = ['action', 'success', 'timestamp']
    search_fields = ['user_email', 'ip_address']
    readonly_fields = [
        'action', 'user_email', 'ip_address', 'changes', 'timestamp', 'success'
    ]

    def has_add_permission(self, request):
        """Prevent manual log creation."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent log deletion."""
        return False

    def has_change_permission(self, request, obj=None):
        """Only superusers can view logs."""
        return request.user.is_superuser
