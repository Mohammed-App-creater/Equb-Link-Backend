import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from user.models import User



# EqubType Model with UUID as primary key
class EqubType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# EqubCategory Model with UUID as primary key
class EqubCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='equb_categories/', null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return self.name

# EqubSubCategory Model with UUID as primary key
class EqubSubCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(EqubCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='sub_equb_categories/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    default_equb_type = models.ForeignKey(EqubType, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

# Equb Model with UUID as primary key
class Equb(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='equbs')
    subcategory = models.ForeignKey(EqubSubCategory, on_delete=models.CASCADE, related_name='equbs')
    start_date = models.DateField()
    end_date = models.DateField()
    lottery_draw_schedule = models.TextField()
    rules_and_conditions = models.TextField()
    rules_and_condit_status = models.BooleanField(default=False)
    payout_system = models.CharField(
        max_length=50,
        choices=[
            ('first_come_first_serve', 'First Come First Serve'),
            ('random', 'Random')
        ]
    )
    total_number_of_members = models.PositiveIntegerField(default=10)  
    payment_at_each_round = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# EqubMember Model with UUID as primary key
class EqubMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    equb = models.ForeignKey(Equb, on_delete=models.CASCADE)
    total_members = models.IntegerField()
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')
    joined_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('paid', 'Paid')], default='pending')

    def __str__(self):
        return f'{self.user.full_name} - {self.equb.name}'

# Payment Model with UUID as primary key
class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    equb_member = models.ForeignKey(EqubMember, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100)
    paid_at = models.DateTimeField(null=True, blank=True)
    recipt_image = models.ImageField(upload_to='recipt_categories/', null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending')

    def __str__(self):
        return f'Payment {self.transaction_id} for {self.equb_member.user.name}'

# LotteryWinner Model with UUID as primary key
class LotteryWinner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    equb = models.ForeignKey(Equb, on_delete=models.CASCADE)
    winner = models.ForeignKey(User, on_delete=models.CASCADE)
    draw_date = models.DateTimeField()

    def __str__(self):
        return f'{self.winner.full_name} - {self.equb.name}'

# Notification Model with UUID as primary key
class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notif_type = models.CharField(max_length=50)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification for {self.user.name}'

# SupportTicket Model with UUID as primary key
class SupportTicket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=50, choices=[('open', 'Open'), ('resolved', 'Resolved')], default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Support Ticket - {self.subject}'
