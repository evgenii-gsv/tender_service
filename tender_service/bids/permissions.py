from tender_service.organizations.models import Employee

from .models import Bid


def is_author(employee: Employee, bid: Bid) -> bool:
    return bid in employee.bids.all().union(employee.organizations.first().bids.all())  # type: ignore


def is_responsible(employee: Employee, bid: Bid) -> bool:
    return bid.tender.organization in employee.organizations.all()  # type: ignore
