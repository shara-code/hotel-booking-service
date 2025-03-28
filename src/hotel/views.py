from rest_framework import generics, status
from rest_framework.response import Response
from .models import Room, Booking
from .serializers import RoomSerializer, BookingSerializer, BookingListSerializer
from rest_framework import filters


class RoomCreateView(generics.CreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"room_id": serializer.data["id"]},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class RoomDeleteView(generics.DestroyAPIView):
    queryset = Room.objects.all()


class RoomListView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["price", "date_added"]


class BookingCreateView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"booking_id": serializer.data["id"]},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class BookingDeleteView(generics.DestroyAPIView):
    queryset = Booking.objects.all()


class BookingListView(generics.ListAPIView):
    serializer_class = BookingListSerializer

    def get_queryset(self):
        room_id = self.request.query_params.get("room_id")
        if room_id:
            return Booking.objects.filter(room_id=room_id).order_by("date_start")
        else:
            return Booking.objects.none()
