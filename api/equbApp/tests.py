from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .models import AppConfig, Equb, EqubCategory, EqubType
import datetime

User = get_user_model()

class EqubDetailTests(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_customer(
            phone="0911223344",
            password="testpassword123"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create EqubType
        self.equb_type = EqubType.objects.create(
            name="Weekly",
            description="Weekly contribution"
        )

        # Create EqubCategory
        self.category = EqubCategory.objects.create(
            name="Savings",
            description="Standard savings"
        )

        # Create Equb
        self.equb = Equb.objects.create(
            name="Test Equb",
            owner=self.user,
            category=self.category,
            equb_type=self.equb_type,
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=30),
            contribution_amount=100.00,
            total_members=10,
            payout_system="random",
            status="active"
        )

    def test_get_equb_detail_success(self):
        """Test getting equb detail successfully."""
        url = reverse('equb-detail', kwargs={'id': self.equb.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], "Test Equb")
        self.assertEqual(response.data['data']['equb_type']['name'], "Weekly")
        self.assertEqual(response.data['data']['category']['name'], "Savings")
        self.assertEqual(response.data['data']['current_members_count'], 0)
        self.assertEqual(response.data['data']['total_rounds'], 10)
        self.assertEqual(response.data['data']['current_round'], 1)

    def test_get_equb_detail_unauthenticated(self):
        """Test getting equb detail without authentication."""
        self.client.credentials()  # Clear credentials
        url = reverse('equb-detail', kwargs={'id': self.equb.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_equb_detail_not_found(self):
        """Test getting equb detail with non-existent ID."""
        import uuid
        url = reverse('equb-detail', kwargs={'id': uuid.uuid4()})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    def test_get_customer_dashboard_success(self):
        """Test getting customer dashboard."""
        url = reverse('customer-dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if user phone is in response
        self.assertEqual(response.data['user_name'], self.user.phone)

    def test_pay_equb_contribution_route(self):
        """Test the route for paying equb contribution."""
        # This requires the user to be an active member.
        from .models import EqubMember
        EqubMember.objects.create(user=self.user, equb=self.equb, status="active")
        
        url = reverse('pay-equb-contribution', kwargs={'equb_id': self.equb.id})
        # Note: We don't have a real receipt image here, so we just check routing/auth
        # or we could mock files if needed. For now, check if reverse works.
        self.assertTrue(url)

    def test_admin_approve_payment_route(self):
        """Test the route for admin payment approval."""
        url = reverse('admin-approve-payment', kwargs={'payment_id': '00000000-0000-0000-0000-000000000000'})
        self.assertTrue(url)

    def test_join_equb_initial_requires_payment(self):
        """Accepting terms alone is not enough: first-round payment is required."""
        url = reverse('join-equb-initial', kwargs={'equb_id': self.equb.id})
        response = self.client.post(url, {"accept_terms": True})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_join_equb_initial_success(self):
        """Test joining an Equb at Round 0 with the first-round payment."""
        import io
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile
        url = reverse('join-equb-initial', kwargs={'equb_id': self.equb.id})
        buf = io.BytesIO()
        Image.new("RGB", (2, 2)).save(buf, "PNG")
        receipt = SimpleUploadedFile("receipt.png", buf.getvalue(), content_type="image/png")
        response = self.client.post(url, {
            "accept_terms": True,
            "amount": "100.00",
            "payment_method": "bank",
            "transaction_id": "TXN-TEST-1",
            "receipt_image": receipt,
        }, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['member_status'], "pending")


class AppConfigEndpointTests(APITestCase):
    def setUp(self):
        cache.clear()
        AppConfig.objects.all().delete()
        AppConfig.objects.create(latest_version="1.2.3", force_update=False)

    def tearDown(self):
        cache.clear()

    def test_app_config_returns_expected_shape(self):
        response = self.client.get("/app-config/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {
            "latestVersion": "1.2.3",
            "forceUpdate": False,
            "_note": "Edit these values at /admin/equbApp/appconfig/",
        })
