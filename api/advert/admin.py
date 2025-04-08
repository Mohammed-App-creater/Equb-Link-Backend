from django.contrib import admin

# Register your models here.

from advert.models import Advert, Testimonial

admin.site.register(Advert)
admin.site.register(Testimonial)
