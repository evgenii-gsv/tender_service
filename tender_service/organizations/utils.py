from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated

from .models import Employee


def get_employee_by_username(username: str | None, raise_exception: bool = True) -> Employee | None:
    if username is None:
        if raise_exception:
            raise NotAuthenticated('No username provided in query parameters.', code=status.HTTP_401_UNAUTHORIZED)
        return None

    try:
        employee = Employee.objects.get(username=username)
    except Employee.DoesNotExist:
        if raise_exception:
            raise AuthenticationFailed('Invalid username.', status.HTTP_401_UNAUTHORIZED)
        return None
    return employee
