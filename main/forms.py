import re
from django import forms
from .models import SiteSettings


class SiteSettingsForm(forms.ModelForm):
    """Form for customizing site appearance with input validation.

    Validates:
    - Color fields: Must be valid hex codes (#RGB or #RRGGBB)
    - Font family: Must be in the defined choices
    - Font size: Must be between 10-32 pixels
    """

    class Meta:
        model = SiteSettings
        fields = [
            'primary_color', 'secondary_color', 'background_color',
            'text_color', 'card_color', 'font_family', 'font_size_base'
        ]
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color'}),
            'background_color': forms.TextInput(attrs={'type': 'color'}),
            'text_color': forms.TextInput(attrs={'type': 'color'}),
            'card_color': forms.TextInput(attrs={'type': 'color'}),
        }

    def clean_primary_color(self):
        return self._validate_hex_color('primary_color')

    def clean_secondary_color(self):
        return self._validate_hex_color('secondary_color')

    def clean_background_color(self):
        return self._validate_hex_color('background_color')

    def clean_text_color(self):
        return self._validate_hex_color('text_color')

    def clean_card_color(self):
        return self._validate_hex_color('card_color')

    def clean_font_size_base(self):
        """Validate font size is within acceptable range."""
        value = self.cleaned_data.get('font_size_base')
        if value is None:
            raise forms.ValidationError('Font size is required')

        try:
            size = int(value)
        except (ValueError, TypeError):
            raise forms.ValidationError('Font size must be a number')

        if not 10 <= size <= 32:
            raise forms.ValidationError('Font size must be between 10 and 32 pixels')

        return size

    def clean_font_family(self):
        """Validate font family is in allowed choices."""
        value = self.cleaned_data.get('font_family')
        valid_fonts = dict(SiteSettings._meta.get_field('font_family').choices)

        if value not in valid_fonts:
            allowed = ', '.join(valid_fonts.keys())
            raise forms.ValidationError(f'Invalid font family. Must be one of: {allowed}')

        return value

    def _validate_hex_color(self, field_name):
        """Validate that field contains valid hex color code."""
        value = self.cleaned_data.get(field_name)
        if not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', value):
            raise forms.ValidationError(
                'Invalid hex color. Use format #RGB or #RRGGBB'
            )
        return value
