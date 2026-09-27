from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Platform admins only (is_admin or superuser).

    Deliberately NOT DRF's IsAdminUser: that one checks `is_staff`, and equb
    owners are created with is_staff=True for the Django admin site, which
    would let every owner into the platform-admin API.
    """
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_admin or user.is_superuser)
        )


class IsCustomerUser(BasePermission):
    """
    Allows access only to customer users.
    """
    def has_permission(self, request, view):
        is_customeruser = request.user and request.user.is_customer
        if not is_customeruser and request.user:
            # Your ban logic goes here
            pass
        return is_customeruser


class IsEqubAdminUser(BasePermission):
    """
    Allows access only to Equb admin users.
    """
    def has_permission(self, request, view):
        is_equbadminuser = request.user and request.user.is_equb_admin
        if not is_equbadminuser and request.user:
            # Your ban logic goes here
            pass
        return is_equbadminuser


class IsEqubAdminOrIsCustomerUser(BasePermission):
    """
    Allows access only to Equb admin or customer users.
    """
    def has_permission(self, request, view):
        is_equbadminuser = request.user and request.user.is_equb_admin
        is_customeruser = request.user and request.user.is_customer
        if not is_equbadminuser and not is_customeruser:
            # Your ban logic goes here
            pass
        return is_customeruser or is_equbadminuser


class IsEqubAdminOrIsAdminUser(BasePermission):
    """
    Allows access only to Equb admin and admin users.
    """
    def has_permission(self, request, view):
        is_equbadminuser = request.user and request.user.is_equb_admin
        is_adminuser = request.user and request.user.is_admin
        if not is_equbadminuser and not is_adminuser:
            # Your ban logic goes here
            pass
        return is_adminuser or is_equbadminuser


class IsCustomerOrIsAdminUser(BasePermission):
    """
    Allows access only to Customer and admin users.
    """
    def has_permission(self, request, view):
        is_customeruser = request.user and request.user.is_customer
        is_adminuser = request.user and request.user.is_admin
        if not is_customeruser and not is_adminuser:
            # Your ban logic goes here
            pass
        return is_adminuser or is_customeruser


# from rest_framework.permissions import BasePermission


# class IsAdminUser(BasePermission):
#     """
#     Allows access only to admin users.
#     """

#     def has_permission(self, request, view):
#         is_adminuser = request.user and request.user.is_admin
#         if not is_adminuser and request.user:
#             # Your ban logic goes here
#             pass
#         return is_adminuser


# class IsStudentUser(BasePermission):
#     """
#     Allows access only to student users.
#     """

#     def has_permission(self, request, view):
#         is_studentuser = request.user and request.user.is_student
#         if not is_studentuser and request.user:
#             # Your ban logic goes here
#             pass
#         return is_studentuser


# class IsInstuctorUser(BasePermission):
#     """
#     Allows access only to Instuctor users.
#     """

#     def has_permission(self, request, view):
#         is_instructoruser = request.user and request.user.is_instructor
#         if not is_instructoruser and request.user:
#             # Your ban logic goes here
#             pass
#         return is_instructoruser


# class IsInstuctorOrIsStudentUser(BasePermission):
#     """
#     Allows access only to Instuctor users.
#     """

#     def has_permission(self, request, view):
#         is_instructoruser = request.user and request.user.is_instructor
#         is_studentuser = request.user and request.user.is_student
#         if not is_instructoruser and not is_studentuser:
#             # Your ban logic goes here
#             pass
#         return is_studentuser or is_instructoruser


# class IsInstuctorOrIsAdminUser(BasePermission):
#     """
#     Allows access only to Instuctor and admin users.
#     """

#     def has_permission(self, request, view):
#         is_instructoruser = request.user and request.user.is_instructor
#         is_adminuser = request.user and request.user.is_admin
#         if not is_instructoruser and not is_adminuser:
#             # Your ban logic goes here
#             pass
#         return is_adminuser or is_instructoruser


# class IsStudentOrIsAdminUser(BasePermission):
#     """
#     Allows access only to Student and admin users.
#     """

#     def has_permission(self, request, view):
#         is_studentuser = request.user and request.user.is_student
#         is_adminuser = request.user and request.user.is_admin
#         if not is_studentuser and not is_adminuser:
#             # Your ban logic goes here
#             pass
#         return is_adminuser or is_studentuser
