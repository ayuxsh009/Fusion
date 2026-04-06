from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from applications.central_mess.selectors import (
    get_access_violation_queryset,
    get_announcement_queryset,
    get_audit_log_queryset,
    get_deregistration_request_queryset,
    get_feedback_report_queryset,
    get_poll_queryset,
    get_refund_ledger_queryset,
    get_refund_request_queryset,
    get_role_assignment_queryset,
    get_role_transfer_log_queryset,
    get_special_event_meal_queryset,
    get_vacation_survey_queryset,
    get_feedback_queryset,
    get_menu_change_request_queryset,
    get_menu_queryset,
    get_mess_bill_base_queryset,
    get_mess_meeting_queryset,
    get_mess_minutes_queryset,
    get_mess_reg_queryset,
    get_messinfo_queryset,
    get_monthly_bill_queryset,
    get_payments_queryset,
    get_rebate_queryset,
    get_reg_main_by_student_id,
    get_reg_main_for_student,
    get_reg_main_queryset,
    get_reg_records_queryset,
    get_registration_request_queryset,
    get_special_request_queryset,
    get_student_from_request_user,
    get_user_designation_names,
    get_update_payment_request_queryset,
    get_vacation_food_queryset,
)
from applications.central_mess.services import (
    apply_monthly_bill_policies,
    assign_mess_role,
    auto_close_expired_polls,
    cancel_refund_request,
    CentralMessServiceError,
    create_feedback_report_snapshot,
    create_refund_request,
    create_special_event_meal,
    RebateOverlapError,
    admin_deregister_all_from_mess,
    admin_bulk_register_students,
    admin_deregister_student,
    admin_register_student,
    close_menu_poll,
    delete_menu_poll,
    create_announcement,
    create_menu_poll,
    create_vacation_survey,
    submit_poll_vote,
    submit_survey_response,
    create_deregistration_request,
    create_feedback,
    create_menu,
    create_menu_change_request,
    create_mess_bill_base,
    create_mess_meeting,
    create_mess_minutes,
    create_messinfo,
    create_mess_reg,
    create_monthly_bill,
    create_rebate,
    create_registration_request,
    create_special_request,
    create_update_payment_request,
    create_vacation_food,
    delete_deregistration_request,
    decide_deregistration_request,
    decide_refund_request,
    decide_registration_request,
    decide_update_payment_request,
    delete_announcement,
    delete_special_event_meal,
    delete_vacation_survey,
    delete_feedback,
    enforce_read_access,
    escalate_stale_rebates,
    process_excel_bill_update,
    update_feedback_status,
    update_menu_items,
    update_rebate_status,
    update_special_request_status,
    update_vacation_food_status,
)

from .serializers import (
    AccessViolationLogSerializer,
    AnnouncementSerializer,
    AuditLogSerializer,
    FeedbackReportSerializer,
    MenuPollSerializer,
    MenuPollVoteSerializer,
    RefundCancelSerializer,
    RefundDecisionSerializer,
    RefundLedgerSerializer,
    RefundRequestSerializer,
    RoleAssignmentActionSerializer,
    RoleAssignmentSerializer,
    RoleTransferLogSerializer,
    SpecialEventMealSerializer,
    VacationSurveySerializer,
    VacationSurveyResponseSerializer,
    DeregistrationDecisionSerializer,
    DeregistrationDeleteSerializer,
    DeregistrationRequestSerializer,
    FeedbackSerializer,
    FeedbackStatusUpdateSerializer,
    GetFilteredSerialzer,
    MenuSerializer,
    Menu_change_requestSerializer,
    Mess_meetingSerializer,
    Mess_minutesSerializer,
    Mess_regSerializer,
    MessBillBaseSerializer,
    MessinfoSerializer,
    Monthly_billSerializer,
    PaymentsSerializer,
    RebateSerializer,
    RebateStatusUpdateSerializer,
    RegistrationDecisionSerializer,
    RegistrationRequestSerializer,
    Special_requestSerializer,
    SpecialRequestStatusUpdateSerializer,
    UpdatePaymentDecisionSerializer,
    UpdatePaymentRequestSerializer,
    Vacation_foodSerializer,
    VacationFoodStatusUpdateSerializer,
    reg_recordSerialzer,
)

MANAGEMENT_READ_ROLES = {"mess_manager", "mess_warden", "mess_admin"}


def _designation_set(user):
    return {str(name).strip().lower() for name in get_user_designation_names(user)}


