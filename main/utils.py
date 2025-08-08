from .models import RideSearch

def handle_ride_search(request):
    if request.method == 'POST' and 'source_city' in request.POST:
        source_city = request.POST.get('source_city')
        ride_type = request.POST.get('ride_type')
        pickup_datetime = request.POST.get('pickup_datetime')

        search = RideSearch.objects.create(
            source_city=source_city,
            ride_type=ride_type,
            pickup_datetime=pickup_datetime
        )
        return search
    return None


def send_booking_sms(mobile, booking_id, link):

    print(f"[SIMULATED SMS] To: {mobile} | Booking ID: {booking_id} | Link: {link}")

import urllib.parse