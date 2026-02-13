from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.permissions import BasePermission


class EventViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]


class IsOrganizerOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        # Allow GET requests for everyone
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        # Allow POST, PATCH, DELETE only for admins
        return request.user and request.user.is_staff
