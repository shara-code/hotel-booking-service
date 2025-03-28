from rest_framework import serializers
from .models import Room, Booking


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "description", "price", "date_added"]


class BookingSerializer(serializers.ModelSerializer):
    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(), source="room", write_only=True
    )

    class Meta:
        model = Booking
        fields = ["id", "room_id", "date_start", "date_end"]
        read_only_fields = ["id"]

    def validate(self, data):
        if data["date_start"] >= data["date_end"]:
            raise serializers.ValidationError("End date must be after start date.")
        room = data["room"]
        overlapping_bookings = Booking.objects.filter(
            room=room, date_start__lt=data["date_end"], date_end__gt=data["date_start"]
        )
        if overlapping_bookings.exists():
            raise serializers.ValidationError(
                "The room is already booked for the selected dates."
            )
        return data


class BookingListSerializer(serializers.ModelSerializer):
    booking_id = serializers.IntegerField(source="id")

    class Meta:
        model = Booking
        fields = ["booking_id", "date_start", "date_end"]
