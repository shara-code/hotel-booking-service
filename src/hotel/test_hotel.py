import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from .models import Room, Booking
import time


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_create_room_success(api_client):
    url = reverse("room-create")
    data = {"description": "Nice room", "price": "100.00"}
    response = api_client.post(url, data)
    assert response.status_code == 201
    assert "room_id" in response.data
    room_id = response.data["room_id"]
    assert Room.objects.filter(id=room_id).exists()


@pytest.mark.django_db
def test_create_room_invalid_price(api_client):
    url = reverse("room-create")
    data = {"description": "Invalid room", "price": "0.00"}
    response = api_client.post(url, data)
    assert response.status_code == 400
    assert "price" in response.data


@pytest.mark.django_db
def test_create_room_negative_price(api_client):
    url = reverse("room-create")
    data = {"description": "Invalid room", "price": "-10.00"}
    response = api_client.post(url, data)
    assert response.status_code == 400
    assert "price" in response.data


@pytest.mark.django_db
def test_delete_room(api_client):
    room_response = api_client.post(
        reverse("room-create"), {"description": "Room", "price": "100"}
    )
    assert room_response.status_code == 201
    room_id = room_response.data["room_id"]
    delete_url = reverse("room-delete", kwargs={"pk": room_id})
    response = api_client.delete(delete_url)
    assert response.status_code == 204
    assert not Room.objects.filter(id=room_id).exists()


@pytest.mark.django_db
def test_delete_room_with_bookings(api_client):
    room_response = api_client.post(
        reverse("room-create"), {"description": "Room", "price": "100"}
    )
    assert room_response.status_code == 201
    room_id = room_response.data["room_id"]
    booking_response = api_client.post(
        reverse("booking-create"),
        {"room_id": room_id, "date_start": "2023-01-01", "date_end": "2023-01-05"},
    )
    assert booking_response.status_code == 201
    delete_url = reverse("room-delete", kwargs={"pk": room_id})
    api_client.delete(delete_url)
    assert not Room.objects.filter(id=room_id).exists()
    assert not Booking.objects.filter(room_id=room_id).exists()


@pytest.mark.django_db
def test_list_rooms_sorted_by_price(api_client):
    api_client.post(reverse("room-create"), {"description": "Room1", "price": "200"})
    time.sleep(1)
    api_client.post(reverse("room-create"), {"description": "Room2", "price": "100"})
    response = api_client.get(reverse("room-list") + "?ordering=price")
    assert response.status_code == 200
    assert response.data[0]["price"] == "100.00"
    assert response.data[1]["price"] == "200.00"


@pytest.mark.django_db
def test_list_rooms_sorted_by_date_added(api_client):
    api_client.post(reverse("room-create"), {"description": "Room1", "price": "100"})
    time.sleep(1)
    api_client.post(reverse("room-create"), {"description": "Room2", "price": "200"})
    response = api_client.get(reverse("room-list") + "?ordering=date_added")
    assert response.status_code == 200
    assert response.data[0]["description"] == "Room1"
    assert response.data[1]["description"] == "Room2"


@pytest.mark.django_db
def test_create_booking_success(api_client):
    room_response = api_client.post(
        reverse("room-create"), {"description": "Room", "price": "100"}
    )
    assert room_response.status_code == 201
    room_id = room_response.data["room_id"]
    booking_data = {
        "room_id": room_id,
        "date_start": "2023-01-01",
        "date_end": "2023-01-05",
    }
    response = api_client.post(reverse("booking-create"), booking_data)
    assert response.status_code == 201
    assert "booking_id" in response.data
    booking_id = response.data["booking_id"]
    assert Booking.objects.filter(id=booking_id).exists()


@pytest.mark.django_db
def test_create_booking_overlapping_dates(api_client):
    room_response = api_client.post(
        reverse("room-create"), {"description": "Room", "price": "100"}
    )
    assert room_response.status_code == 201
    room_id = room_response.data["room_id"]
    api_client.post(
        reverse("booking-create"),
        {"room_id": room_id, "date_start": "2023-01-01", "date_end": "2023-01-05"},
    )
    overlapping_data = {
        "room_id": room_id,
        "date_start": "2023-01-03",
        "date_end": "2023-01-07",
    }
    response = api_client.post(reverse("booking-create"), overlapping_data)
    assert response.status_code == 400
    assert "non_field_errors" in response.data
    assert "The room is already booked for the selected dates." in str(
        response.data["non_field_errors"]
    )


@pytest.mark.django_db
def test_create_booking_invalid_dates(api_client):
    room_response = api_client.post(
        reverse("room-create"), {"description": "Room", "price": "100"}
    )
    assert room_response.status_code == 201
    room_id = room_response.data["room_id"]
    data = {"room_id": room_id, "date_start": "2023-01-05", "date_end": "2023-01-01"}
    response = api_client.post(reverse("booking-create"), data)
    assert response.status_code == 400
    assert "non_field_errors" in response.data
    assert "End date must be after start date." in str(
        response.data["non_field_errors"]
    )


@pytest.mark.django_db
def test_create_booking_invalid_date_format(api_client):
    room_response = api_client.post(
        reverse("room-create"), {"description": "Room", "price": "100"}
    )
    assert room_response.status_code == 201
    room_id = room_response.data["room_id"]
    data = {"room_id": room_id, "date_start": "01-01-2023", "date_end": "01-05-2023"}
    response = api_client.post(reverse("booking-create"), data)
    assert response.status_code == 400
    assert "date_start" in response.data


