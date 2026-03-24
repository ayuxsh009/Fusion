from rest_framework import serializers

from applications.central_mess.models import (
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


def _normalize_status(value):
    return str(value).strip().lower()


class MessinfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messinfo
        fields = "__all__"
        extra_kwargs = {"student_id": {"required": False}}


class Mess_regSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mess_reg
        fields = "__all__"

    def validate(self, attrs):
        start = attrs.get("start_reg")
        end = attrs.get("end_reg")
        if start and end and end < start:
            raise serializers.ValidationError(
                {"end_reg": "end_reg cannot be before start_reg."}
            )
        return attrs


class MessBillBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessBillBase
        fields = "__all__"


class Monthly_billSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monthly_bill
        fields = "__all__"

    def validate_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("amount cannot be negative.")
        return value


class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = "__all__"


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = "__all__"


class RebateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rebate
        fields = "__all__"
        extra_kwargs = {"student_id": {"required": False}}

    def validate(self, attrs):
        start = attrs.get("start_date")
        end = attrs.get("end_date")
        if start and end and end < start:
            raise serializers.ValidationError(
                {"end_date": "end_date cannot be before start_date."}
            )
        return attrs


class Vacation_foodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacation_food
        fields = "__all__"
        extra_kwargs = {"student_id": {"required": False}}

    def validate(self, attrs):
        start = attrs.get("start_date")
        end = attrs.get("end_date")
        if start and end and end < start:
            raise serializers.ValidationError(
                {"end_date": "end_date cannot be before start_date."}
            )
        return attrs


class Special_requestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Special_request
        fields = "__all__"
        extra_kwargs = {"student_id": {"required": False}}

    def validate(self, attrs):
        start = attrs.get("start_date")
        end = attrs.get("end_date")
        if start and end and end < start:
            raise serializers.ValidationError(
                {"end_date": "end_date cannot be before start_date."}
            )
        return attrs


class Mess_meetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mess_meeting
        fields = "__all__"


class Mess_minutesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mess_minutes
        fields = "__all__"


class Menu_change_requestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu_change_request
        fields = "__all__"
        extra_kwargs = {"student_id": {"required": False}}


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = "__all__"
        extra_kwargs = {"student_id": {"required": False}}

    def validate_mess_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("mess_rating must be between 1 and 5.")
        return value

    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("description must be at least 10 characters.")
        return value


class GetFilteredSerialzer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="student_id.id.user.first_name")
    last_name = serializers.CharField(source="student_id.id.user.last_name")

    class Meta:
        model = Reg_main
        fields = "__all__"


class reg_recordSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Reg_records
        fields = "__all__"


class RegistrationRequestSerializer(serializers.ModelSerializer):
    mess_option = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = Registration_Request
        fields = "__all__"
        extra_kwargs = {"student_id": {"required": False}}

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("amount must be greater than 0.")
        return value


class DeregistrationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deregistration_Request
        fields = "__all__"
        extra_kwargs = {"student_id": {"required": False}}


class UpdatePaymentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Update_Payment
        fields = "__all__"
        extra_kwargs = {"student_id": {"required": False}}

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("amount must be greater than 0.")
        return value


class FeedbackStatusUpdateSerializer(serializers.Serializer):
    student_id = serializers.CharField()
    mess = serializers.CharField()
    feedback_type = serializers.CharField()
    description = serializers.CharField()
    fdate = serializers.DateField()
    feedback_remark = serializers.CharField(required=False, allow_blank=True)


class RebateStatusUpdateSerializer(serializers.Serializer):
    student_id = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    purpose = serializers.CharField()
    app_date = serializers.DateField()
    leave_type = serializers.CharField()
    status = serializers.CharField()
    rebate_remark = serializers.CharField(required=False, allow_blank=True)

    def validate_status(self, value):
        if str(value) not in {"0", "1", "2"}:
            raise serializers.ValidationError("status must be one of 0, 1, 2.")
        return str(value)


class VacationFoodStatusUpdateSerializer(serializers.Serializer):
    student_id = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    purpose = serializers.CharField()
    app_date = serializers.DateField()
    status = serializers.CharField()

    def validate_status(self, value):
        if str(value) not in {"0", "1", "2"}:
            raise serializers.ValidationError("status must be one of 0, 1, 2.")
        return str(value)


class SpecialRequestStatusUpdateSerializer(serializers.Serializer):
    student_id = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    app_date = serializers.DateField()
    request = serializers.CharField()
    item1 = serializers.CharField()
    item2 = serializers.CharField()
    status = serializers.CharField()

    def validate_status(self, value):
        if str(value) not in {"0", "1", "2"}:
            raise serializers.ValidationError("status must be one of 0, 1, 2.")
        return str(value)


