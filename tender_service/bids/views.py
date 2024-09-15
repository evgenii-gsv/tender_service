from django.core.exceptions import ValidationError
from rest_framework import exceptions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from tender_service.organizations.utils import get_employee_by_username
from tender_service.tenders.models import Tender
from tender_service.tenders.utils import get_employee_and_tender

from .exceptions import NoRightToViewReviews
from .models import Bid, BidDecisionVariants, BidReview, BidStatus, BidVersion
from .permissions import is_author, is_responsible
from .serializers import BidReviewSerializer, BidSerializer


class BidCreateAPIView(generics.CreateAPIView):
    serializer_class = BidSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(response.data, status=status.HTTP_200_OK)


class MyBidListAPIView(generics.ListAPIView):
    serializer_class = BidSerializer

    def get_queryset(self):
        username = self.request.query_params.get('username')  # type: ignore
        employee = get_employee_by_username(username)

        # getting both bids of the user and of the user's organization
        queryset = employee.bids.all().union(employee.organizations.first().bids.all())  # type: ignore

        return queryset


class TenderBidListAPIView(generics.ListAPIView):
    serializer_class = BidSerializer

    def get_queryset(self):
        username = self.request.query_params.get('username')  # type: ignore
        tender_id = self.kwargs.get('tender_id')
        employee = get_employee_by_username(username)
        try:
            tender = Tender.objects.get(pk=tender_id)
        except Tender.DoesNotExist:
            raise exceptions.NotFound(f'Tender with id "{tender_id}" does not exist.')

        # adding all user bids for this tender
        queryset = employee.bids.filter(tender=tender)  # type: ignore

        # adding all public bids for this tender if employee is responsilbe for tender company
        if tender.organization in employee.organizations.all():  # type: ignore
            queryset.union(Bid.published.filter(tender=tender))

        return queryset


class BidStatusAPIView(APIView):

    def get(self, request, bid_id):
        username = request.query_params.get('username')
        employee = get_employee_by_username(username)
        try:
            bid = Bid.objects.get(pk=bid_id)
        except Bid.DoesNotExist:
            return Response({'reason': 'Invalid bid id.'}, status.HTTP_404_NOT_FOUND)

        if employee and is_author(employee, bid):
            return Response(bid.status, status.HTTP_200_OK)
        return Response({'reason': 'You have no permission.'}, status.HTTP_403_FORBIDDEN)

    def put(self, request, bid_id):
        username = request.query_params.get('username')
        new_status = request.query_params.get('status')
        if not username or not new_status:
            return Response({'reason': 'Username and status query params are required'},
                            status=status.HTTP_400_BAD_REQUEST)
        employee = get_employee_by_username(username)
        try:
            bid = Bid.objects.get(pk=bid_id)
        except Bid.DoesNotExist:
            return Response({'reason': 'Invalid bid id.'}, status.HTTP_404_NOT_FOUND)
        if employee and is_author(employee, bid):
            serializer = BidSerializer(bid, {'status': new_status}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        return Response({'reason': 'You have no permission.'}, status.HTTP_403_FORBIDDEN)


class BidUpdateAPIView(APIView):

    def patch(self, request, bid_id):
        username = request.query_params.get('username')
        data = request.data
        employee = get_employee_by_username(username)
        if len(data) == 0:
            return Response({'reason': 'Data is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            bid = Bid.objects.get(pk=bid_id)
        except Bid.DoesNotExist:
            return Response({'reason': 'Invalid bid id.'}, status.HTTP_404_NOT_FOUND)
        if employee and is_author(employee, bid):
            serializer = BidSerializer(instance=bid, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        return Response({'reason': 'You have no permission.'}, status.HTTP_403_FORBIDDEN)


class BidRollbackAPIView(APIView):

    def put(self, request, bid_id, version):
        username = request.query_params.get('username')
        employee = get_employee_by_username(username)

        try:
            bid = Bid.objects.get(pk=bid_id)
        except Bid.DoesNotExist:
            return Response({'reason': 'Invalid bid id.'}, status.HTTP_404_NOT_FOUND)
        if not (employee and is_author(employee, bid)):
            return Response({'reason': 'You have no permission.'}, status.HTTP_403_FORBIDDEN)
        try:
            bid_version = BidVersion.objects.get(bid=bid, version=version)
        except BidVersion.DoesNotExist:
            return Response({'reason': 'BidVersion not found'}, status=status.HTTP_404_NOT_FOUND)

        bid.rollback_bid(bid_version)
        serializer = BidSerializer(bid)

        return Response(serializer.data, status.HTTP_200_OK)


class BidFeedbackAPIView(APIView):

    def put(self, request, bid_id):
        feedback = request.query_params.get('bidFeedback')
        username = request.query_params.get('username')
        if not feedback or not username:
            return Response({'reason': 'bidFeedback and username query params are required'},
                            status=status.HTTP_400_BAD_REQUEST)
        employee = get_employee_by_username(username)
        try:
            bid = Bid.published.get(pk=bid_id)
        except Bid.DoesNotExist:
            return Response({'reason': 'Invalid bid id or bid not published.'}, status.HTTP_404_NOT_FOUND)
        if not (employee and is_responsible(employee, bid)):
            return Response({'reason': 'You have no permission.'}, status.HTTP_403_FORBIDDEN)
        review_serializer = BidReviewSerializer(data={'description': feedback, 'bid': bid.pk})
        if review_serializer.is_valid():
            review_serializer.save()
            bid_serializer = BidSerializer(bid)
            return Response(bid_serializer.data, status.HTTP_200_OK)
        return Response({'reason': 'Invalid review.'}, status.HTTP_400_BAD_REQUEST)


class BidFeedbackListAPIView(generics.ListAPIView):
    serializer_class = BidReviewSerializer

    def get_queryset(self):
        tender_id = self.kwargs.get('tender_id')
        author_username = self.request.query_params.get('authorUsername')  # type: ignore
        requester_username = self.request.query_params.get('requesterUsername')  # type: ignore

        _, tender = get_employee_and_tender(requester_username, tender_id)
        author = get_employee_by_username(author_username)

        # check if author has any published bids for the tender
        if not author.bids.filter(tender=tender, status=BidStatus.PUBLISHED).exists():  # type: ignore
            raise NoRightToViewReviews()

        queryset = BidReview.objects.filter(bid__in=author.bids.all())  # type: ignore

        if queryset.exists():
            return queryset
        raise exceptions.NotFound('No reviews found.')


class SubmitDecisionAPIView(APIView):

    def put(self, request, bid_id):
        username = request.query_params.get('username')
        decision = request.query_params.get('decision')
        if not decision or not username:
            return Response({'reason': 'decision and username query params are required'},
                            status=status.HTTP_400_BAD_REQUEST)
        employee = get_employee_by_username(username)
        try:
            bid = Bid.published.get(pk=bid_id)
        except Bid.DoesNotExist:
            return Response({'reason': 'Invalid bid id or bid not published.'}, status.HTTP_404_NOT_FOUND)

        if not (employee and is_responsible(employee, bid)):
            return Response({'reason': 'You have no permission.'}, status.HTTP_403_FORBIDDEN)

        decision = decision.capitalize()
        if decision not in BidDecisionVariants.values:
            return Response({
                'reason':
                    f'Invalid decision: {decision}. Allowed statuses are: {", ".join(BidDecisionVariants.values)}'
            },
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            bid.add_decision(decision, employee)
            serializer = BidSerializer(bid)
            return Response(serializer.data, status.HTTP_200_OK)
        except ValidationError:
            return Response({'reason': 'The user has already voted.'}, status=status.HTTP_403_FORBIDDEN)
