from django.urls import path
from .views import AttendanceLogUploadView, school_late_time_rules, late_time_rule_update, late_time_rule_delete


app_name = 'attendance'

urlpatterns = [
    path('logs/', AttendanceLogUploadView.as_view(), name='attendance-logs-upload'),
    path('late-rules/', school_late_time_rules, name='late-rules-list'),
    path('late-rules/<int:pk>/update/', late_time_rule_update, name='late-rule-update'),
    path('late-rules/<int:pk>/delete/', late_time_rule_delete, name='late-rule-delete'),
]


