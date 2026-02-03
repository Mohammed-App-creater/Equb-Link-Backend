import uuid
from django.db import models
from user.models import User
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
    paid_at = models.DateTimeField(null=True, blank=True)
    receipt_image = models.ImageField(
        upload_to="receipt_images/", null=True, blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("completed", "Completed")],
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification for {self.user.name}"


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

