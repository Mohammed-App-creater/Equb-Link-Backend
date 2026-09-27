import uuid
from django.db import models
from user.models import User
from django.shortcuts import get_object_or_404
from django.conf import settings


# ===========================
# BASE ABSTRACT MODELS
# ===========================
class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ===========================
# EQUb TYPE
# ===========================
class EqubType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# ===========================
# CATEGORY & SUBCATEGORY
# ===========================
class EqubCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="equb_categories/", null=True, blank=True)
    description = models.TextField(blank=True,)
    is_favorite = models.BooleanField(default=False, null=True, blank=True)  # <-- favorite marker

    def __str__(self):
        return self.name


# ===========================
# OWNER BANK ACCOUNTS (multiple per owner; same or different banks)
# ===========================
class OwnerBankAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owner_bank_accounts",
    )
    bank_code = models.CharField(
        max_length=10,
        help_text="Code from predefined bank list (e.g. CBE, TBR)",
    )
    account_number = models.CharField(max_length=64)
    account_holder_name = models.CharField(max_length=255)
    label = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional label to distinguish accounts (e.g. Personal, Business)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "bank_code", "account_number"],
                name="equbapp_ownerbankaccount_owner_bank_acct_unique",
            )
        ]

    def __str__(self):
        return f"{self.owner_id} {self.bank_code} …{self.account_number[-4:]}"


# ===========================
# EQUb
# ===========================
class Equb(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_equbs"
    )

    category = models.ForeignKey(
        EqubCategory, on_delete=models.PROTECT, related_name="equbs"
    )

    equb_type = models.ForeignKey(
        EqubType, on_delete=models.SET_NULL, null=True, blank=True
    )

    start_date = models.DateField()
    end_date = models.DateField()

    lottery_draw_schedule = models.DateField(null=True, blank=True)

    rules = models.TextField()
    rules_approved = models.BooleanField(default=False)

    payout_system = models.CharField(
        max_length=50,
        choices=[
            ("first_come_first_serve", "First Come First Serve"),
            ("random", "Random (Lottery)"),
        ],
    )

    total_members = models.PositiveIntegerField(default=10)

    # Financial Fields
    contribution_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount each member contributes per round"
    )

    total_payout = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False
    )

    total_equb_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"),
            ("active", "Active"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
    )

    # Owner's saved accounts members can pay to for this equb (optional; can list several)
    payout_bank_accounts = models.ManyToManyField(
        OwnerBankAccount,
        related_name="equbs_payout",
        blank=True,
        help_text="All must belong to this equb's owner.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Calculate total payout per round
        self.total_payout = self.total_members * self.contribution_amount

        # Calculate total equb value (total rounds = total members)
        self.total_equb_value = self.total_payout * self.total_members

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



# ===========================
# EQUb MEMBER
# ===========================
class EqubMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    equb = models.ForeignKey(Equb, on_delete=models.CASCADE, related_name="members")
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending Approval"),
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("removed", "Removed"),
        ],
        default="pending",
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("paid", "Paid")],
        default="pending",
    )
    has_received_payout = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "equb")

    def __str__(self):
        return f"{self.user} - {self.equb}"


# ===========================
# PAYMENT / CONTRIBUTION
# ===========================
class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    equb_member = models.ForeignKey(
        EqubMember, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100)
    chapa_checkout_url = models.URLField(max_length=500, null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    receipt_image = models.ImageField(
        upload_to="receipt_images/", null=True, blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("completed", "Completed"), ("rejected", "Rejected")],
        default="pending",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_payments"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_reason = models.TextField(blank=True, null=True)
    round_number = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("equb_member", "round_number")

    def __str__(self):
        user = self.equb_member.user
        if hasattr(user, "customer"):
            name = user.customer.name
        elif hasattr(user, "equbadmin"):
            name = user.equbadmin.name
        elif hasattr(user, "admin"):
            name = user.admin.name
        else:
            name = user.phone  # fallback if no profile
        return f"Payment {self.transaction_id} for {name}"
# ===========================
# LOTTERY WINNER
# ===========================
class LotteryWinner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    equb = models.ForeignKey(Equb, on_delete=models.CASCADE)
    winner = models.ForeignKey(EqubMember, on_delete=models.CASCADE)
    round_number = models.PositiveIntegerField()
    draw_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("equb", "round_number")

    def __str__(self):
        user = self.user
        if hasattr(user, "customer"):
            name = user.customer.name
        elif hasattr(user, "equbadmin"):
            name = user.equbadmin.name
        elif hasattr(user, "admin"):
            name = user.admin.name
        else:
            name = user.phone
        return f"Notification for {name}"



# ===========================
# NOTIFICATIONS
# ===========================
class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    notif_type = models.CharField(max_length=50)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Try fetching the related profile name
        if hasattr(self.user, "admin"):
            name = self.user.admin.name
        elif hasattr(self.user, "customer"):
            name = self.user.customer.name
        elif hasattr(self.user, "equbadmin"):
            name = self.user.equbadmin.name
        else:
            name = self.user.phone  # fallback

        return f"Notification for {name}"



# ===========================
# SUPPORT TICKETS
# ===========================
class SupportTicket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="support_tickets"
    )
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[
            ("open", "Open"),
            ("in_progress", "In Progress"),
            ("resolved", "Resolved"),
        ],
        default="open",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Support Ticket - {self.subject}"


# ===========================
# APP CONFIG (singleton — drives mobile app version-check)
# ===========================
from django.core.validators import RegexValidator

semver_validator = RegexValidator(
    regex=r"^\d+\.\d+\.\d+$",
    message="Must be valid semver MAJOR.MINOR.PATCH (e.g. 1.2.3).",
)


class AppConfig(models.Model):
    SINGLETON_ID = 1

    id = models.PositiveSmallIntegerField(
        primary_key=True, default=SINGLETON_ID, editable=False
    )
    latest_version = models.CharField(
        max_length=32, default="1.0.0", validators=[semver_validator]
    )
    force_update = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "App Config"
        verbose_name_plural = "App Config"

    def __str__(self):
        return f"v{self.latest_version} (forceUpdate={self.force_update})"

    def save(self, *args, **kwargs):
        self.pk = self.SINGLETON_ID
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=cls.SINGLETON_ID)
        return obj
