from .serializers import BookingListSerializer
from .models import Booking
from rest_framework import generics
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework import status
from rest_framework.response import Response
from .models import Room
from .serializers import RoomSerializer, BookingSerializer
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
    serializer_class = RoomSerializer


class RoomListView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["price", "created_at"]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                description='Параметр сортировки. Допустимые значения: "price", "-price", "created_at", "-created_at".',
                required=False,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


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
    serializer_class = BookingSerializer


class BookingListView(generics.ListAPIView):
    serializer_class = BookingListSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="room_id",
                type=OpenApiTypes.INT,
                description="Идентификатор комнаты для фильтрации бронирований",
                required=False,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        room_id = self.request.query_params.get("room_id")
        if room_id:
            return Booking.objects.filter(room_id=int(room_id)).order_by("start_date")
        return Booking.objects.all()
