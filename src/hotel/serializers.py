from rest_framework import serializers
from .models import Room, Booking
from decimal import Decimal


class RoomSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("0.01")
    )

    class Meta:
        model = Room
        fields = ["id", "description", "price", "created_at"]


class BookingSerializer(serializers.ModelSerializer):
    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(), source="room", write_only=True
    )

    class Meta:
        model = Booking
        fields = ["id", "room_id", "start_date", "end_date"]
        read_only_fields = ["id"]

    def validate(self, data):
        if data["start_date"] >= data["end_date"]:
            raise serializers.ValidationError(
                "Дата окончания должна быть позже даты начала."
            )
        room = data["room"]
        overlapping_bookings = Booking.objects.filter(
            room=room, start_date__lt=data["end_date"], end_date__gt=data["start_date"]
        )
        if overlapping_bookings.exists():
            raise serializers.ValidationError(
                "Номер уже забронирован на выбранные даты."
            )
        return data


class BookingListSerializer(serializers.ModelSerializer):
    booking_id = serializers.IntegerField(source="id")

    class Meta:
        model = Booking
        fields = ["booking_id", "start_date", "end_date"]
