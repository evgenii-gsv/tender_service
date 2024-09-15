import uuid

from django.db import models

from tender_service.organizations.models import Organization


class TenderStatus(models.TextChoices):
    CREATED = 'Created', 'Created'
    PUBLISHED = 'Published', 'Published'
    CLOSED = 'Closed', 'Closed'


class TenderServiceType(models.TextChoices):
    CONSTRUCTION = 'Construction', 'Construction'
    DELIVERY = 'Delivery', 'Delivery'
    MANUFACTURE = 'Manufacture', 'Manufacture'


class TenderPublishedManager(models.Manager):

    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(status=TenderStatus.PUBLISHED)


class Tender(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    serviceType = models.CharField(max_length=20, choices=TenderServiceType)
    status = models.CharField(max_length=20, choices=TenderStatus, default=TenderStatus.CREATED)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='tenders')
    createdAt = models.DateTimeField(auto_now_add=True)
    version = models.IntegerField(default=1)

    objects = models.Manager()
    published = TenderPublishedManager()

    class Meta:
        ordering = ['name']

    def close(self) -> None:
        self.status = TenderStatus.CLOSED
        self.increment_version()

    def create_tender_version(self) -> None:
        TenderVersion.objects.create(
            tender=self,
            name=self.name,
            description=self.description,
            status=self.status,
            serviceType=self.serviceType,
            version=self.version
        )

    def rollback_tender(self, tender_version) -> None:
        self.name = tender_version.name
        self.description = tender_version.description
        self.status = tender_version.status
        self.serviceType = tender_version.serviceType
        self.increment_version()

    def increment_version(self) -> None:
        self.version += 1
        self.save()
        self.create_tender_version()


class TenderVersion(models.Model):
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='versions')
    name = models.CharField(max_length=100)
    description = models.TextField()
    serviceType = models.CharField(max_length=20, choices=TenderServiceType)
    status = models.CharField(max_length=20, choices=TenderStatus, default=TenderStatus.CREATED)  # type: ignore
    createdAt = models.DateTimeField(auto_now_add=True)
    version = models.IntegerField()
