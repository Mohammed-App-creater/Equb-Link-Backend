from django.urls import path, include

from advert.views import (
    AdvertGetPostAdmin,
    AdvertGetDeleteUpdateAdmin,
    AdvertGetPublic,faq_list,faq_list_create_admin,faq_detail_admin
    
)


urlpatterns = [
    path("advert/", AdvertGetPostAdmin, name="advert"),
    path("advert/<uuid:id>/", AdvertGetDeleteUpdateAdmin, name="advertbyid"),
    path("advert_public/", AdvertGetPublic, name="advert_public"),

    path('admin/faqs/', faq_list_create_admin, name='faq-list-create-admin'),
    path('admin/faqs/<int:id>/', faq_detail_admin, name='faq-detail-admin'),

    # faq_list_create_admin

    path('faqs/', faq_list, name='faq-list'),

]
