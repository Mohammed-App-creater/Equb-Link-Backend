"""
Seed the demo data used in the submission documents (submission/*.pdf):
customer Abebe Kebede (+251911234567), the "Monthly 10K" equb (ETB 1,000 x 10
members) in the "Merchants" category, the five frequencies, a CBE payout
account, FAQs and app-config 1.2.0.

    python manage.py seed_demo                      # DEBUG only, default password
    python manage.py seed_demo --password '<pw>'    # required when DEBUG=False

Safe to run more than once: existing records are reused, and passwords are
only changed when --reset-passwords is given.
"""

import secrets
from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from advert.models import FAQ
from equbApp.models import (
    AppConfig,
    Equb,
    EqubCategory,
    EqubMember,
    EqubType,
    Notification,
    OwnerBankAccount,
    Payment,
)
from user.models import Admin, Customer, EqubAdmin, User

DEFAULT_DEV_PASSWORD = "EqubLink@2026"

# Phones are stored exactly as each client sends them, because login matches
# the phone field exactly: the mobile app sends +251 and 9 digits, the admin
# panel sends what the owner types (placeholder "0911 22 33 44").
ADMIN = {"phone": "0911000000", "name": "Platform Admin", "email": "admin@equblink.com"}
OWNER = {"phone": "0911223344", "name": "Equb Link Owner", "email": "owner@equblink.com"}
CUSTOMER = {"phone": "+251911234567", "name": "Abebe Kebede", "email": None}
# Not a member of any equb, so the join flow can be tested.
CUSTOMER_2 = {"phone": "+251922345678", "name": "Sara Tesfaye", "email": None}

EQUB_TYPES = [
    ("Daily", "One round every day"),
    ("Weekly", "One round every week"),
    ("Monthly", "One round every month"),
    ("Quarterly", "One round every three months"),
    ("Yearly", "One round every year"),
]

FAQS = [
    ("What is an equb?",
     "A traditional Ethiopian savings group. Every member pays the same contribution each round, "
     "and each round one member receives the whole pot."),
    ("How is the winner chosen?",
     "A round is drawn only when every active member has paid. The server picks a member at random "
     "from those who have not won yet, and saves the random value with the round."),
    ("How do I pay?",
     "By bank transfer to the owner's account shown in the app, then upload your receipt, or online with Chapa."),
    ("Can I join more than one equb?",
     "Not in this version. You can be a member of one equb at a time."),
    ("I forgot my password.",
     "On the sign-in screen tap Forgot password?, enter your phone number and use the 6-digit SMS code."),
]


class Command(BaseCommand):
    help = "Seed the demo accounts and equb described in the submission documents."

    def add_arguments(self, parser):
        parser.add_argument("--password", help="Password for all demo accounts.")
        parser.add_argument(
            "--reset-passwords",
            action="store_true",
            help="Also set the password on demo accounts that already exist.",
        )

    def handle(self, *args, **opts):
        password = opts["password"]
        if not password:
            if not settings.DEBUG:
                raise CommandError("DEBUG is off: pass --password for the demo accounts.")
            password = DEFAULT_DEV_PASSWORD
        try:
            validate_password(password)
        except ValidationError as exc:
            raise CommandError("Password rejected: " + " ".join(exc.messages))

        self.password = password
        self.reset = opts["reset_passwords"]

        with transaction.atomic():
            self.seed()

        self.stdout.write(self.style.SUCCESS("\nDemo data ready. Logins:"))
        shown = "<--password>" if opts["password"] else DEFAULT_DEV_PASSWORD
        for role, acct, where in [
            ("Platform admin", ADMIN, "/admin/ and admin panel"),
            ("Equb owner", OWNER, "admin panel (/api/owner/login)"),
            ("Customer", CUSTOMER, "mobile app, enter 911234567"),
            ("Customer (no equb)", CUSTOMER_2, "mobile app, enter 922345678"),
        ]:
            self.stdout.write(f"  {role:20} {acct['phone']:15} {shown}   {where}")

    # ------------------------------------------------------------------
    def account(self, info, create, profile_model, **flags):
        user = User.objects.filter(phone=info["phone"]).first()
        if user is None:
            user = create(info["phone"], self.password, info["email"])
            self.stdout.write(f"created account {info['phone']}")
        elif self.reset:
            user.set_password(self.password)
            user.save()
            self.stdout.write(f"reset password {info['phone']}")
        for k, v in flags.items():
            setattr(user, k, v)
        user.is_active = True
        user.save()

        defaults = {"name": info["name"], "phone": info["phone"]}
        if profile_model is Customer:
            defaults["referral_code"] = info["name"][:4] + str(secrets.randbelow(9000) + 1000)
        profile_model.objects.get_or_create(user=user, defaults=defaults)
        return user

    def seed(self):
        admin = self.account(
            ADMIN, User.objects.create_superuser, Admin, is_admin=True, is_staff=True
        )
        owner = self.account(OWNER, User.objects.create_equb_admin, EqubAdmin, is_equb_admin=True)
        abebe = self.account(CUSTOMER, User.objects.create_customer, Customer, is_customer=True)
        self.account(CUSTOMER_2, User.objects.create_customer, Customer, is_customer=True)

        config = AppConfig.load()
        config.latest_version = "1.2.0"
        config.force_update = False
        config.save()

        types = {}
        for name, desc in EQUB_TYPES:
            types[name], _ = EqubType.objects.get_or_create(name=name, defaults={"description": desc})

        merchants, _ = EqubCategory.objects.get_or_create(
            name="Merchants",
            defaults={"description": "Equbs for traders and shop owners", "is_favorite": True},
        )

        bank, _ = OwnerBankAccount.objects.get_or_create(
            owner=owner,
            bank_code="CBE",
            account_number="1000123456789",
            defaults={"account_holder_name": OWNER["name"], "label": "Business"},
        )

        start = date.today().replace(day=1)
        equb, created = Equb.objects.get_or_create(
            name="Monthly 10K",
            owner=owner,
            defaults={
                "category": merchants,
                "equb_type": types["Monthly"],
                "start_date": start,
                "end_date": start + timedelta(days=31 * 10),
                "rules": (
                    "Pay ETB 1,000 by the 5th of every month. "
                    "Each round one member who has not won yet is drawn at random. "
                    "Every member wins exactly once."
                ),
                "rules_approved": True,
                "payout_system": "random",
                "total_members": 10,
                "contribution_amount": Decimal("1000.00"),
                "status": "active",
            },
        )
        equb.payout_bank_accounts.add(bank)
        if created:
            self.stdout.write("created equb Monthly 10K")

        member, _ = EqubMember.objects.get_or_create(
            user=abebe,
            equb=equb,
            defaults={"status": "active", "payment_status": "paid"},
        )
        _, paid = Payment.objects.get_or_create(
            equb_member=member,
            round_number=1,
            defaults={
                "amount": equb.contribution_amount,
                "payment_method": "bank",
                "transaction_id": "DEMO-CBE-0001",
                "status": "completed",
                "paid_at": timezone.now(),
                "approved_by": owner,
                "approved_at": timezone.now(),
            },
        )
        if paid:
            Notification.objects.create(
                user=abebe,
                notif_type="payment_approved",
                message="Your ETB 1,000.00 payment for Monthly 10K, round 1, was approved.",
            )

        for question, answer in FAQS:
            FAQ.objects.get_or_create(question=question, defaults={"answer": answer})

        # Keep the admin flag on the superuser for the admin panel's role checks.
        admin.is_admin = True
        admin.save()
