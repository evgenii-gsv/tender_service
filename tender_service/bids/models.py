import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models

from tender_service.organizations.models import Employee
from tender_service.tenders.models import Tender


class BidStatus(models.TextChoices):
    CREATED = 'Created', 'Created'
    PUBLISHED = 'Published', 'Published'
    CANCELED = 'Canceled', 'Canceled'


class BidDecisionVariants(models.TextChoices):
    APPROVED = 'Approved', 'Approved'
    REJECTED = 'Rejected', 'Rejected'


class PublishedBidManager(models.Manager):

    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(status=BidStatus.PUBLISHED)


class Bid(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    status = models.CharField(max_length=20, choices=BidStatus, default=BidStatus.CREATED)
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='bids')
    authorType = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    authorId = models.UUIDField()
    author = GenericForeignKey('authorType', 'authorId')
    version = models.IntegerField(default=1)
    createdAt = models.DateTimeField(auto_now_add=True)
    approved = models.IntegerField(default=0)

    objects = models.Manager()
    published = PublishedBidManager()

    class Meta:
        ordering = ['name']

    def get_quorum(self):
        return min(3, self.tender.organization.employees.count())

    def add_decision(self, decision: BidDecisionVariants, author: Employee) -> None:
        if self.decisions.filter(author=author).exists():  # type: ignore
            raise ValidationError('User already voted.')
        bid_decision = BidDecision.objects.create(bid=self, author=author, decision=decision)
        if bid_decision.decision == BidDecisionVariants.REJECTED:
            self.close_bid()
        elif self.count_positive_decisions() >= self.get_quorum():
            self.tender.close()

    def close_bid(self):
        self.status = BidStatus.CANCELED
        self.increment_version()

    def create_bid_version(self) -> None:
        BidVersion.objects.create(
            bid=self, name=self.name, description=self.description, status=self.status, version=self.version
        )

    def increment_version(self) -> None:
        self.version += 1
        self.save()
        self.create_bid_version()

    def rollback_bid(self, bid_version) -> None:
        self.name = bid_version.name
        self.description = bid_version.description
        self.status = bid_version.status
        self.increment_version()

    def count_positive_decisions(self) -> int:
        return self.decisions.filter(decision=BidDecisionVariants.APPROVED).count()  # type: ignore


class BidVersion(models.Model):
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    status = models.CharField(max_length=20, choices=BidStatus)
    version = models.IntegerField()


class BidReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE)
    description = models.TextField(max_length=1000)
    createdAt = models.DateTimeField(auto_now_add=True)


class BidDecision(models.Model):
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name='decisions')
    author = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='decisions')
    decision = models.CharField(max_length=20, choices=BidDecisionVariants)
