from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status, generics

from user.permissions import (
    IsAdminUser,
    IsCustomerUser,
    IsCustomerOrIsAdminUser,
    IsEqubAdminUser,
)

from .models import Advert
from .serializers import AdevertSerializer
from .models import FAQ
from .serializers import FAQSerializer

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def AdvertGetPostAdmin(request):
    """
    List and post a data method AdevertSerializer
    """
    if request.method == "GET":
        advert = Advert.objects.all()
        serializer = AdevertSerializer(advert, many=True)
        return Response(
            {"data": serializer.data, "message": "Get successfully"},
            status=status.HTTP_200_OK,
        )
    elif request.method == "POST":
        serializer = AdevertSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"data": serializer.data, "message": "Created successfully"},
                status=status.HTTP_202_ACCEPTED,
            )
        return Response(
            {"data": serializer.errors, "message": "erorr"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET", "DELETE", "PUT"])
@permission_classes([IsAuthenticated, IsAdminUser])
def AdvertGetDeleteUpdateAdmin(request, id):
    """
    List all Advert, get by id update or delete a new Advert
    """
    if request.method == "GET":
        advert = get_object_or_404(Advert, id=id)
        serializer = AdevertSerializer(advert)
        return Response(
            {"data": serializer.data, "message": "Get successfully"},
            status=status.HTTP_200_OK,
        )
    elif request.method == "DELETE":
        advert = get_object_or_404(Advert, id=id)
        advert.delete()
        return Response(
            {"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )
    elif request.method == "PUT":
        advert = get_object_or_404(Advert, id=id)
        serializer = AdevertSerializer(advert, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"data": serializer.data, "message": "updated successfully"},
            )
        return Response(
            {"data": serializer.errors, "message": "error"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
def AdvertGetPublic(request):
    """
    List and post a data method AdevertSerializer
    """
    if request.method == "GET":
        advert = Advert.objects.all()
        serializer = AdevertSerializer(advert, many=True)
        return Response(
            {"data": serializer.data, "message": "Get successfully"},
            status=status.HTTP_200_OK,
        )
    



# Admin endpoints
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated,IsAdminUser])  # Use custom admin permission if available
def faq_list_create_admin(request):
    if request.method == 'GET':
        faqs = FAQ.objects.all()
        serializer = FAQSerializer(faqs, many=True)
        return Response({"data": serializer.data, "message": "All FAQs retrieved"}, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = FAQSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "FAQ created"}, status=status.HTTP_201_CREATED)
        return Response({"data": serializer.errors, "message": "Validation failed"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated,IsAdminUser])  # Use custom admin permission if available
def faq_detail_admin(request, id):
    faq = get_object_or_404(FAQ, id=id)

    if request.method == 'GET':
        serializer = FAQSerializer(faq)
        return Response({"data": serializer.data, "message": "FAQ retrieved"})

    elif request.method == 'PUT':
        serializer = FAQSerializer(faq, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "FAQ updated"})
        return Response({"data": serializer.errors, "message": "Validation failed"}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        faq.delete()
        return Response({"message": "FAQ deleted"}, status=status.HTTP_204_NO_CONTENT)



# Public endpoint: List all active FAQs
@api_view(['GET'])
def faq_list(request):
    faqs = FAQ.objects.filter(is_active=True)
    serializer = FAQSerializer(faqs, many=True)
    return Response({"data": serializer.data, "message": "FAQs retrieved successfully"}, status=status.HTTP_200_OK)