class FeedbackApi(APIView):

    def get(self, request):
        roles = _designation_set(request.user)
        if roles.intersection(MANAGEMENT_READ_ROLES):
            feedback_obj = get_feedback_queryset()
        else:
            student = get_student_from_request_user(request.user)
            feedback_obj = get_feedback_queryset(student=student)
        serialized_obj = FeedbackSerializer(feedback_obj, many=True)
        return Response({'status': 200, 'payload': serialized_obj.data})

    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            create_feedback(serializer.validated_data, request_user=request.user)
            return Response({'status': 200})
        return Response(serializer.errors, status=400)

    def put(self, request):
        serializer = FeedbackStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            update_feedback_status(serializer.validated_data)
            return Response({'status': 200})
        return Response(serializer.errors, status=400)

    def delete(self, request):
        try:
            delete_feedback(request.data)
            return Response({'status': 200, 'message': 'Feedback deleted successfully.'})
        except Exception:
            return Response({'error': 'Feedback not found.'}, status=404)


class MessinfoApi(APIView):

    def get(self, request):
        messinfo_obj = get_messinfo_queryset()
        serialized_obj = MessinfoSerializer(messinfo_obj, many=True)
        return Response({'status': 200, 'payload': serialized_obj.data})

    def post(self, request):
        serializer = MessinfoSerializer(data=request.data)
        if serializer.is_valid():
            create_messinfo(serializer.validated_data, request_user=request.user)
            return Response({'status': 200})
        return Response(serializer.errors, status=400)


class Mess_regApi(APIView):

    def get(self, request):
        mess_reg_obj = get_mess_reg_queryset()
        serialized_obj = Mess_regSerializer(mess_reg_obj, many=True)
        return Response({'status': 200, 'payload': serialized_obj.data})

    def post(self, request):
        serializer = Mess_regSerializer(data=request.data)
        if serializer.is_valid():
            create_mess_reg(serializer.validated_data)
            return Response({'status': 200})
        return Response(serializer.errors, status=400)


class MessBillBaseApi(APIView):

    def get(self, request):
        messBillBase_obj = get_mess_bill_base_queryset()
        serialized_obj = MessBillBaseSerializer(messBillBase_obj, many=True)
        return Response({'status': 200, 'payload': serialized_obj.data})

    def post(self, request):
        serializer = MessBillBaseSerializer(data=request.data)
        if serializer.is_valid():
            create_mess_bill_base(serializer.validated_data)
            return Response({'status': 200})
        return Response(serializer.errors, status=400)


class Monthly_billApi(APIView):

    def get(self, request):
        apply_monthly_bill_policies()
        roles = _designation_set(request.user)
        if roles.intersection(MANAGEMENT_READ_ROLES):
            monthly_bill_obj = get_monthly_bill_queryset()
        else:
            student = get_student_from_request_user(request.user)
            monthly_bill_obj = get_monthly_bill_queryset(student=student)
        serialized_obj = Monthly_billSerializer(monthly_bill_obj, many=True)
        return Response({'status': 200, 'payload': serialized_obj.data})

    def post(self, request):
        serializer = Monthly_billSerializer(data=request.data)
        if serializer.is_valid():
            create_monthly_bill(serializer.validated_data)
            return Response({'status': 200})
        return Response(serializer.errors, status=400)


class PaymentsApi(APIView):

    def get(self, request):
        student = get_student_from_request_user(request.user)
        payments_obj = get_payments_queryset(student=student)
        serialized_obj = PaymentsSerializer(payments_obj, many=True)
        return Response({'status': 200, 'payload': serialized_obj.data})


class MenuApi(APIView):

    def get(self, request):
        menu_obj = get_menu_queryset()
        serialized_obj = MenuSerializer(menu_obj, many=True)
        return Response({'status': 200, 'payload': serialized_obj.data})

    def post(self, request):
        serializer = MenuSerializer(data=request.data)
        if serializer.is_valid():
            create_menu(serializer.validated_data)
            return Response({'status': 200})
        return Response(serializer.errors, status=400)

    def put(self, request):
        mess_option = request.data.get('mess_option')
        items = request.data.get('items', [])
        if not mess_option or not items:
            return Response({'error': 'mess_option and items are required'}, status=400)
        try:
            update_menu_items(mess_option, items, request_user=request.user)
        except CentralMessServiceError as exc:
            return Response({'error': str(exc)}, status=exc.status_code)
        return Response({'status': 200})


