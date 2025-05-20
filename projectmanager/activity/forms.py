from django import forms
from .models import Ticket, AttendanceCheckin, Attendance, Activity, Organizer
from .models import Profile
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError

class OrganizerForm(forms.ModelForm):
    owner = forms.ModelChoiceField(
        queryset=Profile.objects.all(),
        widget=forms.Select(attrs={'class': 'searchable-select'}),
        label="ชื่อผู้ใช้"
    )

    class Meta:
        model = Organizer
        fields = '__all__'
        exclude = ['address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = "ตำแหน่ง"
        self.fields['description'].label = "รายละเอียด"
        self.fields['image'].label = "รูปภาพ"
        self.fields['email'].label = "อีเมล์"
        self.fields['phone'].label = "เบอร์โทรศัพท์"

    def clean_owner(self):
        owner = self.cleaned_data.get('owner')
        if Organizer.objects.filter(owner=owner).exists():
            raise forms.ValidationError("ไม่สามารถเพิ่มข้อมูลซ้ำได้: มีโปรไฟล์นี้อยู่แล้วในระบบ")
        return owner

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = '__all__'
        exclude = ['status']
        widgets = {
            'date_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].label = "รูปภาพ"
        self.fields['title'].label = "ชื่อกิจกรรม"
        self.fields['description'].label = "คำอธิบาย"
        self.fields['detail'].label = "รายละเอียด"
        self.fields['activity_category'].label = "หน่วยกิจ"
        self.fields['date_start'].label = "วันที่ | เวลาที่จัดกิจกรรม"

        # ตั้ง label ให้ organizer แต่ละฟิลด์
        for i in range(10):
            field_name = f'organizer{i}' if i > 0 else 'organizer'
            if field_name in self.fields:
                self.fields[field_name].label = "ผู้จัด"

    def clean(self):
        cleaned_data = super().clean()

        # ดึงค่าทุก organizer ออกมา
        organizers = []
        for i in range(10):
            field_name = f'organizer{i}' if i > 0 else 'organizer'
            organizer_value = cleaned_data.get(field_name)
            if organizer_value:
                organizers.append(organizer_value)

        # ตรวจสอบว่ามี organizer ซ้ำหรือไม่
        if len(organizers) != len(set(organizers)):
            raise ValidationError("ไม่สามารถเลือกผู้จัดซ้ำกันได้ กรุณาเลือกผู้จัดแต่ละคนให้แตกต่างกัน")

        return cleaned_data

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = '__all__'
        exclude = ['activity', 'qrcode', 'profile', 'checkin']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student_number'].label = "รหัสประจำตัว"
        self.fields['first_name'].label = "ชื่อจริง"
        self.fields['last_name'].label = "นามสกุล"
        self.fields['room'].label = "ห้อง"
        self.fields['degree'].label = "ชั้นปี"
        self.fields['department'].label = "แผนก"

        # Set fields to readonly
        for field in self.fields:
            self.fields[field].widget.attrs['readonly'] = 'readonly'

class AttendanceCheckinForm(forms.ModelForm):

    PRESENCE_CHOICES = [
        (True, 'มา'),
        (False, 'ขาด'),
    ]

    presence = forms.ChoiceField(
        choices=PRESENCE_CHOICES,
        widget=forms.Select
    )

    class Meta:
        model = AttendanceCheckin
        fields = ['student_number', 'first_name', 'last_name', 'room', 'degree', 'department', 'presence']
        widgets = {
            'student_number': forms.HiddenInput(),
            'first_name': forms.HiddenInput(),
            'last_name': forms.HiddenInput(),
            'room': forms.HiddenInput(),
            'degree': forms.HiddenInput(),
            'department': forms.HiddenInput(),
        }

AttendanceCheckinFormSet = inlineformset_factory(
    Attendance,
    AttendanceCheckin,
    form=AttendanceCheckinForm,
    extra=0,  # No extra forms initially
    can_delete=False
)

class ReportExportForm(forms.Form):
    term = forms.CharField(label='เทอม', max_length=10, required=True)
    academic_year = forms.CharField(label='ปีการศึกษา', max_length=10, required=True)

