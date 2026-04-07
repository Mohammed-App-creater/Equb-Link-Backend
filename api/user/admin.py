from django.contrib import admin
from django.contrib.auth import get_user_model

from user.models import EqubAdmin, Customer

User = get_user_model()


@admin.register(User)
class AccountAdmin(admin.ModelAdmin):
    """Enables autocomplete for Owner bank account → owner FK and similar."""

    list_display = ("phone", "email", "is_equb_admin", "is_customer", "is_active")
    search_fields = ("phone", "email")
    list_filter = ("is_equb_admin", "is_customer", "is_active")


class EqubAdminAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "photo", "user")


class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "photo", "user")


admin.site.register(EqubAdmin, EqubAdminAdmin)
admin.site.register(Customer, CustomerAdmin)



# from django.contrib import admin

# from course.models import Course

# from user.models import Department, Instructor, Student

# class DepartmentAdmin(admin.ModelAdmin):
#     list_display = ("id", "name")


# class InstructorAdmin(admin.ModelAdmin):
#     list_display = ("id", "name", "phone", "photo", "user", "department")


# class StudentAdmin(admin.ModelAdmin):
#     list_display = ("id", "name", "phone", "photo", "user", "department")


# admin.site.register(Department, DepartmentAdmin)

# admin.site.register(Instructor, InstructorAdmin)
# admin.site.register(Student, StudentAdmin)
