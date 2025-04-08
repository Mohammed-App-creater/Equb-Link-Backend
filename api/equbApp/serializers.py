from rest_framework import serializers
from .models import (
    EqubType, EqubCategory, EqubSubCategory,
    Equb, EqubMember, Payment, LotteryWinner,
    Notification, SupportTicket
)
from user.models import User


# Basic User Serializer for nested representations
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class EqubTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EqubType
        fields = '__all__'


class EqubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EqubCategory
        fields = '__all__'


class EqubSubCategorySerializer(serializers.ModelSerializer):
    category = EqubCategorySerializer(read_only=True)
    default_equb_type = EqubTypeSerializer(read_only=True)

    class Meta:
        model = EqubSubCategory
        fields = '__all__'

class EqubSubCategoryPostSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=EqubCategory.objects.all()
    )
    default_equb_type = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=EqubType.objects.all()
    )

    class Meta:
        model = EqubSubCategory
        fields = '__all__'



class EqubSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    subcategory = EqubSubCategorySerializer(read_only=True)
    equb_type = EqubTypeSerializer(read_only=True)

    class Meta:
        model = Equb
        fields = '__all__'

class EqubPostSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    subcategory = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=EqubSubCategory.objects.all()
    )
    equb_type = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=EqubType.objects.all()
    )

    class Meta:
        model = Equb
        fields = '__all__'

class SubCategoryWithEqubsSerializer(serializers.ModelSerializer):
    equbs = EqubSerializer(many=True, read_only=True)  # uses related_name on Equb.subcategory

    class Meta:
        model = EqubSubCategory
        fields = ['id', 'name', 'category', 'default_equb_type', 'equbs']



class EqubMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    equb = EqubSerializer(read_only=True)

    class Meta:
        model = EqubMember
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    equb_member = EqubMemberSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'


class LotteryWinnerSerializer(serializers.ModelSerializer):
    equb = EqubSerializer(read_only=True)
    winner = UserSerializer(read_only=True)

    class Meta:
        model = LotteryWinner
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'


class SupportTicketSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = SupportTicket
        fields = '__all__'


