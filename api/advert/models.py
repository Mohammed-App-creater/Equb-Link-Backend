from django.db import models

import uuid


class Advert(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    images = models.ImageField(upload_to="advert-img", null=True, blank=True)
    images2 = models.ImageField(upload_to="advert-img", null=True, blank=True)
    images3 = models.ImageField(upload_to="advert-img", null=True, blank=True)

    def __str__(self) -> str:
        return str(self.id)


class Testimonial(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    postion = models.CharField(max_length=200)
    images = models.ImageField(upload_to="testimonial-img", null=True, blank=True)
    description = models.TextField(max_length=300)

    def __str__(self) -> str:
        return str(self.id)


class Feedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.id)


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question