class RegistrationDecisionSerializer(serializers.Serializer):
    student_id = serializers.CharField()
    start_date = serializers.DateField()
    payment_date = serializers.DateField()
    amount = serializers.IntegerField()
    Txn_no = serializers.CharField()
    status = serializers.CharField()
    registration_remark = serializers.CharField(required=False, allow_blank=True)
    mess_option = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        status = _normalize_status(attrs.get("status"))
        if status not in {"pending", "accept", "reject"}:
            raise serializers.ValidationError(
                {"status": "status must be one of pending, accept, reject."}
            )
        if status == "accept" and not attrs.get("mess_option"):
            raise serializers.ValidationError(
                {"mess_option": "mess_option is required when accepting request."}
            )
        if attrs.get("amount", 0) <= 0:
            raise serializers.ValidationError({"amount": "amount must be greater than 0."})
        attrs["status"] = status
        return attrs


class DeregistrationDecisionSerializer(serializers.Serializer):
    student_id = serializers.CharField()
    end_date = serializers.DateField()
    status = serializers.CharField()
    deregistration_remark = serializers.CharField(required=False, allow_blank=True)

    def validate_status(self, value):
        status = _normalize_status(value)
        if status not in {"pending", "accept", "reject"}:
            raise serializers.ValidationError(
                "status must be one of pending, accept, reject."
            )
        return status


class DeregistrationDeleteSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=1)


class UpdatePaymentDecisionSerializer(serializers.Serializer):
    student_id = serializers.CharField()
    payment_date = serializers.DateField()
    amount = serializers.IntegerField()
    Txn_no = serializers.CharField()
    status = serializers.CharField()
    update_payment_remark = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        status = _normalize_status(attrs.get("status"))
        if status not in {"pending", "accept", "reject"}:
            raise serializers.ValidationError(
                {"status": "status must be one of pending, accept, reject."}
            )
        if attrs.get("amount", 0) <= 0:
            raise serializers.ValidationError({"amount": "amount must be greater than 0."})
        attrs["status"] = status
        return attrs


class AnnouncementSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Announcement
        fields = "__all__"
        extra_kwargs = {"created_by": {"required": False}}

    def get_created_by_name(self, obj):
        if obj.created_by and obj.created_by.user:
            return f"{obj.created_by.user.first_name} {obj.created_by.user.last_name}".strip()
        return ""

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("title must be at least 3 characters.")
        return value

    def validate_content(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("content must be at least 10 characters.")
        return value


class MenuPollSerializer(serializers.ModelSerializer):
    vote_counts = serializers.SerializerMethodField(read_only=True)
    user_vote = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MenuPoll
        fields = "__all__"
        extra_kwargs = {"created_by": {"required": False}}

    def get_vote_counts(self, obj):
        votes = obj.votes.all()
        return {
            "option1": votes.filter(selected_option=1).count(),
            "option2": votes.filter(selected_option=2).count(),
            "option3": votes.filter(selected_option=3).count(),
            "option4": votes.filter(selected_option=4).count(),
        }

    def get_user_vote(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            from applications.globals.models import ExtraInfo
            from applications.academic_information.models import Student
            try:
                extra = ExtraInfo.objects.get(user=request.user)
                student = Student.objects.get(id=extra.id)
                vote = obj.votes.filter(student_id=student).first()
                return vote.selected_option if vote else None
            except Exception:
                return None
        return None


class MenuPollVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuPollVote
        fields = "__all__"
        extra_kwargs = {"student_id": {"required": False}}

    def validate_selected_option(self, value):
        if value not in {1, 2, 3, 4}:
            raise serializers.ValidationError("selected_option must be 1, 2, 3, or 4.")
        return value


class VacationSurveySerializer(serializers.ModelSerializer):
    response_counts = serializers.SerializerMethodField(read_only=True)
    user_response = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = VacationSurvey
        fields = "__all__"
        extra_kwargs = {"created_by": {"required": False}}

    def validate(self, attrs):
        start = attrs.get("vacation_start")
        end = attrs.get("vacation_end")
        if start and end and end < start:
            raise serializers.ValidationError({"vacation_end": "vacation_end cannot be before vacation_start."})
        return attrs

    def get_response_counts(self, obj):
        responses = obj.responses.all()
        return {
            "staying": responses.filter(response="staying").count(),
            "leaving": responses.filter(response="leaving").count(),
            "undecided": responses.filter(response="undecided").count(),
        }

    def get_user_response(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            from applications.globals.models import ExtraInfo
            from applications.academic_information.models import Student
            try:
                extra = ExtraInfo.objects.get(user=request.user)
                student = Student.objects.get(id=extra.id)
                resp = obj.responses.filter(student_id=student).first()
                return resp.response if resp else None
            except Exception:
                return None
        return None


class VacationSurveyResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = VacationSurveyResponse
        fields = "__all__"
        extra_kwargs = {"student_id": {"required": False}}
