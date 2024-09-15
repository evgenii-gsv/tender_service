from rest_framework import serializers, status

from tender_service.organizations.models import Employee, Organization

from .models import Tender, TenderServiceType


class TenderSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=500)
    status = serializers.CharField(max_length=20, read_only=True)
    serviceType = serializers.CharField(max_length=20)
    version = serializers.IntegerField(read_only=True)
    createdAt = serializers.DateTimeField(read_only=True)
    organizationId = serializers.UUIDField(write_only=True)
    creatorUsername = serializers.CharField(write_only=True)

    def create(self, validated_data):
        tender = Tender.objects.create(
            name=validated_data['name'],
            description=validated_data['description'],
            serviceType=validated_data['serviceType'],
            organization=self.organization,
        )
        tender.create_tender_version()
        return tender

    def update(self, instance: Tender, validated_data):
        name = validated_data.get('name')
        description = validated_data.get('description')
        serviceType = validated_data.get('serviceType')
        status = validated_data.get('status')

        instance.name = name or instance.name
        instance.description = description or instance.description
        instance.serviceType = serviceType or instance.serviceType
        instance.status = status or instance.status

        # Increment version number
        if any((name, description, serviceType, status)):
            instance.increment_version()

        return instance

    def validate_creatorUsername(self, value):
        try:
            self.creator = Employee.objects.get(username=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError(f'No user with username "{value}"', status.HTTP_401_UNAUTHORIZED)
        return value

    def validate_organizationId(self, value):
        try:
            self.organization = Organization.objects.get(pk=value)
        except Organization.DoesNotExist:
            raise serializers.ValidationError(f'No organization with id "{value}"', status.HTTP_401_UNAUTHORIZED)
        return value

    def validate_serviceType(self, value):
        value = value.capitalize()
        if value not in TenderServiceType.values:
            raise serializers.ValidationError(
                f'Invalid service type: {value}. Allowed values are: {", ".join(TenderServiceType.values)}',
                status.HTTP_400_BAD_REQUEST
            )
        return value

    def validate(self, data):
        if not self.organization.employees.contains(self.creator):
            raise serializers.ValidationError(
                f'{self.creator} is not responsible for organization {self.organization.pk}.',
                status.HTTP_403_FORBIDDEN
            )
        return data
