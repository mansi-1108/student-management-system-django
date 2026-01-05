from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import (login_required,permission_required,user_passes_test)
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q, Avg, Count
import csv
from openpyxl import Workbook
from .models import Student, Subject, ActivityLog
from .utils import log_activity, get_client_ip
# =========================
# Helper
# =========================
def is_admin(user):
    return user.groups.filter(name='Admin').exists()


def get_students_for_user(user):
    if user.groups.filter(name='Admin').exists():
        return Student.objects.all()
    elif user.groups.filter(name='Teacher').exists():
        return Student.objects.filter(user=user)
    else:
        return Student.objects.all()  # Viewer = read-only


# =========================
# Student List
# =========================
class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 5

    def get_queryset(self):
        queryset = get_students_for_user(self.request.user)

        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(roll_no__icontains=query) |
                Q(subject__name__icontains=query)
            )
        return queryset


# =========================
# Create Student
# =========================
class StudentCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CreateView
):
    model = Student
    permission_required = 'students.add_student'
    fields = ['name', 'roll_no', 'subject', 'marks']
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)

        log_activity(
            self.request.user,
            f"Added Student: {self.object.name} (Roll {self.object.roll_no})",
            action="ADD",
            request=self.request
        )
        return response


# =========================
# Update Student
# =========================
class StudentUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UpdateView
):
    model = Student
    permission_required = 'students.change_student'
    fields = ['name', 'roll_no', 'subject', 'marks']
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student_list')

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Admin').exists():
            return Student.objects.all()
        return Student.objects.filter(user=user)

    def form_valid(self, form):
        response = super().form_valid(form)

        log_activity(
            self.request.user,
            f"Updated Student: {self.object.name}",
            action="EDIT",
            request=self.request
        )
        return response

# =========================
# Delete Student (Admin only)
# =========================
class StudentDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DeleteView
):
    model = Student
    permission_required = 'students.delete_student'
    template_name = 'students/confirm_delete.html'
    success_url = reverse_lazy('student_list')

    def form_valid(self, form):
        log_activity(
            self.request.user,
            f"Deleted Student: {self.object.name} (Roll {self.object.roll_no})",
            action="DELETE",
            request=self.request
        )
        return super().form_valid(form)


# =========================
# Export CSV (Admin / Teacher)
# =========================
@login_required
@permission_required('students.add_student', raise_exception=True)
def export_students_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Roll No', 'Subject', 'Marks', 'Grade'])

    queryset = get_students_for_user(request.user)

    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query) |
            Q(roll_no__icontains=query) |
            Q(subject__name__icontains=query)
        )

    for s in queryset:
        writer.writerow([
            s.name,
            s.roll_no,
            s.subject.name,
            s.marks,
            s.grade
        ])

    ActivityLog.objects.create(
        user=request.user,
        action="EXPORT",
        description="Exported students to CSV",
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    return response


# =========================
# Export Excel (Admin / Teacher)
# =========================
@login_required
@permission_required('students.add_student', raise_exception=True)
def export_students_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Students"

    ws.append(['Name', 'Roll No', 'Subject', 'Marks', 'Grade'])

    queryset = get_students_for_user(request.user)

    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query) |
            Q(roll_no__icontains=query) |
            Q(subject__name__icontains=query)
        )

    for s in queryset:
        ws.append([
            s.name,
            s.roll_no,
            s.subject.name,
            s.marks,
            s.grade
        ])

    ActivityLog.objects.create(
        user=request.user,
        action="EXPORT",
        description="Exported students to Excel",
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=students.xlsx'
    wb.save(response)

    return response


# =========================
# Activity Logs (Admin only)
# =========================
@staff_member_required
def activity_logs(request):
    logs = ActivityLog.objects.order_by('-timestamp')
    return render(request, "students/activity_logs.html", {'logs': logs})


# =========================
# Admin Dashboard
# =========================
@staff_member_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    students = Student.objects.all()

    total_students = students.count()
    avg_marks = students.aggregate(avg=Avg('marks'))['avg']

    top_students = students.order_by('-marks')[:5]
    at_risk_students = students.filter(marks__lt=40)

    subject_avg = Subject.objects.annotate(
        avg_marks=Avg('student__marks'),
        count=Count('student')
    )

    pass_count = students.filter(marks__gte=40).count()
    fail_count = students.filter(marks__lt=40).count()
    total = pass_count + fail_count

    context = {
        'total_students': total_students,
        'avg_marks': avg_marks,
        'top_students': top_students,
        'at_risk_students': at_risk_students,
        'subject_avg': subject_avg,
        'pass_percent': round((pass_count / total) * 100, 2) if total else 0,
        'fail_percent': round((fail_count / total) * 100, 2) if total else 0,
        'grade_distribution': {
            'A+': students.filter(marks__gte=90).count(),
            'A': students.filter(marks__gte=75, marks__lt=90).count(),
            'B': students.filter(marks__gte=60, marks__lt=75).count(),
            'C': students.filter(marks__lt=60).count(),
        }
    }

    return render(request, 'students/dashboard.html', context)


