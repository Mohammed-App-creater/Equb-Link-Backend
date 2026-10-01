"""
Seed the demo data used in the submission documents (submission/*.pdf) plus a
full catalogue so every screen has content:

- logins: platform admin, equb owner, Abebe Kebede (+251911234567) and a
  customer with no equb (for the join flow), plus 29 member accounts
- 6 categories (with generated images), the 5 frequencies, 3 payout accounts
- 7 equbs covering every frequency and state: "Monthly 10K" (ETB 1,000 x 10,
  2 rounds drawn, round 3 in progress), one fully paid and ready to draw,
  ones open for joining, pending applications and payments, and a draft
- winners and draw seeds, payouts, notifications, support tickets, adverts,
  testimonials, FAQs, audit log entries and app-config 1.2.0

    python manage.py seed_demo                      # DEBUG only, default password
    python manage.py seed_demo --password '<pw>'    # required when DEBUG=False

Safe to run more than once: existing records are reused, and passwords are
only changed when --reset-passwords is given.
"""

import io
import secrets
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

from advert.models import FAQ, Advert, Testimonial
from equbApp.models import (
    AppConfig,
    Equb,
    EqubCategory,
    EqubMember,
    EqubType,
    LotteryWinner,
    Notification,
    OwnerBankAccount,
    Payment,
    SupportTicket,
)
from owner_panel.models import AuditLog, LotteryRound
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

MEMBER_NAMES = [
    "Almaz Tadesse", "Bekele Girma", "Chaltu Abdi", "Dawit Haile", "Eden Alemu",
    "Fikru Mengistu", "Genet Wolde", "Habtamu Desta", "Hirut Bekele", "Kebede Tola",
    "Lemlem Gebre", "Meseret Ayele", "Mulugeta Assefa", "Nardos Teshome", "Rahel Mekonnen",
    "Selam Getachew", "Solomon Tefera", "Tigist Abebe", "Tsegaye Lemma", "Yared Kassa",
    "Yeshi Demissie", "Yonas Berhanu", "Zewdu Negash", "Betelhem Shiferaw", "Biruk Alemayehu",
    "Mahlet Worku", "Henok Fekadu", "Kidist Tsegaye", "Ermias Wondimu",
]

EQUB_TYPES = [
    ("Daily", "One round every day", 1),
    ("Weekly", "One round every week", 7),
    ("Monthly", "One round every month", 30),
    ("Quarterly", "One round every three months", 91),
    ("Yearly", "One round every year", 365),
]

# name, description, favourite, image colour
CATEGORIES = [
    ("Merchants", "Equbs for traders and shop owners", True, "#0F766E"),
    ("Employees", "Salary-day equbs for office and factory staff", True, "#1D4ED8"),
    ("Drivers", "Daily equbs for taxi, bajaj and truck drivers", False, "#B45309"),
    ("Students", "Small weekly equbs for university students", False, "#7C3AED"),
    ("Business Owners", "Large equbs for growing businesses", False, "#BE123C"),
    ("Family & Community", "Equbs for families, idirs and neighbourhoods", False, "#15803D"),
]

BANK_ACCOUNTS = [
    ("CBE", "1000123456789", "Business"),
    ("TBR", "0911223344", "Telebirr"),
    ("AWB", "01320456789012", "Awash savings"),
]