class RebateApi(APIView):

    def get(self, request):
        escalate_stale_rebates()
        roles = _designation_set(request.user)
        if roles.intersection(MANAGEMENT_READ_ROLES):
            rebate_obj = get_rebate_queryset()
        else:
            student = get_student_from_request_user(request.user)
            rebate_obj = get_rebate_queryset(student=student)
        serialized_obj = RebateSerializer(rebate_obj, many=True)
        return Response({'status': 200, 'payload': serialized_obj.data})

    def post(self, request):
        serializer = RebateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                create_rebate(serializer.validated_data, request_user=request.user)
            except RebateOverlapError as exc:
                return Response(exc.payload or {'message': exc.message})
            return Response({'status': 200})
        return Response(serializer.errors, status=400)

    def put(self, request):
        serializer = RebateStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                update_rebate_status(serializer.validated_data, request_user=request.user)
            except CentralMessServiceError as exc:
                return Response({'error': str(exc)}, status=exc.status_code)
            return Response({'status': 200})
        return Response(serializer.errors, status=400)


class Vacation_foodApi(APIView):

    def get(self, request):
        roles = _designation_set(request.user)
        if roles.intersection(MANAGEMENT_READ_ROLES):
            vacation_food_obj = get_vacation_food_queryset()
        else:
            student = get_student_from_request_user(request.user)
            vacation_food_obj = get_vacation_food_queryset(student=student)
        serialized_obj = Vacation_foodSerializer(vacation_food_obj, many=True)
        return Response({'status': 200, 'payload': serialized_obj.data})

    def post(self, request):
        serializer = Vacation_foodSerializer(data=request.data)
        if serializer.is_valid():
            create_vacation_food(serializer.validated_data, request_user=request.user)
            return Response({'status': 200})
        return Response(serializer.errors, status=400)

    def put(self, request):
        serializer = VacationFoodStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                update_vacation_food_status(serializer.validated_data)
            except CentralMessServiceError as exc:
                return Response({'error': exc.message}, status=exc.status_code)
            return Response({'status': 200})
        return Response(serializer.errors, status=400)


class Special_requestApi(APIView):

    def get(self, request):
        roles = _designation_set(request.user)
        if roles.intersection(MANAGEMENT_READ_ROLES):
            special_request_obj = get_special_request_queryset()
        else:
            student = get_student_from_request_user(request.user)
            special_request_obj = get_special_request_queryset(student=student)
        serialized_obj = Special_requestSerializer(special_request_obj, many=True)
        return Response({'status': 200, 'payload': serialized_obj.data})

    def post(self, request):
        serializer = Special_requestSerializer(data=request.data)
        if serializer.is_valid():
            create_special_request(serializer.validated_data, request_user=request.user)
            return Response({'status': 200})
        return Response(serializer.errors, status=400)

    def put(self, request):
        serializer = SpecialRequestStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                update_special_request_status(serializer.validated_data, request_user=request.user)
            except CentralMessServiceError as exc:
                return Response({'error': str(exc)}, status=exc.status_code)
            return Response({'status': 200})
        return Response(serializer.errors, status=400)


class Mess_meetingApi(APIView):

    def get(self, request):
        mess_meeting_obj = get_mess_meeting_queryset()
        serialized_obj = Mess_meetingSerializer(mess_meeting_obj, many=True)
        return Response({'status': 200, 'payload': serialized_obj.data})

    def post(self, request):
        serializer = Mess_meetingSerializer(data=request.data)
        if serializer.is_valid():
            create_mess_meeting(serializer.validated_data)
            return Response({'status': 200})
        return Response(serializer.errors, status=400)


class Mess_minutesApi(APIView):

    def get(self, request):
        mess_minutes_obj = get_mess_minutes_queryset()
        serialized_obj = Mess_minutesSerializer(mess_minutes_obj, many=True)
        return Response({'status': 200, 'payload': serialized_obj.data})

    def post(self, request):
        serializer = Mess_minutesSerializer(data=request.data)
        if serializer.is_valid():
            create_mess_minutes(serializer.validated_data)
            return Response({'status': 200})
        return Response(serializer.errors, status=400)


class Menu_change_requestApi(APIView):

    def get(self, request):
        menu_change_request_obj = get_menu_change_request_queryset()
        serialized_obj = Menu_change_requestSerializer(menu_change_request_obj, many=True)
        return Response({'status': 200, 'payload': serialized_obj.data})

    def post(self, request):
        try:
            create_menu_change_request(request.data, request_user=request.user)
            return Response({'status': 200})
        except CentralMessServiceError as exc:
            return Response({'error': str(exc)}, status=exc.status_code)
        except Exception as exc:
            return Response({'error': str(exc)}, status=400)


