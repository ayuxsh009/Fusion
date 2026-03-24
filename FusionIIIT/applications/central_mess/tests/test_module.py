from pathlib import Path
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from applications.central_mess import selectors, services


# ---------------------------------------------------------------------------
# Architecture / structure tests
# ---------------------------------------------------------------------------

class CentralMessModuleStructureTest(TestCase):
    def test_modular_layer_files_exist(self):
        module_root = Path(__file__).resolve().parents[1]
        expected = [
            module_root / "services.py",
            module_root / "selectors.py",
            module_root / "api" / "urls.py",
            module_root / "api" / "views.py",
            module_root / "api" / "serializers.py",
            module_root / "tests" / "test_module.py",
        ]
        for path in expected:
            self.assertTrue(path.exists(), f"Missing required module file: {path}")

    def test_services_module_exposes_expected_entrypoints(self):
        expected = [
            "create_feedback",
            "update_feedback_status",
            "delete_feedback",
            "create_rebate",
            "update_rebate_status",
            "create_special_request",
            "update_special_request_status",
            "create_vacation_food",
            "update_vacation_food_status",
            "create_registration_request",
            "decide_registration_request",
            "create_deregistration_request",
            "decide_deregistration_request",
            "create_update_payment_request",
            "decide_update_payment_request",
            "create_mess_meeting",
            "create_mess_minutes",
            "create_menu_change_request",
            "process_excel_bill_update",
            "CentralMessServiceError",
            "RebateOverlapError",
        ]
        for name in expected:
            self.assertTrue(
                hasattr(services, name),
                f"services.py is missing: {name}",
            )

    def test_selectors_module_exposes_expected_entrypoints(self):
        expected = [
            "get_student_from_request_user",
            "get_feedback_queryset",
            "get_menu_queryset",
            "get_rebate_queryset",
            "get_special_request_queryset",
            "get_vacation_food_queryset",
            "get_registration_request_queryset",
            "get_deregistration_request_queryset",
            "get_update_payment_request_queryset",
            "get_monthly_bill_queryset",
            "get_payments_queryset",
            "get_reg_main_for_student",
            "get_reg_main_queryset",
            "get_reg_main_by_student_id",
            "get_reg_records_queryset",
            "get_messinfo_queryset",
            "get_mess_reg_queryset",
            "get_mess_bill_base_queryset",
            "get_mess_meeting_queryset",
            "get_mess_minutes_queryset",
            "get_menu_change_request_queryset",
        ]
        for name in expected:
            self.assertTrue(
                hasattr(selectors, name),
                f"selectors.py is missing: {name}",
            )

    def test_api_views_has_no_direct_orm(self):
        """Verify api/views.py does not import ORM models directly."""
        api_views_path = Path(__file__).resolve().parents[1] / "api" / "views.py"
        source = api_views_path.read_text()
        forbidden = [
            "objects.filter(",
            "objects.all()",
            "objects.get(",
            "objects.create(",
        ]
        for snippet in forbidden:
            self.assertNotIn(
                snippet,
                source,
                f"api/views.py should not contain direct ORM call: {snippet}",
            )

    def test_api_views_imports_no_models(self):
        """api/views.py must not import Django model classes directly."""
        api_views_path = Path(__file__).resolve().parents[1] / "api" / "views.py"
        source = api_views_path.read_text()
        self.assertNotIn(
            "from applications.central_mess.models import",
            source,
            "api/views.py should not import models directly — use selectors/services.",
        )

    def test_api_urls_uses_path_not_url(self):
        """api/urls.py must use django.urls.path, not the deprecated url()."""
        api_urls_path = Path(__file__).resolve().parents[1] / "api" / "urls.py"
        source = api_urls_path.read_text()
        self.assertIn("from django.urls import path", source)
        self.assertNotIn("from django.conf.urls import url", source)


# ---------------------------------------------------------------------------
# Selector unit tests (no DB needed for structural checks)
# ---------------------------------------------------------------------------