# Each equb: who is in it and how far it has run.
#   members        active members drawn from MEMBER_NAMES, in order (Abebe is added to Monthly 10K)
#   winners        member indexes (within this equb) that won rounds 1..n
#   paid_out       how many of those rounds the owner has marked as paid out
#   current_paid   members who have a completed payment for the current round
#   current_pending members (after those) with a pending payment for the current round
#   applicants     extra members with a pending join request (round 0 payment)
#   start_offset   start date = today + offset * period length
EQUBS = [
    {
        "name": "Monthly 10K", "category": "Merchants", "type": "Monthly",
        "amount": "1000.00", "total": 10, "start_offset": -2, "members": 9,
        "winners": [3, 7], "paid_out": 1, "current_paid": 7, "current_pending": 2,
        "applicants": 0, "banks": ["CBE", "TBR"], "status": "active",
        "rules": "Pay ETB 1,000 by the 5th of every month. Each round one member who has not won yet "
                 "is drawn at random. Every member wins exactly once.",
    },
    {
        "name": "Quarterly Business Equb", "category": "Business Owners", "type": "Quarterly",
        "amount": "10000.00", "total": 8, "start_offset": -1, "members": 8,
        "winners": [2], "paid_out": 1, "current_paid": 8, "current_pending": 0,
        "applicants": 0, "banks": ["CBE", "AWB"], "status": "active",
        "rules": "ETB 10,000 per quarter. Round 2 is fully paid and ready to draw.",
    },
    {
        "name": "Daily Drivers 500", "category": "Drivers", "type": "Daily",
        "amount": "100.00", "total": 5, "start_offset": 0, "members": 3,
        "winners": [], "paid_out": 0, "current_paid": 2, "current_pending": 1,
        "applicants": 0, "banks": ["TBR"], "status": "active",
        "rules": "ETB 100 every day before 8 pm via Telebirr or CBE.",
    },
    {
        "name": "Weekly Office Savings", "category": "Employees", "type": "Weekly",
        "amount": "500.00", "total": 12, "start_offset": 1, "members": 4,
        "winners": [], "paid_out": 0, "current_paid": 0, "current_pending": 0,
        "applicants": 1, "banks": ["CBE"], "status": "active",
        "rules": "ETB 500 every Friday. Starts next week.",
    },
    {
        "name": "Student Weekly 200", "category": "Students", "type": "Weekly",
        "amount": "200.00", "total": 10, "start_offset": 2, "members": 1,
        "winners": [], "paid_out": 0, "current_paid": 0, "current_pending": 0,
        "applicants": 1, "banks": ["TBR"], "status": "active",
        "rules": "ETB 200 every Monday. Open to registered university students.",
    },
    {
        "name": "Yearly Family Equb", "category": "Family & Community", "type": "Yearly",
        "amount": "5000.00", "total": 6, "start_offset": 1, "members": 2,
        "winners": [], "paid_out": 0, "current_paid": 0, "current_pending": 0,
        "applicants": 0, "banks": ["AWB"], "status": "active",
        "rules": "ETB 5,000 once a year, drawn every Meskel holiday.",
    },
    {
        "name": "Merchants Daily 1K", "category": "Merchants", "type": "Daily",
        "amount": "1000.00", "total": 20, "start_offset": 7, "members": 0,
        "winners": [], "paid_out": 0, "current_paid": 0, "current_pending": 0,
        "applicants": 0, "banks": ["CBE"], "status": "draft",
        "rules": "Draft: not visible to customers until the owner activates it.",
    },
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
    ("When is my payment approved?",
     "The equb owner checks your receipt, usually within one working day. You get a notification when it is approved."),
    ("What if I join after the equb has started?",
     "You pay the contributions for the rounds already completed, so you catch up with the other members."),
]

ADVERTS = [
    ("Save together with Equb Link", "#0F766E"),
    ("Pay your contribution with Chapa", "#1D4ED8"),
    ("New: Weekly Office Savings is open", "#B45309"),
]

TESTIMONIALS = [
    ("Almaz Tadesse", "Shop owner, Merkato",
     "I won round two of my equb and used it to restock my shop. Paying from my phone saves me a trip every month."),
    ("Dawit Haile", "Taxi driver",
     "The daily equb fits how I earn. I can see who has paid and when the draw is."),
    ("Rahel Mekonnen", "Accountant",
     "Every draw is recorded, so our group trusts the result."),
]


