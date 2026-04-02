from django.db import models


class SiteSettings(models.Model):
    primary_color    = models.CharField(max_length=7, default='#4F46E5')
    secondary_color  = models.CharField(max_length=7, default='#7C3AED')
    background_color = models.CharField(max_length=7, default='#F8FAFC')
    text_color       = models.CharField(max_length=7, default='#1E293B')
    card_color       = models.CharField(max_length=7, default='#FFFFFF')
    font_family      = models.CharField(
        max_length=100,
        default='Inter',
        choices=[
            ('Inter',            'Inter (Modern)'),
            ('Roboto',           'Roboto (Clean)'),
            ('Poppins',          'Poppins (Friendly)'),
            ('Merriweather',     'Merriweather (Serif)'),
            ('Fira Code',        'Fira Code (Monospace)'),
            ('Playfair Display', 'Playfair Display (Elegant)'),
        ]
    )
    font_size_base     = models.PositiveIntegerField(default=16)
    last_modified_by   = models.EmailField(blank=True)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return f'Site Settings (font: {self.font_family})'

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AuditLog(models.Model):
    """Track all modifications to site settings.

    Provides accountability and security monitoring.
    """
    ACTION_CHOICES = [
        ('UPDATE', 'Updated Settings'),
        ('VIEW', 'Viewed Settings'),
        ('FAILED_AUTH', 'Failed Authorization'),
    ]

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    user_email = models.EmailField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    changes = models.JSONField(
        default=dict,
        help_text="Fields changed and old/new values"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Log Entry'
        verbose_name_plural = 'Audit Logs'
        indexes = [
            models.Index(fields=['user_email', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.action} by {self.user_email} on {self.timestamp}"
