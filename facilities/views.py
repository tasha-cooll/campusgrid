from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Facility, FacilityHours, FacilityZone, RecurringBlock
from .serializers import (
    FacilitySerializer,
    FacilityWriteSerializer,
    FacilityHoursSerializer,
    FacilityZoneSerializer,
    RecurringBlockSerializer,
)
from accounts.permissions import IsAdmin


class FacilityListView(generics.ListAPIView):
    queryset = Facility.objects.filter(is_active=True).prefetch_related(
        'hours', 'zones', 'recurring_blocks')
    serializer_class = FacilitySerializer
    permission_classes = [IsAuthenticated]


class FacilityCreateView(generics.CreateAPIView):
    queryset = Facility.objects.all()
    serializer_class = FacilityWriteSerializer
    permission_classes = [IsAdmin]


class FacilityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Facility.objects.all().prefetch_related(
        'hours', 'zones', 'recurring_blocks')
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return FacilityWriteSerializer
        return FacilitySerializer

    def destroy(self, request, *args, **kwargs):
        facility = self.get_object()
        facility.is_active = False
        facility.save()
        return Response(
            {"message": f"Facility '{facility.name}' has been deactivated."},
            status=status.HTTP_200_OK
        )


class FacilityHoursView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        hours = FacilityHours.objects.filter(facility_id=pk)
        return Response(FacilityHoursSerializer(hours, many=True).data)

    def post(self, request, pk):
        if not IsAdmin().has_permission(request, self):
            return Response({"error": "Admin access required."}, status=status.HTTP_403_FORBIDDEN)
        try:
            facility = Facility.objects.get(pk=pk)
        except Facility.DoesNotExist:
            return Response({"error": "Facility not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = FacilityHoursSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(facility=facility)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FacilityZoneListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/facilities/<pk>/zones/  — List zones for a facility
    POST /api/facilities/<pk>/zones/  — Add a zone (Admin only)
    """
    serializer_class = FacilityZoneSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FacilityZone.objects.filter(
            facility_id=self.kwargs['pk'],
            is_active=True
        )

    def perform_create(self, serializer):
        if not IsAdmin().has_permission(self.request, self):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Admin access required.")
        facility = Facility.objects.get(pk=self.kwargs['pk'])
        serializer.save(facility=facility)


class RecurringBlockListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/facilities/<pk>/blocks/  — List recurring blocks
    POST /api/facilities/<pk>/blocks/  — Create a block (Admin only)
    """
    serializer_class = RecurringBlockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RecurringBlock.objects.filter(
            facility_id=self.kwargs['pk'],
            is_active=True
        )

    def perform_create(self, serializer):
        if not IsAdmin().has_permission(self.request, self):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Admin access required.")
        facility = Facility.objects.get(pk=self.kwargs['pk'])
        serializer.save(facility=facility, created_by=self.request.user)
