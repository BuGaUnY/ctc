
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
from django_filters import FilterSet, RangeFilter, DateRangeFilter, DateFilter, ChoiceFilter
from django_filters.views import FilterView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from .forms import ProfileForm
from django.shortcuts import render, get_object_or_404, redirect
from .models import Profile
import django_filters
import qrcode
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from activity.models import AttendanceCheckin
import logging
from django.http import HttpResponse, HttpResponseForbidden
from linebot import WebhookHandler
from linebot.exceptions import InvalidSignatureError
from projectmanager import settings
from django.contrib.auth import login, get_backends
from django.core.signing import Signer, BadSignature
from django.contrib.auth.models import User
from .forms import ProfileFormSet

# Logging setup
logger = logging.getLogger(__name__)
handler = WebhookHandler(settings.channel_secret)

def auto_login_view(request):
    signer = Signer()
    signed_uid = request.GET.get('uid')
    next_url = request.GET.get('next', '/')

    if not signed_uid:
        return HttpResponse("Missing UID", status=400)

    try:
        uid = signer.unsign(signed_uid)
        user = User.objects.get(pk=uid)

        # ✅ เพิ่มบรรทัดนี้เพื่อระบุ backend
        backend = get_backends()[0]  # ใช้ backend ตัวแรกที่ config ไว้
        user.backend = f"{backend.__module__}.{backend.__class__.__name__}"

        login(request, user)
        return redirect(next_url)

    except (BadSignature, User.DoesNotExist):
        return HttpResponse("Invalid login link", status=403)

@csrf_exempt
def line_webhook(request):
    if request.method != 'POST':
        logger.error("Invalid method")
        return HttpResponseForbidden("Method not allowed.")

    # อ่าน Signature และ Body
    signature = request.headers.get('X-Line-Signature', '')
    body = request.body.decode('utf-8')

    try:
        # ตรวจสอบ Signature
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature. Verification failed.")
        return HttpResponseForbidden("Invalid signature.")
    except Exception as e:
        # Log ข้อผิดพลาดที่ไม่คาดคิด
        logger.exception("Unexpected error occurred.")
        return HttpResponse(status=500)  # ยังคงแจ้งว่าเกิดข้อผิดพลาด

    return HttpResponse(status=200)

class ProfileDetail(LoginRequiredMixin, TemplateView):
    template_name = 'base/profile-detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = Profile.objects.get(user=self.request.user)
        return context

class ProfileUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Profile
    template_name = 'base/profile-update.html'
    form_class = ProfileForm
    success_message = 'แก้ไขโปรไฟล์เรียบร้อยแล้ว'

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

    def get_success_url(self):
        return reverse('profile-detail')

@method_decorator(csrf_exempt, name='dispatch')  # ยกเว้น CSRF เฉพาะ View นี้
class VerifyProfile(LoginRequiredMixin, UpdateView, SuccessMessageMixin):
    template_name = 'base/verifyProfile.html'
    model = Profile
    fields = ['status']
    http_method_names = ['post', 'get']  # รองรับ POST และ GET
    success_message = 'ยืนยันโปรไฟล์เรียบร้อยแล้ว'

    def get_object(self):
        return Profile.objects.get(pk=self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        profile = self.get_object()
        try:
            profile.status = True  # เปลี่ยนสถานะเป็นยืนยัน
            profile.save()  # บันทึกในฐานข้อมูล
            messages.success(self.request, self.success_message)
            return JsonResponse({
                'success': True,
                'message': 'ยืนยันโปรไฟล์',
                'redirect_url': self.get_success_url()
            })
        except Exception as e:
            logger.error(f"Failed to verify profile: {e}")
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    def get_success_url(self):
        return reverse('profile-detail')

class BulkResetProfilesView(View):
    template_name = 'base/bulk_reset_profiles.html'

    def get(self, request):
        room = request.GET.get('room')
        department = request.GET.get('department')

        profiles = Profile.objects.all()

        if room:
            profiles = profiles.filter(room=room)
        if department:
            profiles = profiles.filter(department=department)

        # ดึง room และ department ที่ไม่ใช่ None และไม่ซ้ำ
        rooms = Profile.objects.exclude(room__isnull=True).exclude(room__exact='').values_list('room', flat=True).distinct()
        departments = Profile.objects.exclude(department__isnull=True).exclude(department__exact='').values_list('department', flat=True).distinct()

        context = {
            'profiles': profiles,
            'rooms': rooms,
            'departments': departments,
            'selected_room': room,
            'selected_department': department,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        profile_ids = request.POST.getlist('profile_ids')
        Profile.objects.filter(pk__in=profile_ids).update(
            degree=None,
            room=None,
            department=None,
            status=False
        )
        return redirect('teacher')

class BulkEditProfilesView(View):
    template_name = 'base/bulk_edit_profiles.html'

    def get_queryset(self, request):
        room = request.GET.get('room')
        department = request.GET.get('department')

        queryset = Profile.objects.all()

        if room:
            queryset = queryset.filter(room=room)
        if department:
            queryset = queryset.filter(department=department)

        queryset = queryset.order_by('room', 'department', 'student_number')
        return queryset

    def get(self, request):
        room = request.GET.get('room')
        department = request.GET.get('department')

        # แสดงข้อมูลก็ต่อเมื่อมีการกรองห้องหรือแผนก
        if room or department:
            queryset = self.get_queryset(request)
        else:
            queryset = Profile.objects.none()

        formset = ProfileFormSet(queryset=queryset)

        room_list = Profile.objects.order_by('room').values_list('room', flat=True).distinct()
        department_list = Profile.objects.order_by('department').values_list('department', flat=True).distinct()

        context = {
            'formset': formset,
            'room': room,
            'department': department,
            'room_list': room_list,
            'department_list': department_list,
            'show_formset': bool(room or department),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        queryset = self.get_queryset(request)
        formset = ProfileFormSet(request.POST, request.FILES, queryset=queryset)

        room_list = Profile.objects.order_by('room').values_list('room', flat=True).distinct()
        department_list = Profile.objects.order_by('department').values_list('department', flat=True).distinct()

        if formset.is_valid():
            formset.save()
            messages.success(request, 'อัปเดตข้อมูลเรียบร้อยแล้ว')
            return redirect('bulk_edit_profiles')

        context = {
            'formset': formset,
            'room': request.GET.get('room', ''),
            'department': request.GET.get('department', ''),
            'room_list': room_list,
            'department_list': department_list,
            'show_formset': True,
        }
        return render(request, self.template_name, context)