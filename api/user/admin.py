from django.contrib import admin

from user.models import  EqubAdmin, Customer




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
