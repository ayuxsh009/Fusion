from __future__ import absolute_import, unicode_literals

from celery import shared_task

from .services import (
    apply_monthly_bill_policies,
    auto_close_expired_polls,
    create_feedback_report_snapshot,
    escalate_stale_rebates,
    generate_bill,
)


@shared_task
def generate_mess_bill():
    """
    Celery periodic task: generate monthly mess bills for all registered students.
    Should be scheduled to run on the 1st of each month via CELERY_BEAT_SCHEDULE.
    """
    generate_bill()


@shared_task
def run_mess_policy_jobs():
    """
    Periodic policy tasks:
    - Close expired polls
    - Escalate stale rebate requests
    - Apply payment grace/late-fee rules
    """
    auto_close_expired_polls()
    escalate_stale_rebates()
    apply_monthly_bill_policies()


@shared_task
def generate_weekly_feedback_report():
    """
    Weekly feedback report generation and notification.
    """
    create_feedback_report_snapshot()
