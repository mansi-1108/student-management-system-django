from django.urls import path
from .views import export_students_csv, export_students_excel
from .views import activity_logs
from .views import admin_dashboard

from .views import (
    StudentListView,
    StudentCreateView,
    StudentUpdateView,
    StudentDeleteView,
)

urlpatterns = [
    path('', StudentListView.as_view(), name='student_list'),
    path('add/', StudentCreateView.as_view(), name='student_add'),
    path('edit/<int:pk>/', StudentUpdateView.as_view(), name='student_edit'),
    path('delete/<int:pk>/', StudentDeleteView.as_view(), name='student_delete'),
    path('export/csv/', export_students_csv, name='export_students_csv'),
    path('export/excel/', export_students_excel, name='export_students_excel'),
    path('activity-logs/', activity_logs, name='activity_logs'),
    path('dashboard/',admin_dashboard,name='admin_dashboard'),
]