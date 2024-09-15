from rest_framework import generics, status, views
from rest_framework.response import Response

from tender_service.organizations.utils import get_employee_by_username

from .models import Tender, TenderStatus, TenderVersion
from .serializers import TenderSerializer
from .utils import get_employee_and_tender


class TenderListAPIView(generics.ListAPIView):
    serializer_class = TenderSerializer

    def get_queryset(self):
        queryset = Tender.published.all()
        service_type = self.request.query_params.get('service_type')  # type: ignore

        if service_type is not None:
            queryset = queryset.filter(serviceType=service_type)
        return queryset


class MyTenderListAPIView(generics.ListAPIView):
    serializer_class = TenderSerializer

    def get_queryset(self):
        username = self.request.query_params.get('username')  # type: ignore
        employee = get_employee_by_username(username)

        return Tender.objects.filter(organization__in=employee.organizations.all())  # type: ignore


class TenderCreateAPIView(generics.CreateAPIView):
    serializer_class = TenderSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(response.data, status=status.HTTP_200_OK)


class TenderUpdateAPIView(views.APIView):

    def patch(self, request, tender_id):
        username = request.query_params.get('username')
        data = request.data
        employee, tender = get_employee_and_tender(username, tender_id)
        if len(data) == 0:
            return Response({'reason': 'Data is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        data.update({
            'organizationId': tender.organization.pk,
            'creatorUsername':
                employee.username  # type: ignore
        })

        serializer = TenderSerializer(instance=tender, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)


class TenderStatusAPIView(views.APIView):

    def get(self, request, tender_id):
        username = request.query_params.get('username')
        _, tender = get_employee_and_tender(username, tender_id)
        return Response(tender.status, status.HTTP_200_OK)

    def put(self, request, tender_id):
        username = request.query_params.get('username')
        new_status = request.query_params.get('status')

        if not username or not new_status:
            return Response({'reason': 'Username and status query params are required'},
                            status=status.HTTP_400_BAD_REQUEST)
        new_status = new_status.capitalize()

        _, tender = get_employee_and_tender(username, tender_id)

        if new_status not in TenderStatus.values:
            return Response({
                'reason': f'Invalid status: {new_status}. Allowed statuses are: {", ".join(TenderStatus.values)}'
            },
                            status=status.HTTP_400_BAD_REQUEST)

        tender.status = new_status
        tender.increment_version()

        serializer = TenderSerializer(tender)

        return Response(serializer.data, status.HTTP_200_OK)


class TenderRollbackAPIView(views.APIView):

    def put(self, request, tender_id, version):
        username = request.query_params.get('username')
        if not username:
            return Response({'reason': 'Username query param is required'}, status=status.HTTP_400_BAD_REQUEST)

        _, tender = get_employee_and_tender(username, tender_id)

        try:
            tender_version = TenderVersion.objects.get(tender=tender, version=version)
        except TenderVersion.DoesNotExist:
            return Response({'reason': 'TenderVersion not found'}, status=status.HTTP_404_NOT_FOUND)

        tender.rollback_tender(tender_version)
        serializer = TenderSerializer(tender)

        return Response(serializer.data, status.HTTP_200_OK)
