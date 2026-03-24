from django.urls import path

from . import views

urlpatterns = [
    path("feedbackApi/", views.FeedbackApi.as_view(), name="feedbackApi"),
    path("menuChangeRequestApi/", views.Menu_change_requestApi.as_view(), name="menuChangeRequestApi"),
    path("messMinutesApi/", views.Mess_minutesApi.as_view(), name="messMinutesApi"),
    path("specialRequestApi/", views.Special_requestApi.as_view(), name="specialRequestApi"),
    path("messMeetingApi/", views.Mess_meetingApi.as_view(), name="messMeetingApi"),
    path("vacationFoodApi/", views.Vacation_foodApi.as_view(), name="vacationFoodApi"),
    path("messInfoApi/", views.MessinfoApi.as_view(), name="messInfoApi"),
    path("rebateApi/", views.RebateApi.as_view(), name="rebateApi"),
    path("menuApi/", views.MenuApi.as_view(), name="menuApi"),
    path("paymentsApi/", views.PaymentsApi.as_view(), name="paymentsApi"),
    path("monthlyBillApi/", views.Monthly_billApi.as_view(), name="monthlyBillApi"),
    path("messBillBaseApi/", views.MessBillBaseApi.as_view(), name="messBillBaseApi"),
    path("messRegApi/", views.Mess_regApi.as_view(), name="messRegApi"),
    path("get_mess_students/", views.Get_Filtered_Students.as_view(), name="get_mess_students"),
    path("get_reg_records/", views.Get_Reg_Records.as_view(), name="reg_record_API"),
    path("get_student_bill/", views.Get_Student_bill.as_view(), name="student_bill_API"),
    path("get_student_payment/", views.Get_Student_Payments.as_view(), name="student_payment_API"),
    path("get_student_all_details/", views.Get_Student_Details.as_view(), name="get_student_details_API"),
    path("registrationRequestApi/", views.RegistrationRequestApi.as_view(), name="registrationRequestApi"),
    path("deRegistrationRequestApi/", views.DeregistrationRequestApi.as_view(), name="deRegistrationRequestApi"),
    path("updatePaymentRequestApi/", views.UpdatePaymentRequestApi.as_view(), name="updatePaymentRequestApi"),
    path("get_mess_balance_statusApi/", views.Get_Mess_Balance_Status.as_view(), name="get_mess_balance_statusApi"),
    path("updateBillExcelApi/", views.UpdateBillExcelAPI.as_view(), name="updateBillExcelApi"),
    path("announcementApi/", views.AnnouncementApi.as_view(), name="announcementApi"),
    path("adminMessManagementApi/", views.AdminMessManagementApi.as_view(), name="adminMessManagementApi"),
    path("menuPollApi/", views.MenuPollApi.as_view(), name="menuPollApi"),
    path("vacationSurveyApi/", views.VacationSurveyApi.as_view(), name="vacationSurveyApi"),
]
