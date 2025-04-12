from django.urls import path
from .views import (
    RoomCreateView,
    RoomDeleteView,
    RoomListView,
    BookingCreateView,
    BookingDeleteView,
    BookingListView,
)

urlpatterns = [
    path("rooms/create", RoomCreateView.as_view(), name="room-create"),
    path("rooms/delete/<int:pk>", RoomDeleteView.as_view(), name="room-delete"),
    path("rooms/list", RoomListView.as_view(), name="room-list"),
    path("bookings/create", BookingCreateView.as_view(), name="booking-create"),
    path(
        "bookings/delete/<int:pk>", BookingDeleteView.as_view(), name="booking-delete"
    ),
    path("bookings/list", BookingListView.as_view(), name="booking-list"),
]
