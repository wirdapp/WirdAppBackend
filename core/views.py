from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class ChangePasswordViewSet(viewsets.ModelViewSet):
    @action(detail=True, methods=['put'], name='Change Password')
    def change_password(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({**serializer.errors})
        serializer.update(user, serializer.validated_data)
        return Response({**serializer.data})
