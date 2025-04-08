from rest_framework import serializers

from advert.models import Advert, Testimonial
from .models import *


class AdevertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advert
        fields = ["id", "title", "images", "wallet"]


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ["id", "name", "postion", "images", "description"]


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = "__all__"


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'