def banner(text, colour, size):
    """A plain coloured PNG with centred text, so seeded images are not blank."""
    img = Image.new("RGB", size, colour)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=max(18, size[1] // 9))
    box = draw.textbbox((0, 0), text, font=font)
    x = (size[0] - (box[2] - box[0])) / 2
    y = (size[1] - (box[3] - box[1])) / 2
    draw.text((x, y), text, fill="white", font=font)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return ContentFile(buf.getvalue())


def slug(text):
    return "".join(c.lower() if c.isalnum() else "-" for c in text).strip("-")


class Command(BaseCommand):
    help = "Seed the demo accounts, catalogue and equb history described in the submission documents."

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
        self.now = timezone.now()

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
        self.stdout.write(
            f"  {len(MEMBER_NAMES)} more members: +251911001001 to +2519110010{len(MEMBER_NAMES):02d}, same password"
        )

    # ------------------------------------------------------------------
    def account(self, info, create, profile_model, quiet=False, **flags):
        user = User.objects.filter(phone=info["phone"]).first()
        if user is None:
            user = create(info["phone"], self.password, info["email"])
            if not quiet:
                self.stdout.write(f"created account {info['phone']}")
        elif self.reset:
            user.set_password(self.password)
            user.save()
            if not quiet:
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

    def notify(self, user, notif_type, message, **extra):
        Notification.objects.get_or_create(
            user=user, notif_type=notif_type, message=message, defaults=extra
        )

    def seed(self):
        admin = self.account(
            ADMIN, User.objects.create_superuser, Admin, is_admin=True, is_staff=True
        )
        owner = self.account(OWNER, User.objects.create_equb_admin, EqubAdmin, is_equb_admin=True)
        abebe = self.account(CUSTOMER, User.objects.create_customer, Customer, is_customer=True)
        self.account(CUSTOMER_2, User.objects.create_customer, Customer, is_customer=True)
        members = [
            self.account(
                {"phone": f"+2519110010{i:02d}", "name": name, "email": None},
                User.objects.create_customer, Customer, quiet=True, is_customer=True,
            )
            for i, name in enumerate(MEMBER_NAMES, start=1)
        ]
        self.stdout.write(f"{len(members)} member accounts ready")

        config = AppConfig.load()
        config.latest_version = "1.2.0"
        config.force_update = False
        config.save()

        self.seed_catalogue(owner)
        self.seed_equbs(owner, abebe, members)
        self.seed_content(abebe, admin)

    def seed_catalogue(self, owner):
        self.types, self.period = {}, {}
        for name, desc, days in EQUB_TYPES:
            self.types[name], _ = EqubType.objects.get_or_create(name=name, defaults={"description": desc})
            self.period[name] = days

        self.categories = {}
        for name, desc, fav, colour in CATEGORIES:
            cat, _ = EqubCategory.objects.get_or_create(
                name=name, defaults={"description": desc, "is_favorite": fav}
            )
            if not cat.image:
                cat.image.save(f"{slug(name)}.png", banner(name, colour, (512, 512)), save=True)
            self.categories[name] = cat

        self.banks = {}
        for code, number, label in BANK_ACCOUNTS:
            self.banks[code], _ = OwnerBankAccount.objects.get_or_create(
                owner=owner, bank_code=code, account_number=number,
                defaults={"account_holder_name": OWNER["name"], "label": label},
            )
        self.stdout.write(f"{len(self.categories)} categories, {len(self.types)} frequencies, "
                          f"{len(self.banks)} payout accounts ready")

    def seed_equbs(self, owner, abebe, members):
        pool = iter(members)
        today = date.today()
        for spec in EQUBS:
            days = self.period[spec["type"]]
            start = today + timedelta(days=days * spec["start_offset"])
            current_round = len(spec["winners"]) + 1
            # update_or_create so reruns realign dates with the seeded round history.
            equb, created = Equb.objects.update_or_create(
                name=spec["name"], owner=owner,
                defaults={
                    "category": self.categories[spec["category"]],
                    "equb_type": self.types[spec["type"]],
                    "start_date": start,
                    "end_date": start + timedelta(days=days * spec["total"]),
                    "lottery_draw_schedule": start + timedelta(days=days * current_round),
                    "rules": spec["rules"],
                    "rules_approved": True,
                    "payout_system": "random",
                    "total_members": spec["total"],
                    "contribution_amount": Decimal(spec["amount"]),
                    "status": spec["status"],
                },
            )
            equb.payout_bank_accounts.add(*(self.banks[c] for c in spec["banks"]))

            users = [next(pool) for _ in range(spec["members"])]
            if spec["name"] == "Monthly 10K":
                users.insert(0, abebe)  # Abebe is never a winner here, so he is still in the draw
            active = [self.member(equb, u, "active") for u in users]
            applicants = [self.member(equb, next(pool), "pending") for _ in range(spec["applicants"])]

            self.seed_history(equb, spec, active, owner, start, days)
            for m in applicants:
                self.join_request(equb, m, owner)
            self.stdout.write(
                f"{'created' if created else 'updated'} equb {equb.name}: "
                f"{len(active)}/{spec['total']} members, round {current_round}"
            )

    def member(self, equb, user, status):
        m, _ = EqubMember.objects.get_or_create(
            user=user, equb=equb,
            defaults={"status": status, "payment_status": "paid" if status == "active" else "pending"},
        )
        if status == "active":
            AuditLog.objects.get_or_create(
                user=equb.owner, action="approve_member", target=str(m.id),
                defaults={"meta": {"equb": str(equb.id), "seeded": True}},
            )
        return m

    def pay(self, member, rnd, status, when, owner):
        payment, created = Payment.objects.get_or_create(
            equb_member=member, round_number=rnd,
            defaults={
                "amount": member.equb.contribution_amount,
                "payment_method": "bank",
                "transaction_id": f"DEMO-{str(member.id)[:8].upper()}-R{rnd}",
                "status": status,
                "paid_at": when,
                "approved_by": owner if status == "completed" else None,
                "approved_at": when if status == "completed" else None,
            },
        )
        if created and status == "completed":
            AuditLog.objects.create(
                user=owner, action="approve_payment", target=str(payment.id),
                meta={"equb": str(member.equb_id), "round": rnd, "seeded": True},
            )
            self.notify(
                member.user, "payment_approved",
                f"Your ETB {payment.amount:,.2f} payment for {member.equb.name}, round {rnd}, was approved.",
            )
        elif created:
            self.notify(
                owner, "payment_submitted",
                f"{member.user.customer.name} submitted ETB {payment.amount:,.2f} for "
                f"{member.equb.name}, round {rnd}.",
            )
            self.notify(
                member.user, "payment_submitted",
                f"Your payment for {member.equb.name}, round {rnd}, is waiting for approval.",
            )
        return payment

    def seed_history(self, equb, spec, active, owner, start, days):
        def round_date(r):
            day = start + timedelta(days=days * (r - 1))
            return timezone.make_aware(datetime.combine(day, time(10, 0)))

        # Completed rounds: everyone paid, then a winner was drawn.
        for rnd, winner_idx in enumerate(spec["winners"], start=1):
            for m in active:
                self.pay(m, rnd, "completed", round_date(rnd), owner)
            winner = active[winner_idx]
            drawn_at = round_date(rnd) + timedelta(days=min(days, 3))
            LotteryRound.objects.get_or_create(
                equb=equb, round=rnd,
                defaults={
                    "winner": winner.user,
                    "seed": secrets.token_hex(16),
                    "drawn_at": drawn_at,
                    "is_paid": rnd <= spec["paid_out"],
                },
            )
            _, won = LotteryWinner.objects.get_or_create(
                equb=equb, round_number=rnd, defaults={"winner": winner}
            )
            if not winner.has_received_payout:
                winner.has_received_payout = True
                winner.save()
            if won:
                for m in active:
                    self.notify(
                        m.user, "system",
                        f"Round {rnd} of {equb.name} was drawn. "
                        f"Winner: {winner.user.customer.name} (ETB {equb.total_payout:,.2f}).",
                    )

        # Current round: some paid, some waiting for approval, the rest not yet paid.
        if equb.status == "active" and spec["start_offset"] <= 0:
            rnd = len(spec["winners"]) + 1
            for i, m in enumerate(active):
                if i < spec["current_paid"]:
                    self.pay(m, rnd, "completed", self.now - timedelta(hours=i + 1), owner)
                elif i < spec["current_paid"] + spec["current_pending"]:
                    self.pay(m, rnd, "pending", self.now - timedelta(minutes=30 * i), owner)

    def join_request(self, equb, member, owner):
        Payment.objects.get_or_create(
            equb_member=member, round_number=0,
            defaults={
                "amount": equb.contribution_amount,
                "payment_method": "bank",
                "transaction_id": f"DEMO-{str(member.id)[:8].upper()}-JOIN",
                "status": "pending",
            },
        )
        name = member.user.customer.name
        self.notify(
            member.user, "join_request_submitted",
            f"Your join request for {equb.name} has been submitted. "
            f"First-round payment is pending admin approval.",
        )
        self.notify(owner, "join_request", f"{name} asked to join {equb.name}.")

    def seed_content(self, abebe, admin):
        for question, answer in FAQS:
            FAQ.objects.get_or_create(question=question, defaults={"answer": answer})

        for title, colour in ADVERTS:
            ad, _ = Advert.objects.get_or_create(title=title)
            if not ad.images:
                ad.images.save(f"{slug(title)}.png", banner(title, colour, (1200, 600)), save=True)

        for name, position, text in TESTIMONIALS:
            Testimonial.objects.get_or_create(
                name=name, defaults={"postion": position, "description": text}
            )

        for subject, message, status in [
            ("Receipt upload failed",
             "My CBE receipt would not upload yesterday. It worked after I cropped the image.", "resolved"),
            ("Change of payout account",
             "I would like my winnings paid to my Telebirr account instead of CBE.", "open"),
        ]:
            _, created = SupportTicket.objects.get_or_create(
                user=abebe, subject=subject, defaults={"message": message, "status": status}
            )
            if created and status == "open":
                self.notify(admin, "support_ticket", f"New support ticket from Abebe Kebede: {subject}")

        self.notify(
            abebe, "system",
            "Welcome to Equb Link! Your membership in Monthly 10K is active.",
            is_pinned=True, is_read=True,
        )
        self.stdout.write(
            f"{len(FAQS)} FAQs, {len(ADVERTS)} adverts, {len(TESTIMONIALS)} testimonials, 2 support tickets ready"
        )
