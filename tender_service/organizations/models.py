from django.contrib.contenttypes.fields import GenericRelation
from django.db import models


class Employee(models.Model):
    id = models.UUIDField(primary_key=True)
    username = models.CharField(unique=True, max_length=50)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    bids = GenericRelation(
        'bids.Bid', content_type_field='authorType', object_id_field='authorId', related_query_name='author'
    )

    class Meta:
        managed = False
        db_table = 'employee'

    def __str__(self) -> str:
        return f'{self.username} {self.pk}'


class Organization(models.Model):

    class OrganizationType(models.TextChoices):
        IE = 'IE', 'Individual Enterprise'
        LLC = 'LLC', 'Limited Liability Company'
        JSC = 'JSC', 'Joint Stock Company'

    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=3, choices=OrganizationType, blank=True, null=True)  # type: ignore
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    employees = models.ManyToManyField(Employee, through='OrganizationResponsible', related_name='organizations')

    bids = GenericRelation(
        'bids.Bid', content_type_field='authorType', object_id_field='authorId', related_query_name='author'
    )

    class Meta:
        managed = False
        db_table = 'organization'

    def __str__(self) -> str:
        return f'{self.name} {self.pk}'


class OrganizationResponsible(models.Model):
    id = models.UUIDField(primary_key=True)
    organization = models.ForeignKey(Organization, models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(Employee, models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'organization_responsible'
