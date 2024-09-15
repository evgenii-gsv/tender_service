from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from tender_service.organizations.models import Employee, Organization
from tender_service.tenders.models import Tender

from .models import Bid, BidReview, BidStatus


class BidSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=500)
    status = serializers.CharField(max_length=20, required=False)
    version = serializers.IntegerField(read_only=True)
    createdAt = serializers.DateTimeField(read_only=True)
    tenderId = serializers.UUIDField(write_only=True)
    authorType = serializers.CharField(max_length=100)
    authorId = serializers.UUIDField(write_only=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        author_type_value = {
            'Organizations | organization': 'Organization',
            'Organizations | employee': 'User',
        }
        representation['authorType'] = author_type_value[representation['authorType']]
        return representation

    def create(self, validated_data):
        author = self.get_author(validated_data['authorId'])

        bid = Bid.objects.create(
            name=validated_data['name'],
            description=validated_data['description'],
            tender=self.tender,
            authorType=self.author_type,
            authorId=validated_data['authorId']
        )
        bid.create_bid_version()
        return bid

    def update(self, instance: Bid, validated_data):
        name = validated_data.get('name')
        description = validated_data.get('description')
        status = validated_data.get('status')

        instance.name = name or instance.name
        instance.description = description or instance.description
        instance.status = status or instance.status

        # Increment version number
        if any((name, description, status)):
            instance.increment_version()

        return instance

    def validate_authorType(self, value):
        if value.lower() == 'user':
            self.author_model = Employee
            self.author_type = ContentType.objects.get(model='employee')
        elif value.lower() == 'organization':
            self.author_model = Organization
            self.author_type = ContentType.objects.get(model='organization')
        else:
            raise serializers.ValidationError(
                f'Invalid authorType: {value}. Allowed authorType are: {", ".join(("User", "Organization"))}'
            )
        return value.capitalize()

    def get_author(self, author_id):
        try:
            author = self.author_model.objects.get(pk=author_id)
        except self.author_model.DoesNotExist:
            raise serializers.ValidationError('Invalid author id.')
        return author

    def validate_tenderId(self, value):
        try:
            self.tender = Tender.objects.get(pk=value)
        except Tender.DoesNotExist:
            raise serializers.ValidationError('Invalid tender id.')
        return value

    def validate_status(self, value):
        value = value.capitalize()
        if value not in BidStatus.values:
            raise serializers.ValidationError(
                f'Invalid status: {value}. Allowed statuses are: {", ".join(BidStatus.values)}'
            )
        return value


class BidReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = BidReview
        fields = ('id', 'description', 'createdAt', 'bid')
        extra_kwargs = {'bid': {'write_only': True}}
