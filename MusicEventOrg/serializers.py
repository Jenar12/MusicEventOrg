from django.contrib.auth.models import User
from django.core.mail import send_mail
from rest_framework import serializers

from .models import Venue, Event, Ticket, Payment, Review, Performer, Festival


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'


def get_average_rating(obj):
    return obj.average_rating


class EventSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'

    def get_average_rating(self, obj):
        return obj.average_rating


class PerformerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performer
        fields = ['id', 'name', 'bio', 'image', 'created_at', 'updated_at']


class FestivalSerializer(serializers.ModelSerializer):
    organizer = serializers.StringRelatedField(read_only=True)  # Display organizer username

    class Meta:
        model = Festival
        fields = ['id', 'title', 'description', 'start_date', 'end_date', 'venue', 'organizer', 'created_at',
                  'updated_at']
        read_only_fields = ['organizer']


class TicketSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = '__all__'

    def validate(self, data):
        event = data['event']
        if event.available_seats <= 0:
            raise serializers.ValidationError("No seats available")
        return data


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'user', 'event', 'rating', 'comment', 'created_at']
        read_only_fields = ['user']


# class UserRegistrationSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
#     confirm_password = serializers.CharField(write_only=True)
#
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password', 'confirm_password']
#
#     def validate(self, attrs):
#         if attrs['password'] != attrs['confirm_password']:
#             raise serializers.ValidationError({"password": "Password fields didn't match."})
#         return attrs
#
#     def create(self, validated_data):
#         validated_data.pop('confirm_password')
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=validated_data['password']
#         )
#         send_mail(
#             'Welcome to Our Platform',
#             f'Hello {user.username}, thank you for registering!',
#             'from@example.com',
#             [user.email],
#             fail_silently=False,
#         )
#         return user




# Login Serializer
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


# Registration Serializer
class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'password': 'Passwords do not match!'})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user