@pytest.mark.django_db
def test_create_booking_invalid_date_value(api_client):
    room_response = api_client.post(
        reverse("room-create"), {"description": "Room", "price": "100"}
    )
    assert room_response.status_code == 201
    room_id = room_response.data["room_id"]
    data = {"room_id": room_id, "date_start": "2023-02-30", "date_end": "2023-03-05"}
    response = api_client.post(reverse("booking-create"), data)
    assert response.status_code == 400
    assert "date_start" in response.data


@pytest.mark.django_db
def test_create_booking_nonexistent_room(api_client):
    data = {"room_id": 9999, "date_start": "2023-01-01", "date_end": "2023-01-05"}
    response = api_client.post(reverse("booking-create"), data)
    assert response.status_code == 400
    assert "room_id" in response.data
    assert (
        str(response.data["room_id"][0]) == 'Invalid pk "9999" - object does not exist.'
    )


@pytest.mark.django_db
def test_delete_booking(api_client):
    room_response = api_client.post(
        reverse("room-create"), {"description": "Room", "price": "100"}
    )
    assert room_response.status_code == 201
    room_id = room_response.data["room_id"]
    booking_response = api_client.post(
        reverse("booking-create"),
        {"room_id": room_id, "date_start": "2023-01-01", "date_end": "2023-01-05"},
    )
    assert booking_response.status_code == 201
    booking_id = booking_response.data["booking_id"]
    delete_url = reverse("booking-delete", kwargs={"pk": booking_id})
    response = api_client.delete(delete_url)
    assert response.status_code == 204
    assert not Booking.objects.filter(id=booking_id).exists()


@pytest.mark.django_db
def test_list_bookings_for_room(api_client):
    room_response = api_client.post(
        reverse("room-create"), {"description": "Room", "price": "100"}
    )
    assert room_response.status_code == 201
    room_id = room_response.data["room_id"]
    api_client.post(
        reverse("booking-create"),
        {"room_id": room_id, "date_start": "2023-01-10", "date_end": "2023-01-15"},
    )
    api_client.post(
        reverse("booking-create"),
        {"room_id": room_id, "date_start": "2023-01-01", "date_end": "2023-01-05"},
    )
    response = api_client.get(reverse("booking-list") + f"?room_id={room_id}")
    assert response.status_code == 200
    assert len(response.data) == 2
    assert response.data[0]["date_start"] == "2023-01-01"
    assert response.data[1]["date_start"] == "2023-01-10"
    assert "booking_id" in response.data[0]


@pytest.mark.django_db
def test_list_bookings_no_room_id(api_client):
    response = api_client.get(reverse("booking-list"))
    assert response.status_code == 200
    assert len(response.data) == 0


@pytest.mark.django_db
def test_delete_nonexistent_room(api_client):
    response = api_client.delete(reverse("room-delete", kwargs={"pk": 9999}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_nonexistent_booking(api_client):
    response = api_client.delete(reverse("booking-delete", kwargs={"pk": 9999}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_booking_on_boundary(api_client):
    """Тест бронирования на границе дат существующего бронирования"""
    room_response = api_client.post(
        reverse("room-create"), {"description": "Test Room", "price": "100"}
    )
    assert room_response.status_code == 201
    room_id = room_response.data["room_id"]

    booking1 = api_client.post(
        reverse("booking-create"),
        {"room_id": room_id, "date_start": "2023-01-01", "date_end": "2023-01-05"},
    )
    assert booking1.status_code == 201

    booking2 = api_client.post(
        reverse("booking-create"),
        {"room_id": room_id, "date_start": "2023-01-05", "date_end": "2023-01-10"},
    )
    assert booking2.status_code == 201

    assert Booking.objects.filter(room_id=room_id).count() == 2


@pytest.mark.django_db
def test_list_rooms_sorted_by_price_desc(api_client):
    """Тест сортировки списка номеров по цене в убывающем порядке"""
    api_client.post(reverse("room-create"), {"description": "Room1", "price": "100"})
    api_client.post(reverse("room-create"), {"description": "Room2", "price": "200"})
    api_client.post(reverse("room-create"), {"description": "Room3", "price": "150"})

    response = api_client.get(reverse("room-list") + "?ordering=-price")
    assert response.status_code == 200

    assert response.data[0]["price"] == "200.00"
    assert response.data[1]["price"] == "150.00"
    assert response.data[2]["price"] == "100.00"


@pytest.mark.django_db
def test_list_bookings_sorted_by_date_start_desc(api_client):
    """Тест сортировки списка бронирований по дате начала в убывающем порядке"""
    room_response = api_client.post(
        reverse("room-create"), {"description": "Test Room", "price": "100"}
    )
    assert room_response.status_code == 201
    room_id = room_response.data["room_id"]

    api_client.post(
        reverse("booking-create"),
        {"room_id": room_id, "date_start": "2023-01-01", "date_end": "2023-01-05"},
    )
    api_client.post(
        reverse("booking-create"),
        {"room_id": room_id, "date_start": "2023-01-10", "date_end": "2023-01-15"},
    )
    api_client.post(
        reverse("booking-create"),
        {"room_id": room_id, "date_start": "2023-01-20", "date_end": "2023-01-25"},
    )

    response = api_client.get(
        reverse("booking-list") + f"?room_id={room_id}&ordering=-date_start"
    )
    assert response.status_code == 200

    assert response.data[0]["date_start"] == "2023-01-01"
    assert response.data[1]["date_start"] == "2023-01-10"
    assert response.data[2]["date_start"] == "2023-01-20"
