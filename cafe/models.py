from django.db import models
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.models import Student
from core.models import Grade, School

class SchoolCharge(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    meta_data = models.JSONField(default=dict, blank=True)
    grades = models.ManyToManyField(Grade)

    class Meta:
        verbose_name = "School Charge"
        verbose_name_plural = "School Charges"

    def __str__(self):
        return f"{self.name} - {self.school.name}"

    def get_bundle_amount(self, period):
        """
        Supported metadata shape:
        {
          "full_amounts": {
            "between": 30,
            "weekly": 120,
            "monthly": 600,
            "termly": 1500
          }
        }
        """
        period = (period or "").strip().lower()
        alias_map = {
            "week": "weekly",
            "month": "monthly",
            "term": "termly",
        }
        period = alias_map.get(period, period)
        full_amounts = (self.meta_data or {}).get("full_amounts", {})
        if not isinstance(full_amounts, dict):
            return None
        value = full_amounts.get(period)
        if value is None:
            return None
        try:
            amount = Decimal(str(value))
        except Exception:
            return None
        if amount <= 0:
            return None
        return amount

    def get_savings_for_period(self, period, expected_days):
        bundle_amount = self.get_bundle_amount(period)
        if bundle_amount is None:
            return Decimal("0")

        try:
            days = Decimal(str(expected_days))
        except Exception:
            return Decimal("0")

        normal_total = self.amount * days
        savings = normal_total - bundle_amount
        return savings if savings > 0 else Decimal("0")


class LunchSubscription(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="lunch_subscriptions")
    school_charge = models.ForeignKey(SchoolCharge, on_delete=models.PROTECT, related_name="subscriptions")
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    notes = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_lunch_subscriptions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lunch Subscription"
        verbose_name_plural = "Lunch Subscriptions"
        ordering = ["-end_date", "-start_date"]

    def __str__(self):
        return f"{self.student.get_full_name()} ({self.start_date} to {self.end_date})"

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("End date must be on or after start date.")

    @property
    def has_expired(self):
        return timezone.now().date() > self.end_date

    @property
    def days_remaining(self):
        remaining = (self.end_date - timezone.now().date()).days
        return remaining if remaining > 0 else 0