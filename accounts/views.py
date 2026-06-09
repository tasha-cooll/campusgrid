from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model

from .serializers import RegisterSerializer, UserSerializer, ChangeRoleSerializer
from .permissions import IsAdmin

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    POST /api/accounts/register/
    Open endpoint — anyone can register.
    Default role is Requester unless set by Admin.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class MeView(APIView):
    """
    GET /api/accounts/me/
    Returns the currently logged-in user's profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UserListView(generics.ListAPIView):
    """
    GET /api/accounts/users/
    Admin only — returns all registered users.
    """
    queryset = User.objects.all().order_by('date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class ChangeRoleView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        old_role = user.role
        serializer = ChangeRoleSerializer(
            user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            from reports.utils import log_action
            log_action(
                actor=request.user,
                action='user_role_changed',
                details=f'Changed {user.username} role from {old_role} to {user.role}',
                target_user=user,
                request=request,
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ToggleUserActiveView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        user.is_active = not user.is_active
        user.save()

        action = 'user_activated' if user.is_active else 'user_deactivated'
        details = f'{"Activated" if user.is_active else "Deactivated"} account for {user.username}'

        from reports.utils import log_action
        log_action(
            actor=request.user,
            action=action,
            details=details,
            target_user=user,
            request=request,
        )

        return Response({
            'id':        user.id,
            'is_active': user.is_active,
            'message':   details,
        })