class Get_Filtered_Students(APIView):

    def post(self, request):
        enforce_read_access(
            request.user,
            endpoint="/mess/api/get_mess_students/",
            method="POST",
            allowed_designations=MANAGEMENT_READ_ROLES,
            allow_staff=True,
        )
        req_type = request.data.get('type')

        if req_type == 'filter':
            reg_main = get_reg_main_queryset(
                status=request.data.get('status'),
                program=request.data.get('program'),
                mess_option=request.data.get('mess_option'),
            )
            serialized_obj = GetFilteredSerialzer(reg_main, many=True)
            return Response({'payload': serialized_obj.data})

        elif req_type == 'search':
            student_id = str(request.data.get('student_id', '')).upper()
            try:
                reg_main = get_reg_main_by_student_id(student_id)
                serialized_obj = GetFilteredSerialzer(reg_main)
                return Response({'payload': serialized_obj.data})
            except Exception:
                return Response({'error': 'student does not exist'}, status=404)

        return Response({'error': 'invalid type'}, status=400)


class Get_Reg_Records(APIView):

    def get(self, request):
        enforce_read_access(
            request.user,
            endpoint="/mess/api/get_reg_records/",
            method="GET",
            allowed_designations=MANAGEMENT_READ_ROLES,
            allow_staff=True,
        )
        student_id = request.GET.get('student_id')
        reg_record = get_reg_records_queryset(student=student_id)
        serialized_obj = reg_recordSerialzer(reg_record, many=True)
        return Response({'payload': serialized_obj.data})


class Get_Student_bill(APIView):

    def post(self, request):
        apply_monthly_bill_policies()
        enforce_read_access(
            request.user,
            endpoint="/mess/api/get_student_bill/",
            method="POST",
            allowed_designations=MANAGEMENT_READ_ROLES,
            allow_staff=True,
        )
        student = request.data.get('student_id')
        bill_details = get_monthly_bill_queryset(student=student)
        serialized_obj = Monthly_billSerializer(bill_details, many=True)
        return Response({'payload': serialized_obj.data})


class Get_Student_Payments(APIView):

    def post(self, request):
        enforce_read_access(
            request.user,
            endpoint="/mess/api/get_student_payment/",
            method="POST",
            allowed_designations=MANAGEMENT_READ_ROLES,
            allow_staff=True,
        )
        student = request.data.get('student_id')
        payment_details = get_payments_queryset(student=student)
        serialized_obj = PaymentsSerializer(payment_details, many=True)
        return Response({'payload': serialized_obj.data})


class Get_Student_Details(APIView):

    def post(self, request):
        enforce_read_access(
            request.user,
            endpoint="/mess/api/get_student_all_details/",
            method="POST",
            allowed_designations=MANAGEMENT_READ_ROLES,
            allow_staff=True,
        )
        student = request.data.get('student_id')
        try:
            reg_main = get_reg_main_by_student_id(student)
        except Exception:
            return Response({'error': 'student does not exist'}, status=404)

        data = {
            'payment': PaymentsSerializer(
                get_payments_queryset(student=student), many=True
            ).data,
            'bill': Monthly_billSerializer(
                get_monthly_bill_queryset(student=student), many=True
            ).data,
            'reg_records': reg_recordSerialzer(
                get_reg_records_queryset(student=student), many=True
            ).data,
            'student_details': GetFilteredSerialzer(reg_main).data,
        }
        return Response({'payload': data})


class RegistrationRequestApi(APIView):

    def get(self, request):
        roles = _designation_set(request.user)
        if roles.intersection(MANAGEMENT_READ_ROLES):
            registration_requests = get_registration_request_queryset()
        else:
            student = get_student_from_request_user(request.user)
            registration_requests = get_registration_request_queryset(student=student)
        serializer = RegistrationRequestSerializer(registration_requests, many=True)
        return Response({'status': 200, 'payload': serializer.data})

    def post(self, request):
        serializer = RegistrationRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                create_registration_request(
                    serializer.validated_data, request_user=request.user
                )
                return Response({'status': 200})
            except CentralMessServiceError as exc:
                return Response({'error': str(exc)}, status=exc.status_code)
            except Exception as exc:
                return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=400)

    def put(self, request):
        serializer = RegistrationDecisionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                decide_registration_request(serializer.validated_data, request_user=request.user)
            except CentralMessServiceError as exc:
                return Response({'error': str(exc)}, status=exc.status_code)
            return Response({'status': 200})
        return Response(serializer.errors, status=400)


