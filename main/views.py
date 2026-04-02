from django.shortcuts import render, redirect
from django.contrib import messages
from django_ratelimit.decorators import ratelimit
from .models import SiteSettings
from .forms import SiteSettingsForm
from .context_processors import _is_group_member
from .utils import log_audit_event


def index(request):
    """Display group biodata (public page)."""
    return render(request, 'index.html', {'page_title': 'Beranda'})


@ratelimit(key='user', rate='20/m', method='POST', block=True)
def customize(request):
    """Customize site appearance (authorized members only).

    Features:
    - Requires authentication (Google OAuth)
    - Requires authorization (member email whitelist)
    - Input validation on all fields
    - Rate limiting on POST requests
    - Audit logging of all changes
    """
    # AUTHENTICATION CHECK
    if not request.user.is_authenticated:
        log_audit_event('FAILED_AUTH', request, success=False)
        messages.error(request, 'Kamu harus login terlebih dahulu.')
        return redirect('/')

    # AUTHORIZATION CHECK
    if not _is_group_member(request):
        log_audit_event(
            'FAILED_AUTH',
            request,
            success=False,
            changes={'reason': 'User not in allowed members list'}
        )
        messages.error(
            request,
            'Akses ditolak. Hanya anggota kelompok yang dapat mengubah tampilan.'
        )
        return redirect('/')

    site_cfg = SiteSettings.get_settings()

    if request.method == 'POST':
        form = SiteSettingsForm(request.POST, instance=site_cfg)

        if form.is_valid():
            # Track what changed for audit log
            changes = {}
            for field in form.changed_data:
                old_value = getattr(site_cfg, field)
                new_value = form.cleaned_data[field]
                changes[field] = {
                    'old': str(old_value),
                    'new': str(new_value)
                }

            # Save with audit trail
            settings_obj = form.save(commit=False)
            settings_obj.last_modified_by = request.user.email
            settings_obj.save()

            # Log successful update
            log_audit_event('UPDATE', request, success=True, changes=changes)

            messages.success(request, 'Tampilan berhasil diperbarui!')
            return redirect('customize')
        else:
            # Log failed validation attempt
            log_audit_event(
                'UPDATE',
                request,
                success=False,
                changes={'errors': dict(form.errors)}
            )

            # Display validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        # Log view access
        log_audit_event('VIEW', request, success=True)
        form = SiteSettingsForm(instance=site_cfg)

    return render(request, 'customize.html', {
        'page_title': 'Kustomisasi Tampilan',
        'site_cfg': site_cfg,
        'form': form,
        'font_choices': SiteSettings._meta.get_field('font_family').choices,
    })
