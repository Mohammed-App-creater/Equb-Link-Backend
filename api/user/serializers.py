from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

from .models import Customer, EqubAdmin, Admin


class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = "__all__"


class AdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta(object):
        model = Admin
        fields = "__all__"


class AdminPostSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=User.objects.all()
    )

    class Meta(object):
        model = Admin
        fields = "__all__"




class CustomerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=User.objects.all()
    )


    class Meta(object):
        model = Customer
        fields = "__all__"


class CustomerDataSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta(object):
        model = Customer
        fields = "__all__"


class EqubAdminSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=User.objects.all()
    )


    class Meta(object):
        model = EqubAdmin
        fields = "__all__"


class EqubAdminDataSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta(object):
        model = EqubAdmin
        fields = "__all__"




# from rest_framework import serializers
# from django.contrib.auth import get_user_model

# User = get_user_model()

# from .models import Student, Instructor, Admin, Department


# class UserSerializer(serializers.ModelSerializer):
#     class Meta(object):
#         model = User
#         fields = ["id", "email", "is_admin", "is_instructor", "is_student"]


# class AdminSerializer(serializers.ModelSerializer):
#     user = UserSerializer()

#     class Meta(object):
#         model = Admin
#         fields = ["id", "name", "phone", "photo", "user"]

# class AdminPostSerializer(serializers.ModelSerializer):
#     user = serializers.PrimaryKeyRelatedField(
#         read_only=False, queryset=User.objects.all()
#     )

#     class Meta(object):
#         model = Admin
#         fields = ["id", "name", "phone", "photo", "user"]


# class DepartmentSerializer(serializers.ModelSerializer):
#     class Meta(object):
#         model = Department
#         fields = ["id", "name"]


# class DepartmentSerializer(serializers.ModelSerializer):
#     class Meta(object):
#         model = Department
#         fields = ["id", "name"]


# class StudentSerializer(serializers.ModelSerializer):
#     user = serializers.PrimaryKeyRelatedField(
#         read_only=False, queryset=User.objects.all()
#     )
#     department = serializers.PrimaryKeyRelatedField(
#         allow_null=True, read_only=False, queryset=Department.objects.all()
#     )

#     class Meta(object):
#         model = Student
#         fields = ["id", "name", "phone", "photo", "user", "department", "stream"]


# class StudentDataSerializer(serializers.ModelSerializer):
#     user = UserSerializer()
#     department = DepartmentSerializer()

#     class Meta(object):
#         model = Student
#         fields = ["id", "name", "phone", "photo", "user", "department", "stream", "referral_code", "referred_by", "aff_code", "aff_percent", "aff_paid"]


# class InstructorSerializer(serializers.ModelSerializer):
#     user = serializers.PrimaryKeyRelatedField(
#         read_only=False, queryset=User.objects.all()
#     )
#     department = serializers.PrimaryKeyRelatedField(
#         allow_null=True, read_only=False, queryset=Department.objects.all()
#     )

#     class Meta(object):
#         model = Instructor
#         fields = ["id", "name", "phone", "photo", "user", "department", "stream"]


# class InstructorDataSerializer(serializers.ModelSerializer):
#     user = UserSerializer()
#     department = DepartmentSerializer()

#     class Meta(object):
#         model = Instructor
#         fields = ["id", "name", "phone", "photo", "user", "department", "stream", "earn_percent"]
