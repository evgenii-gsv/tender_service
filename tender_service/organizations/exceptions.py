from rest_framework import status
from rest_framework.exceptions import APIException


class NotResponsible(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'User is not responsible for this organization.'