class DeregistrationRequestApi(APIView):

    def get(self, request):
        roles = _designation_set(request.user)
        if roles.intersection(MANAGEMENT_READ_ROLES):
            deregistration_requests = get_deregistration_request_queryset()
        else:
            student = get_student_from_request_user(request.user)
            deregistration_requests = get_deregistration_request_queryset(student=student)
        serializer = DeregistrationRequestSerializer(deregistration_requests, many=True)
        return Response({'status': 200, 'payload': serializer.data})

    def post(self, request):
        serializer = DeregistrationRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                create_deregistration_request(
                    serializer.validated_data, request_user=request.user
                )
                return Response({'status': 200})
            except CentralMessServiceError as exc:
                return Response({'error': str(exc)}, status=exc.status_code)
            except Exception as exc:
                return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=400)

    def put(self, request):
        serializer = DeregistrationDecisionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                decide_deregistration_request(serializer.validated_data, request_user=request.user)
                return Response({'status': 200})
            except CentralMessServiceError as exc:
                return Response({'error': str(exc)}, status=exc.status_code)
            except Exception as exc:
                return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=400)

    def delete(self, request):
        serializer = DeregistrationDeleteSerializer(data=request.data)
        if serializer.is_valid():
            try:
                delete_deregistration_request(
                    serializer.validated_data,
                    request_user=request.user,
                )
                return Response({'status': 200, 'message': 'Deregistration request deleted.'})
            except CentralMessServiceError as exc:
                return Response({'error': str(exc)}, status=exc.status_code)
            except Exception as exc:
                return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=400)


class UpdatePaymentRequestApi(APIView):

    def get(self, request):
        student_id = request.query_params.get('student_id')
        roles = _designation_set(request.user)
        if roles.intersection(MANAGEMENT_READ_ROLES):
            update_payment_requests = get_update_payment_request_queryset(student=student_id)
        else:
            student = get_student_from_request_user(request.user)
            update_payment_requests = get_update_payment_request_queryset(student=student)
        serializer = UpdatePaymentRequestSerializer(update_payment_requests, many=True)
        return Response({'status': 200, 'payload': serializer.data})

    def post(self, request):
        serializer = UpdatePaymentRequestSerializer(data=request.data)
        if serializer.is_valid():
            create_update_payment_request(
                serializer.validated_data, request_user=request.user
            )
            return Response({'status': 200})
        return Response(serializer.errors, status=400)

    def put(self, request):
        serializer = UpdatePaymentDecisionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                decide_update_payment_request(serializer.validated_data, request_user=request.user)
            except CentralMessServiceError as exc:
                return Response({'error': str(exc)}, status=exc.status_code)
            return Response({'status': 200})
        return Response(serializer.errors, status=400)


