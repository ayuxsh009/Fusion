from __future__ import absolute_import, unicode_literals

from celery import shared_task

from .services import generate_bill


@shared_task
def generate_mess_bill():
    """
    Celery periodic task: generate monthly mess bills for all registered students.
    Should be scheduled to run on the 1st of each month via CELERY_BEAT_SCHEDULE.
    """
    generate_bill()
