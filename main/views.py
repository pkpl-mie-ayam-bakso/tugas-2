from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SiteSettings
from .context_processors import _is_group_member


def index(request):
    return render(request, 'index.html', {'page_title': 'Beranda'})


def customize(request):
    # AUTHENTICATION
    if not request.user.is_authenticated:
        messages.error(request, 'Kamu harus login terlebih dahulu.')
        return redirect('/')

    # AUTHORIZATION
    if not _is_group_member(request):
        messages.error(request, 'Akses ditolak. Hanya anggota kelompok yang dapat mengubah tampilan.')
        return redirect('/')

    site_cfg = SiteSettings.get_settings()

    if request.method == 'POST':
        site_cfg.primary_color    = request.POST.get('primary_color',    site_cfg.primary_color)
        site_cfg.secondary_color  = request.POST.get('secondary_color',  site_cfg.secondary_color)
        site_cfg.background_color = request.POST.get('background_color', site_cfg.background_color)
        site_cfg.text_color       = request.POST.get('text_color',       site_cfg.text_color)
        site_cfg.card_color       = request.POST.get('card_color',       site_cfg.card_color)
        site_cfg.font_family      = request.POST.get('font_family',      site_cfg.font_family)
        site_cfg.font_size_base   = int(request.POST.get('font_size_base', site_cfg.font_size_base))
        site_cfg.last_modified_by = request.user.email
        site_cfg.save()
        messages.success(request, 'Tampilan berhasil diperbarui!')
        return redirect('customize')

    return render(request, 'customize.html', {
        'page_title': 'Kustomisasi Tampilan',
        'site_cfg':   site_cfg,
        'font_choices': SiteSettings._meta.get_field('font_family').choices,
    })