from rest_framework import status
from rest_framework.exceptions import APIException


class NoRightToViewReviews(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'The author has no published bids to this tender'
