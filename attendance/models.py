from django.db import models

class Device(models.Model):
    # We will use the database primary key (id) as the device identifier
    name = models.CharField(max_length=150)
    school = models.ForeignKey('core.School', on_delete=models.CASCADE, related_name='attendance_devices')
    created_at = models.DateTimeField(auto_now_add=True)
    last_sync = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (ID: {self.id}) - {self.school.name}"

class LateTimeRule(models.Model):
    name = models.CharField(max_length=100, help_text="e.g., Primary Section Early Start")
    school = models.ForeignKey('core.School', on_delete=models.CASCADE, related_name='late_time_rules')
    grades = models.ManyToManyField('core.Grade', related_name='late_time_rules')
    late_time = models.TimeField(help_text="Time after which attendance is marked as 'Late'")

    def __str__(self):
        return f"{self.name} - {self.late_time} ({self.school.name})"


