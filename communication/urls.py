from django.urls import path
from . import views

app_name = 'communication'

urlpatterns = [
    path('', views.notification_dashboard, name='dashboard'),
    path('delete/<int:pk>/', views.delete_notification, name='delete-notification'),
    path('payments/', views.payment_notifications_list, name='payment-notifications'),
    path('my-notifications/', views.guardian_notification_list, name='guardian-notifications'),
    path('ajax/recipients-count/', views.get_recipients_count, name='recipients-count'),
    path('send-results/', views.send_results_sms, name='send-results'),
    path('resend/<int:pk>/', views.resend_notification, name='resend-notification'),
    path('attendance-logs/', views.attendance_sms_logs, name='attendance-sms-logs'),
]
