from django.db import models
from equbApp.models import Equb
from django.conf import settings


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    action = models.CharField(max_length=100)
    target = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    meta = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.user} - {self.action}"

class LotteryRound(models.Model):

    equb = models.ForeignKey(
        Equb,
        related_name="rounds",
        on_delete=models.CASCADE
    )

    round = models.IntegerField()

    winner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    seed = models.CharField(max_length=100)
    drawn_at = models.DateTimeField(null=True, blank=True)

    is_paid = models.BooleanField(default=False)

    class Meta:
        unique_together = ["equb", "round"]

    def __str__(self):
        return f"{self.equb} - Round {self.round}"