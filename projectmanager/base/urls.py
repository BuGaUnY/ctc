
from django.urls import path
from . import views
from django.urls import register_converter, path

# สร้างตัวแปลงสำหรับ UUID หรือ Integer
class IntOrUUIDConverter:
    regex = '[0-9]+|[a-f0-9-]{36}'
    
    def to_python(self, value):
        try:
            return int(value)
        except ValueError:
            return value

    def to_url(self, value):
        return str(value)

# ลงทะเบียนตัวแปลง
register_converter(IntOrUUIDConverter, 'int_or_uuid')

urlpatterns = [
    path('auto-login/', views.auto_login_view, name='auto-login'),
    path('profile/', views.ProfileDetail.as_view(), name='profile-detail'),
    path('profile/update/', views.ProfileUpdate.as_view(), name='profile-update'),
    path('profile/verify/<int_or_uuid:pk>/', views.VerifyProfile.as_view(), name='profile-verify'),
    path('webhook/', views.line_webhook, name='line_webhook'),
    path('profiles/bulk-reset/', views.BulkResetProfilesView.as_view(), name='bulk_reset_profiles'),
    path('profiles/bulk-edit/', views.BulkEditProfilesView.as_view(), name='bulk_edit_profiles'),
]