class SelectorsReturnQuerysetTest(TestCase):
    """Smoke-test that each selector returns something iterable (empty DB is fine)."""

    def test_get_feedback_queryset_returns_queryset(self):
        qs = selectors.get_feedback_queryset()
        list(qs)  # should not raise

    def test_get_menu_queryset_returns_queryset(self):
        qs = selectors.get_menu_queryset()
        list(qs)

    def test_get_rebate_queryset_returns_queryset(self):
        qs = selectors.get_rebate_queryset()
        list(qs)

    def test_get_special_request_queryset_returns_queryset(self):
        qs = selectors.get_special_request_queryset()
        list(qs)

    def test_get_vacation_food_queryset_returns_queryset(self):
        qs = selectors.get_vacation_food_queryset()
        list(qs)

    def test_get_registration_request_queryset_returns_queryset(self):
        qs = selectors.get_registration_request_queryset()
        list(qs)

    def test_get_deregistration_request_queryset_returns_queryset(self):
        qs = selectors.get_deregistration_request_queryset()
        list(qs)

    def test_get_update_payment_request_queryset_returns_queryset(self):
        qs = selectors.get_update_payment_request_queryset()
        list(qs)

    def test_get_monthly_bill_queryset_returns_queryset(self):
        qs = selectors.get_monthly_bill_queryset()
        list(qs)

    def test_get_payments_queryset_returns_queryset(self):
        qs = selectors.get_payments_queryset()
        list(qs)

    def test_get_reg_main_queryset_returns_queryset(self):
        qs = selectors.get_reg_main_queryset()
        list(qs)

    def test_get_reg_main_queryset_filters_status(self):
        qs_all = selectors.get_reg_main_queryset()
        qs_filtered = selectors.get_reg_main_queryset(status="Registered")
        # Filtered must be a subset of all
        self.assertLessEqual(qs_filtered.count(), qs_all.count())

    def test_get_reg_main_queryset_ignores_all_sentinel(self):
        qs_all = selectors.get_reg_main_queryset()
        qs_sentinel = selectors.get_reg_main_queryset(status="all", program="all", mess_option="all")
        self.assertEqual(qs_all.count(), qs_sentinel.count())

    def test_get_reg_records_queryset_returns_queryset(self):
        qs = selectors.get_reg_records_queryset()
        list(qs)

    def test_get_mess_meeting_queryset_returns_queryset(self):
        qs = selectors.get_mess_meeting_queryset()
        list(qs)

    def test_get_mess_minutes_queryset_returns_queryset(self):
        qs = selectors.get_mess_minutes_queryset()
        list(qs)

    def test_get_menu_change_request_queryset_returns_queryset(self):
        qs = selectors.get_menu_change_request_queryset()
        list(qs)

    def test_get_reg_main_for_student_returns_none_for_unknown(self):
        result = selectors.get_reg_main_for_student(student=None)
        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# Service exception class tests
# ---------------------------------------------------------------------------

class ServiceExceptionTest(TestCase):
    def test_central_mess_service_error_attributes(self):
        exc = services.CentralMessServiceError("test error", status_code=422, payload={"k": "v"})
        self.assertEqual(exc.message, "test error")
        self.assertEqual(exc.status_code, 422)
        self.assertEqual(exc.payload, {"k": "v"})

    def test_rebate_overlap_error_is_service_error(self):
        exc = services.RebateOverlapError("overlap")
        self.assertIsInstance(exc, services.CentralMessServiceError)

    def test_central_mess_service_error_defaults(self):
        exc = services.CentralMessServiceError("err")
        self.assertEqual(exc.status_code, 400)
        self.assertEqual(exc.payload, {})


# ---------------------------------------------------------------------------
# API endpoint smoke tests (unauthenticated → 403/401)
# ---------------------------------------------------------------------------

class ApiEndpointAuthTest(TestCase):
    """All API endpoints should reject unauthenticated requests."""

    READ_ENDPOINTS = [
        "/mess/apifeedbackApi",
        "/mess/apimenuApi",
        "/mess/apirebateApi",
        "/mess/apispecialRequestApi",
        "/mess/apivacationFoodApi",
        "/mess/apiregistrationRequestApi",
        "/mess/apideRegistrationRequestApi",
        "/mess/apiupdatePaymentRequestApi",
        "/mess/apipaymentsApi",
        "/mess/apimessBillBaseApi",
        "/mess/apimessRegApi",
        "/mess/apiget_mess_balance_statusApi",
    ]

    def test_unauthenticated_get_returns_401_or_403(self):
        for url in self.READ_ENDPOINTS:
            response = self.client.get(url)
            self.assertIn(
                response.status_code,
                [401, 403],
                f"Expected 401/403 for unauthenticated GET {url}, got {response.status_code}",
            )
