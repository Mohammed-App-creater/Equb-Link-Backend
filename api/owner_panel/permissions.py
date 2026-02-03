from rest_framework.permissions import BasePermission
from owner_panel.models import LotteryRound
from rest_framework import serializers 


class IsEqubOwner(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_equb_admin
        )

    def has_object_permission(self, request, view, obj):

        # If object is Equb
        if hasattr(obj, "owner"):
            return obj.owner == request.user

        # If nested object
        if hasattr(obj, "equb"):
            return obj.equb.owner == request.user

        return False
    
class OwnerRoundSerializer(serializers.ModelSerializer):

    winner_id = serializers.UUIDField(
        source="winner.id",
        read_only=True
    )

    class Meta:
        model = LotteryRound
        fields = [
            "round",
            "winner_id",
            "is_paid",
            "drawn_at"
        ]

