"""
Activity Logging Utility
Centralized helper for recording administrative actions throughout the system.
"""
from django.utils import timezone


def log_activity(user, action, category, description="", target_model="", target_id=None, extra_data=None):
    """
    Create an activity log entry.
    
    Args:
        user: The MyUser who performed the action
        action: Short action verb (e.g. 'Created', 'Deleted', 'Updated')
        category: Functional category for filtering (e.g. 'Student', 'Finance', 'Exam')
        description: Human-readable detail of what happened
        target_model: The model name affected (e.g. 'Student', 'Payment')
        target_id: PK of the affected object
        extra_data: Optional dict of additional context
    """
    from core.models import ActivityLog
    
    try:
        ActivityLog.objects.create(
            user=user,
            action=action,
            category=category,
            description=description,
            target_model=target_model,
            target_id=target_id,
            ip_address=None,  # Can be enhanced later with request.META
            extra_data=extra_data or {},
        )
    except Exception:
        # Never let logging break the main flow
        pass
