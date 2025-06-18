from django.contrib import admin
from .models import DownloadOperation

@admin.register(DownloadOperation)
class DownloadOperationAdmin(admin.ModelAdmin):
    list_display = ('video_url', 'ip_address', 'timestamp')
    search_fields = ('video_url', 'ip_address')
    list_filter = ('timestamp',)