class UpdateBillExcelAPI(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        enforce_read_access(
            request.user,
            endpoint="/mess/api/updateBillExcelApi/",
            method="POST",
            allowed_designations=MANAGEMENT_READ_ROLES,
            allow_staff=True,
        )
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST
            )
        file = request.FILES['file']
        if not file.name.endswith(('.xlsx', '.xls')):
            return Response(
                {'error': 'Invalid file format. Only .xlsx and .xls are allowed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            process_excel_bill_update(file)
            return Response(
                {'message': 'File processed successfully'}, status=status.HTTP_200_OK
            )
        except Exception as exc:
            return Response(
                {'error': f'An error occurred: {str(exc)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class Get_Mess_Balance_Status(APIView):

    def get(self, request):
        student = get_student_from_request_user(request.user)
        mess_optn = get_reg_main_for_student(student)

        if mess_optn:
            payload = {
                'mess_option': mess_optn.mess_option,
                'current_rem_balance': mess_optn.balance,
                'current_mess_status': mess_optn.current_mess_status,
            }
        else:
            payload = {
                'mess_option': 'no-mess',
                'current_rem_balance': 0,
                'current_mess_status': 'Deregistered',
            }

        return Response({'payload': payload})


class MenuPollApi(APIView):
    """
    GET  ?mess_option=&active_only=true  — list polls
    POST {question, option1, option2, option3?, option4?, mess_option, end_date?}  — create poll (caretaker)
    PUT  {poll_id, action:"vote", selected_option}  — cast/change vote (student)
    PUT  {poll_id, action:"close"}  — close poll (caretaker)
    DELETE {poll_id}  — delete poll (caretaker)
    """

    def get(self, request):
        auto_close_expired_polls()
        mess_option = request.query_params.get("mess_option")
        active_only = request.query_params.get("active_only", "").lower() == "true"
        polls = get_poll_queryset(mess_option=mess_option, active_only=active_only)
        serializer = MenuPollSerializer(polls, many=True, context={"request": request})
        return Response({"status": 200, "payload": serializer.data})

    def post(self, request):
        serializer = MenuPollSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            try:
                poll = create_menu_poll(serializer.validated_data, request_user=request.user)
                return Response(
                    {"status": 200, "payload": MenuPollSerializer(poll, context={"request": request}).data},
                    status=status.HTTP_201_CREATED,
                )
            except CentralMessServiceError as exc:
                return Response({"error": str(exc)}, status=exc.status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        poll_id = request.data.get("poll_id")
        action = request.data.get("action")
        if not poll_id:
            return Response({"error": "poll_id is required."}, status=400)

        if action == "vote":
            selected_option = request.data.get("selected_option")
            if not selected_option:
                return Response({"error": "selected_option is required."}, status=400)
            try:
                submit_poll_vote(poll_id, int(selected_option), request_user=request.user)
                return Response({"status": 200, "message": "Vote recorded."})
            except CentralMessServiceError as exc:
                return Response({"error": str(exc)}, status=exc.status_code)
        elif action == "close":
            try:
                close_menu_poll(poll_id, request_user=request.user)
                return Response({"status": 200, "message": "Poll closed."})
            except Exception as exc:
                return Response({"error": str(exc)}, status=400)

        return Response({"error": "action must be vote or close."}, status=400)

    def delete(self, request):
        poll_id = request.data.get("poll_id")
        if not poll_id:
            return Response({"error": "poll_id is required."}, status=400)
        try:
            delete_menu_poll(poll_id, request_user=request.user)
            return Response({"status": 200})
        except CentralMessServiceError as exc:
            return Response({"error": str(exc)}, status=exc.status_code)


class AdminMessManagementApi(APIView):
    """
    Admin-level direct student registration management for caretaker/mess_manager.
    POST  {action:"add", student_id, mess_option, amount, program}
    POST  {action:"remove", student_id}
    POST  {action:"remove_all", mess_option}
    """

    def post(self, request):
        action = request.data.get("action")
        student_id = request.data.get("student_id", "").strip()

        if action == "add":
            mess_option = request.data.get("mess_option", "mess1")
            amount = int(request.data.get("amount", 0))
            program = request.data.get("program", "UG")
            try:
                admin_register_student(
                    student_id, mess_option, amount, program, request.user
                )
                return Response({"status": 200, "message": f"Student {student_id} registered to {mess_option}."})
            except CentralMessServiceError as exc:
                return Response({"error": str(exc)}, status=exc.status_code)

        elif action == "remove":
            try:
                admin_deregister_student(student_id, request.user)
                return Response({"status": 200, "message": f"Student {student_id} deregistered."})
            except CentralMessServiceError as exc:
                return Response({"error": str(exc)}, status=exc.status_code)

        elif action == "remove_all":
            mess_option = request.data.get("mess_option")
            if not mess_option:
                return Response({"error": "mess_option is required."}, status=400)
            count = admin_deregister_all_from_mess(mess_option, request.user)
            return Response({"status": 200, "message": f"Deregistered {count} students from {mess_option}."})

        elif action == "bulk_add":
            upload = request.FILES.get("file")
            if upload is None:
                return Response({"error": "file is required for bulk_add action."}, status=400)
            mess_option = request.data.get("mess_option", "mess1")
            try:
                result = admin_bulk_register_students(upload, mess_option, request.user)
            except CentralMessServiceError as exc:
                return Response({"error": str(exc)}, status=exc.status_code)
            message = (
                f"Bulk registration completed. Success: {result['success_count']}, "
                f"Failed: {result['failed_count']}."
            )
            return Response({"status": 200, "message": message, "payload": result})

        return Response({"error": "Invalid action. Must be add, remove, remove_all, or bulk_add."}, status=400)


class AnnouncementApi(APIView):

    def get(self, request):
        mess_option = request.query_params.get("mess_option")
        announcements = get_announcement_queryset(mess_option=mess_option)
        serializer = AnnouncementSerializer(announcements, many=True)
        return Response({'status': 200, 'payload': serializer.data})

    def post(self, request):
        serializer = AnnouncementSerializer(data=request.data)
        if serializer.is_valid():
            try:
                announcement = create_announcement(
                    serializer.validated_data, request_user=request.user
                )
                return Response(
                    {'status': 200, 'payload': AnnouncementSerializer(announcement).data},
                    status=status.HTTP_201_CREATED,
                )
            except CentralMessServiceError as exc:
                return Response({'error': str(exc)}, status=exc.status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        announcement_id = request.data.get("id")
        if not announcement_id:
            return Response({'error': 'id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            delete_announcement(announcement_id, request_user=request.user)
            return Response({'status': 200})
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_404_NOT_FOUND)


class VacationSurveyApi(APIView):
    """
    GET  ?mess_option=&active_only=  — list surveys
    POST {title, description?, vacation_start, vacation_end, mess_option}  — create survey (caretaker)
    PUT  {survey_id, response, remarks?}  — respond to survey (student)
    DELETE {survey_id}  — delete survey (caretaker)
    """

    def get(self, request):
        mess_option = request.query_params.get("mess_option")
        active_only = request.query_params.get("active_only", "").lower() == "true"
        surveys = get_vacation_survey_queryset(mess_option=mess_option, active_only=active_only)
        serializer = VacationSurveySerializer(surveys, many=True, context={"request": request})
        return Response({"status": 200, "payload": serializer.data})

    def post(self, request):
        serializer = VacationSurveySerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            try:
                survey = create_vacation_survey(serializer.validated_data, request_user=request.user)
                return Response(
                    {"status": 200, "payload": VacationSurveySerializer(survey, context={"request": request}).data},
                    status=status.HTTP_201_CREATED,
                )
            except CentralMessServiceError as exc:
                return Response({"error": str(exc)}, status=exc.status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        survey_id = request.data.get("survey_id")
        response_val = request.data.get("response")
        remarks = request.data.get("remarks", "")
        if not survey_id or not response_val:
            return Response({"error": "survey_id and response are required."}, status=400)
        try:
            submit_survey_response(survey_id, response_val, remarks, request_user=request.user)
            return Response({"status": 200, "message": "Response recorded."})
        except CentralMessServiceError as exc:
            return Response({"error": str(exc)}, status=exc.status_code)

    def delete(self, request):
        survey_id = request.data.get("survey_id")
        if not survey_id:
            return Response({"error": "survey_id is required."}, status=400)
        try:
            delete_vacation_survey(survey_id, request_user=request.user)
            return Response({"status": 200})
        except CentralMessServiceError as exc:
            return Response({"error": str(exc)}, status=exc.status_code)


class RefundRequestApi(APIView):

    def get(self, request):
        roles = _designation_set(request.user)
        if roles.intersection(MANAGEMENT_READ_ROLES):
            refund_qs = get_refund_request_queryset()
        else:
            student = get_student_from_request_user(request.user)
            refund_qs = get_refund_request_queryset(student=student)
        serializer = RefundRequestSerializer(refund_qs, many=True)
        return Response({"status": 200, "payload": serializer.data})

    def post(self, request):
        serializer = RefundRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                obj = create_refund_request(serializer.validated_data, request_user=request.user)
                return Response(
                    {"status": 200, "payload": RefundRequestSerializer(obj).data},
                    status=status.HTTP_201_CREATED,
                )
            except CentralMessServiceError as exc:
                return Response({"error": str(exc)}, status=exc.status_code)
        return Response(serializer.errors, status=400)

    def put(self, request):
        serializer = RefundDecisionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                obj = decide_refund_request(
                    serializer.validated_data["id"],
                    serializer.validated_data["status"],
                    serializer.validated_data.get("reviewer_remark", ""),
                    serializer.validated_data.get("reference_no", ""),
                    request_user=request.user,
                )
                return Response({"status": 200, "payload": RefundRequestSerializer(obj).data})
            except CentralMessServiceError as exc:
                return Response({"error": str(exc)}, status=exc.status_code)
        return Response(serializer.errors, status=400)

    def delete(self, request):
        serializer = RefundCancelSerializer(data=request.data)
        if serializer.is_valid():
            try:
                obj = cancel_refund_request(serializer.validated_data["id"], request_user=request.user)
                return Response({"status": 200, "payload": RefundRequestSerializer(obj).data})
            except CentralMessServiceError as exc:
                return Response({"error": str(exc)}, status=exc.status_code)
        return Response(serializer.errors, status=400)


class RefundLedgerApi(APIView):

    def get(self, request):
        roles = _designation_set(request.user)
        if roles.intersection(MANAGEMENT_READ_ROLES):
            ledger_qs = get_refund_ledger_queryset()
        else:
            student = get_student_from_request_user(request.user)
            ledger_qs = get_refund_ledger_queryset(student=student)
        serializer = RefundLedgerSerializer(ledger_qs, many=True)
        return Response({"status": 200, "payload": serializer.data})


class SpecialEventMealApi(APIView):

    def get(self, request):
        mess_option = request.query_params.get("mess_option")
        active_only = request.query_params.get("active_only", "").lower() == "true"
        qs = get_special_event_meal_queryset(mess_option=mess_option, active_only=active_only)
        serializer = SpecialEventMealSerializer(qs, many=True)
        return Response({"status": 200, "payload": serializer.data})

    def post(self, request):
        serializer = SpecialEventMealSerializer(data=request.data)
        if serializer.is_valid():
            try:
                obj = create_special_event_meal(serializer.validated_data, request_user=request.user)
                return Response(
                    {"status": 200, "payload": SpecialEventMealSerializer(obj).data},
                    status=status.HTTP_201_CREATED,
                )
            except CentralMessServiceError as exc:
                return Response({"error": str(exc)}, status=exc.status_code)
        return Response(serializer.errors, status=400)

    def delete(self, request):
        event_id = request.data.get("id")
        if not event_id:
            return Response({"error": "id is required."}, status=400)
        try:
            obj = delete_special_event_meal(event_id, request_user=request.user)
            return Response({"status": 200, "payload": SpecialEventMealSerializer(obj).data})
        except CentralMessServiceError as exc:
            return Response({"error": str(exc)}, status=exc.status_code)


class RoleAssignmentApi(APIView):

    def get(self, request):
        enforce_read_access(
            request.user,
            endpoint="/mess/api/roleAssignmentApi/",
            method="GET",
            allowed_designations=MANAGEMENT_READ_ROLES,
            allow_staff=True,
        )
        role_type = request.query_params.get("role_type")
        active_only = request.query_params.get("active_only", "").lower() == "true"
        assignments = get_role_assignment_queryset(role_type=role_type, active_only=active_only)
        transfers = get_role_transfer_log_queryset(role_type=role_type)
        return Response(
            {
                "status": 200,
                "payload": {
                    "assignments": RoleAssignmentSerializer(assignments, many=True).data,
                    "transfers": RoleTransferLogSerializer(transfers, many=True).data,
                },
            }
        )

    def post(self, request):
        serializer = RoleAssignmentActionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                obj = assign_mess_role(
                    serializer.validated_data["role_type"],
                    serializer.validated_data["assignee_username"],
                    serializer.validated_data.get("start_date"),
                    serializer.validated_data.get("end_date"),
                    serializer.validated_data.get("reason", ""),
                    request_user=request.user,
                )
                return Response(
                    {"status": 200, "payload": RoleAssignmentSerializer(obj).data},
                    status=status.HTTP_201_CREATED,
                )
            except CentralMessServiceError as exc:
                return Response({"error": str(exc)}, status=exc.status_code)
        return Response(serializer.errors, status=400)


class AuditAndComplianceApi(APIView):

    def get(self, request):
        enforce_read_access(
            request.user,
            endpoint="/mess/api/auditComplianceApi/",
            method="GET",
            allowed_designations=MANAGEMENT_READ_ROLES,
            allow_staff=True,
        )
        return Response(
            {
                "status": 200,
                "payload": {
                    "audit_logs": AuditLogSerializer(get_audit_log_queryset()[:200], many=True).data,
                    "access_violations": AccessViolationLogSerializer(
                        get_access_violation_queryset()[:200], many=True
                    ).data,
                },
            }
        )


class FeedbackReportApi(APIView):

    def get(self, request):
        enforce_read_access(
            request.user,
            endpoint="/mess/api/feedbackReportApi/",
            method="GET",
            allowed_designations=MANAGEMENT_READ_ROLES,
            allow_staff=True,
        )
        reports = get_feedback_report_queryset()
        serializer = FeedbackReportSerializer(reports, many=True)
        return Response({"status": 200, "payload": serializer.data})

    def post(self, request):
        enforce_read_access(
            request.user,
            endpoint="/mess/api/feedbackReportApi/",
            method="POST",
            allowed_designations=MANAGEMENT_READ_ROLES,
            allow_staff=True,
        )
        report = create_feedback_report_snapshot(request_user=request.user)
        return Response(
            {"status": 200, "payload": FeedbackReportSerializer(report).data},
            status=status.HTTP_201_CREATED,
        )
