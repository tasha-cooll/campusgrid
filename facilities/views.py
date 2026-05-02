from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Facility, FacilityHours
from .serializers import (
    FacilitySerializer,
    FacilityWriteSerializer,
    FacilityHoursSerializer,
)
from accounts.permissions import IsAdmin


class FacilityListView(generics.ListAPIView):
    """
    GET /api/facilities/
    All authenticated users can view the facility list.
    """
    queryset = Facility.objects.filter(
        is_active=True).prefetch_related('hours')
    serializer_class = FacilitySerializer
    permission_classes = [IsAuthenticated]


class FacilityCreateView(generics.CreateAPIView):
    """
    POST /api/facilities/
    Admin only — create a new facility.
    """
    queryset = Facility.objects.all()
    serializer_class = FacilityWriteSerializer
    permission_classes = [IsAdmin]


class FacilityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/facilities/<id>/   — view any authenticated user
    PATCH  /api/facilities/<id>/   — admin only
    DELETE /api/facilities/<id>/   — admin only
    """
    queryset = Facility.objects.all().prefetch_related('hours')
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return FacilityWriteSerializer
        return FacilitySerializer

    def check_permissions(self, request):
        super().check_permissions(request)
        if request.method in ['PATCH', 'PUT', 'DELETE']:
            IsAdmin().has_permission(request, self)
            if not IsAdmin().has_permission(request, self):
                self.permission_denied(request)

    def destroy(self, request, *args, **kwargs):
        facility = self.get_object()
        # Soft delete — mark inactive instead of removing from DB
        facility.is_active = False
        facility.save()
        return Response(
            {"message": f"Facility '{facility.name}' has been deactivated."},
            status=status.HTTP_200_OK
        )


class FacilityHoursView(APIView):
    """
    POST   /api/facilities/<id>/hours/  — Admin sets operating hours
    GET    /api/facilities/<id>/hours/  — Anyone can view hours
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        hours = FacilityHours.objects.filter(facility_id=pk)
        serializer = FacilityHoursSerializer(hours, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        if not IsAdmin().has_permission(request, self):
            return Response(
                {"error": "Admin access required."},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            facility = Facility.objects.get(pk=pk)
        except Facility.DoesNotExist:
            return Response(
                {"error": "Facility not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = FacilityHoursSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(facility=facility)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
