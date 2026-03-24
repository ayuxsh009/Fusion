"""
Central Mess selector layer.

Read/query helpers live here to keep ORM access centralized and reusable.
"""

from django.shortcuts import get_object_or_404

from applications.academic_information.models import Student
from applications.globals.models import ExtraInfo, HoldsDesignation

from .models import (
    Announcement,
    Deregistration_Request,
    MenuPoll,
    MenuPollVote,
    VacationSurvey,
    VacationSurveyResponse,
    Feedback,
    Menu,
    Menu_change_request,
    Mess_meeting,
    Mess_minutes,
    Mess_reg,
    MessBillBase,
    Messinfo,
    Monthly_bill,
    Payments,
    Rebate,
    Reg_main,
    Reg_records,
    Registration_Request,
    Special_request,
    Update_Payment,
    Vacation_food,
)


# ---------------------------------------------------------------------------
# Auth / User helpers
# ---------------------------------------------------------------------------

def get_student_from_request_user(user):
    """Return Student row for authenticated Django user."""
    info = get_object_or_404(ExtraInfo, user=user)
    return get_object_or_404(Student, id=info.id)


def get_user_designation_names(user):
    return list(
        HoldsDesignation.objects.select_related("designation")
        .filter(user=user)
        .values_list("designation__name", flat=True)
    )


# ---------------------------------------------------------------------------
# Messinfo
# ---------------------------------------------------------------------------

def get_messinfo_queryset(student=None):
    qs = Messinfo.objects.all()
    if student is not None:
        qs = qs.filter(student_id=student)
    return qs


# ---------------------------------------------------------------------------
# Mess Registration Window
# ---------------------------------------------------------------------------

def get_mess_reg_queryset():
    return Mess_reg.objects.all()


# ---------------------------------------------------------------------------
# Mess Bill Base
# ---------------------------------------------------------------------------

def get_mess_bill_base_queryset():
    return MessBillBase.objects.all()


# ---------------------------------------------------------------------------
# Monthly Bill
# ---------------------------------------------------------------------------

def get_monthly_bill_queryset(student=None):
    qs = Monthly_bill.objects.all()
    if student is not None:
        qs = qs.filter(student_id=student)
    return qs


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------

def get_payments_queryset(student=None):
    qs = Payments.objects.all()
    if student is not None:
        qs = qs.filter(student_id=student)
    return qs


# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------

def get_menu_queryset(mess_option=None):
    qs = Menu.objects.all()
    if mess_option:
        qs = qs.filter(mess_option=mess_option)
    return qs


# ---------------------------------------------------------------------------
# Rebate
# ---------------------------------------------------------------------------

def get_rebate_queryset(student=None):
    qs = Rebate.objects.all()
    if student is not None:
        qs = qs.filter(student_id=student)
    return qs


# ---------------------------------------------------------------------------
# Vacation Food
# ---------------------------------------------------------------------------

def get_vacation_food_queryset(student=None):
    qs = Vacation_food.objects.all()
    if student is not None:
        qs = qs.filter(student_id=student)
    return qs


# ---------------------------------------------------------------------------
# Special Request
# ---------------------------------------------------------------------------

def get_special_request_queryset(student=None):
    qs = Special_request.objects.all()
    if student is not None:
        qs = qs.filter(student_id=student)
    return qs


# ---------------------------------------------------------------------------
# Mess Meeting & Minutes
# ---------------------------------------------------------------------------

def get_mess_meeting_queryset():
    return Mess_meeting.objects.all()


def get_mess_minutes_queryset():
    return Mess_minutes.objects.all()


# ---------------------------------------------------------------------------
# Menu Change Request
# ---------------------------------------------------------------------------

def get_menu_change_request_queryset():
    return Menu_change_request.objects.all()


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------

def get_feedback_queryset(student=None):
    qs = Feedback.objects.all()
    if student is not None:
        qs = qs.filter(student_id=student)
    return qs


# ---------------------------------------------------------------------------
# Registration / Deregistration Requests
# ---------------------------------------------------------------------------

def get_registration_request_queryset(student=None, status=None):
    qs = Registration_Request.objects.all()
    if student is not None:
        qs = qs.filter(student_id=student)
    if status:
        qs = qs.filter(status=status)
    return qs


def get_deregistration_request_queryset(student=None, status=None):
    qs = Deregistration_Request.objects.all()
    if student is not None:
        qs = qs.filter(student_id=student)
    if status:
        qs = qs.filter(status=status)
    return qs


def get_update_payment_request_queryset(student=None, status=None):
    qs = Update_Payment.objects.all()
    if student is not None:
        qs = qs.filter(student_id=student)
    if status:
        qs = qs.filter(status=status)
    return qs


# ---------------------------------------------------------------------------
# Reg_main (student mess status)
# ---------------------------------------------------------------------------

def get_reg_main_for_student(student):
    """Return Reg_main for student, or None if not found."""
    return Reg_main.objects.filter(student_id=student).first()


def get_reg_main_queryset(status=None, program=None, mess_option=None):
    """Filtered queryset for the caretaker student list view."""
    qs = Reg_main.objects.select_related(
        "student_id",
        "student_id__id",
        "student_id__id__user",
        "student_id__id__department",
    ).all()
    if status and status != "all":
        qs = qs.filter(current_mess_status=status)
    if program and program != "all":
        qs = qs.filter(program=program)
    if mess_option and mess_option != "all":
        qs = qs.filter(mess_option=mess_option)
    return qs


def get_reg_main_by_student_id(student_id):
    """Return a single Reg_main row with related data; raises DoesNotExist if missing."""
    return Reg_main.objects.select_related(
        "student_id",
        "student_id__id",
        "student_id__id__user",
        "student_id__id__department",
    ).get(student_id=student_id)


# ---------------------------------------------------------------------------
# Reg_records
# ---------------------------------------------------------------------------

def get_reg_records_queryset(student=None):
    qs = Reg_records.objects.all()
    if student is not None:
        qs = qs.filter(student_id=student)
    return qs


# ---------------------------------------------------------------------------
# Announcements
# ---------------------------------------------------------------------------

def get_announcement_queryset(mess_option=None):
    qs = Announcement.objects.select_related("created_by", "created_by__user").all()
    if mess_option and mess_option != "all":
        qs = qs.filter(mess_option__in=[mess_option, "all"])
    return qs


# ---------------------------------------------------------------------------
# Menu Poll
# ---------------------------------------------------------------------------

def get_poll_queryset(mess_option=None, active_only=False):
    qs = MenuPoll.objects.prefetch_related("votes").all()
    if mess_option and mess_option != "all":
        qs = qs.filter(mess_option__in=[mess_option, "all"])
    if active_only:
        qs = qs.filter(is_active=True)
    return qs


# ---------------------------------------------------------------------------
# Vacation Survey
# ---------------------------------------------------------------------------

def get_vacation_survey_queryset(mess_option=None, active_only=False):
    qs = VacationSurvey.objects.prefetch_related("responses").all()
    if mess_option and mess_option != "all":
        qs = qs.filter(mess_option__in=[mess_option, "all"])
    if active_only:
        qs = qs.filter(is_active=True)
    return qs
