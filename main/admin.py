from django.contrib import admin
from .models import SiteSettings

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display  = ['primary_color', 'font_family', 'font_size_base', 'last_modified_by', 'updated_at']
    readonly_fields = ['last_modified_by', 'updated_at']