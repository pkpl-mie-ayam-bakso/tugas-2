import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django_ratelimit.decorators import ratelimit
from django.http import JsonResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import SiteSettings
from .forms import SiteSettingsForm
from .context_processors import _is_group_member
from .utils import log_audit_event


def index(request):
    """Display group biodata (public page)."""
    return render(request, 'index.html', {'page_title': 'Beranda'})


@ratelimit(key='user', rate='20/m', method='GET', block=True)
def customize(request):
    """Customize site appearance (authorized members only)."""
    
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

    # Log view access
    log_audit_event('VIEW', request, success=True)

    site_cfg = SiteSettings.get_settings()
    form = SiteSettingsForm(instance=site_cfg)

    # Generate JWT Token untuk dikirim ke frontend
    refresh = RefreshToken.for_user(request.user)
    access_token = str(refresh.access_token)

    return render(request, 'customize.html', {
        'page_title': 'Kustomisasi Tampilan',
        'site_cfg': site_cfg,
        'form': form,
        'access_token': access_token, 
        'font_choices': SiteSettings._meta.get_field('font_family').choices,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated]) # Ini adalah validasi JWT dari DRF
def update_settings_api(request):
    """API Endpoint to update site settings securely via JWT."""
    
    # Authorization validation (RBAC)
    if not _is_group_member(request):
        log_audit_event('FAILED_AUTH', request, success=False, changes={'reason': 'API attempt by non-member'})
        return JsonResponse({'error': 'Akses ditolak. Anda bukan anggota kelompok.'}, status=403)
    
    try:
        # Retrieve JSON data from request
        data = request.data
        site_cfg = SiteSettings.get_settings()
        
        # Validation and simple update logic
        fields_to_update = ['primary_color', 'secondary_color', 'background_color', 'text_color', 'card_color', 'font_family', 'font_size_base']
        changes = {}
        
        for field in fields_to_update:
            if field in data:
                old_val = getattr(site_cfg, field)
                new_val = data[field]
                if old_val != new_val:
                    setattr(site_cfg, field, new_val)
                    changes[field] = {'old': str(old_val), 'new': str(new_val)}
        
        if changes:
            site_cfg.last_modified_by = request.user.email
            site_cfg.save()
            # Log the update in the audit trail
            log_audit_event('UPDATE', request, success=True, changes=changes)
            
        return JsonResponse({'message': 'Tema berhasil diperbarui!'}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)