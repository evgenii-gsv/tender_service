from django.shortcuts import get_object_or_404

from tender_service.organizations.exceptions import NotResponsible
from tender_service.organizations.utils import get_employee_by_username

from .models import Tender


def get_employee_and_tender(username, tender_id):
    employee = get_employee_by_username(username)
    tender = get_object_or_404(Tender, pk=tender_id)
    if tender.organization not in employee.organizations.all():  # type: ignore
        raise NotResponsible()

    return employee, tender
