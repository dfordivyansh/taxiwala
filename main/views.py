from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import EnquiryForm, RideSearchForm, LocalRentalForm, OneWayForm, RoundTripForm,  DestinationFormSet, RoadTripBookingForm, LocalTransferForm, BookingRequestForm

from .utils import handle_ride_search
from django.urls import reverse
import urllib.parse
from sentence_transformers import SentenceTransformer

from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
import json
from .models import ChatQA, Destination, RoundTrip, CityPage, RideSearch, Taxi ,BookingDetail, BookingRequest


def main_view(request):
    # recent_ratings = BookingDetail.objects.exclude(rating__isnull=True).order_by('-id')[:5]
    city_pages = CityPage.objects.filter(show_on_pages__contains='home')
    form = RideSearchForm()
    return render(request, 'base/ride_base.html', {'city_pages': city_pages, 'form': form})


def ride_search_view(request):
    if request.method == 'POST':
        source_city = request.POST.get('source_city')
        ride_type = request.POST.get('ride_type')
        pickup_datetime = request.POST.get('pickup_datetime')

        # Save the search (optional)
        RideSearch.objects.create(
            source_city=source_city,
            ride_type=ride_type,
            pickup_datetime=pickup_datetime
        )

        # Redirect to the taxi list page with source_city as query param
        url = reverse('taxi-list')  # Replace with your taxi list URL name
        return redirect(f"{url}?source_city={source_city}")

    # Fallback
    return redirect('taxi-list')

def city_autocomplete(request):
    q = request.GET.get('q', '')
    matches = RideSearch.objects.filter(source_city__icontains=q).values_list('source_city', flat=True).distinct()
    return JsonResponse(list(matches), safe=False)



def local_rental_view(request):
    city_pages = CityPage.objects.filter(show_on_pages__contains='local_rental')
    if request.method == 'POST':
        form = LocalRentalForm(request.POST)
        if form.is_valid():
            print("✅ Local Rental form is valid")
            form.save()
            messages.success(
                request, "Thank you for your enquiry in a Local Rental! Our team will contact you soon.")
            return render(request, 'views/local_rental.html')
        else:
            print("❌ Local Rental form is invalid")
            print(form.errors)
    else:
        form = LocalRentalForm()

    return render(request, 'views/local_rental.html', {'form': form, 'city_pages': city_pages})


def one_way_view(request):
    city_pages = CityPage.objects.filter(show_on_pages__contains='one_way')
    if request.method == 'POST':
        form = OneWayForm(request.POST)
        if form.is_valid():
            print("✅ One Way Enquiry form is valid")
            form.save()
            messages.success(
                request, "Thank you for your enquiry! We will contact you shortly regarding your one way trip.")
            return render(request, 'views/one_way.html')
        else:
            print("❌ One Way Enquiry form is invalid")
            print(form.errors)
    else:
        form = OneWayForm()

    return render(request, 'views/one_way.html', {'form': form, 'city_pages': city_pages})


def round_trip_view(request):
    city_pages = CityPage.objects.filter(show_on_pages__contains='round_trip')

    if request.method == 'POST':
        form = RoundTripForm(request.POST)
        destinations = request.POST.getlist('destination[]')

        if form.is_valid() and destinations:
            try:
                round_trip = form.save()  # ✅ this creates the RoundTrip instance

                # Create each Destination object and link it
                for city in destinations:
                    if city.strip():
                        Destination.objects.create(
                            round_trip=round_trip,  # ✅ use the model, not the form class
                            destination_city=city.strip()
                        )

                # ✅ Generate and save the simulated SMS
                round_trip.simulated_sms_message()

                messages.success(request, "Thank you for your round trip enquiry!")
            except Exception as e:
                messages.error(request, f"Error saving data: {e}")
        else:
            messages.error(request, "Please fill all required fields.")

        return render(request, 'views/round_trip.html', {'city_pages': city_pages})

    return render(request, 'views/round_trip.html', {'city_pages': city_pages})

def road_trip_view(request):
    city_pages = CityPage.objects.filter(show_on_pages__contains='road_trip')
    if request.method == 'POST':
        form = RoadTripBookingForm(request.POST)
        if form.is_valid():
            print("✅ Road Trip Enquiry form is valid")
            form.save()
            messages.success(
                request, "Thank you for your enquiry! We will contact you shortly regarding your road trip.")
            return render(request, 'views/road_trip.html')
        else:
            print("❌ Road Trip Enquiry form is invalid")
            print(form.errors)
    else:
        form = RoadTripBookingForm()

    return render(request, 'views/road_trip.html', {'form': form, 'city_pages': city_pages})


def local_transfer_view(request):
    city_pages = CityPage.objects.filter(show_on_pages__contains='local_transfer')
    if request.method == 'POST':
        form = LocalTransferForm(request.POST)
        if form.is_valid():
            print("✅ Local Transfer form is valid")
            form.save()
            messages.success(request, "Thank you! We will contact you shortly regarding your local transfer.")
            return render(request, 'views/local_transfer.html')  # Your success page or same page
        else:
            print("❌ Local Transfer form is invalid")
            print(form.errors)
    else:
        form = LocalTransferForm()

    return render(request, 'views/local_transfer.html', {'form': form, 'city_pages': city_pages})



def enquiry_view(request):
    if request.method == 'POST':
        form = EnquiryForm(request.POST)
        if form.is_valid():
            print("✅ Enquiry form is valid")
            form.save()
            messages.success(request, "Thank you for your enquiry!")
            return render(request, 'base/ride_base.html')  # redirect optional
        else:
            print("❌ Enquiry form is invalid")
            print(form.errors)
    else:
        form = EnquiryForm()
    return render(request, 'views/enquiry.html', {'form': form})


# Load model once (at module level)
model = SentenceTransformer('all-MiniLM-L6-v2')


@csrf_exempt
def chatbot_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip().lower()

            # Try matching question
            qa = ChatQA.objects.filter(question__icontains=message).first()

            if qa:
                return JsonResponse({'reply': qa.answer})
            else:
                return JsonResponse({
                    'reply': "Sorry, I couldn't find an answer for that.",
                    'whatsapp_button': True,
                    'whatsapp_link': 'https://wa.me/916394005588'
                })

        except Exception as e:
            return JsonResponse({'reply': f"Error: {str(e)}"})

    return JsonResponse({'reply': 'Invalid request method.'})



from collections import defaultdict

def city_detail(request, slug):
    city = get_object_or_404(CityPage, slug=slug)
    fares = city.taxi_fares.all()

    # Organize fares by category
    taxi_fares_by_category = defaultdict(list)
    for fare in fares:
        taxi_fares_by_category[fare.category].append(fare)

    # Map internal category keys to readable titles
    category_labels = {
        'local': '8Hrs/80Kms',
        'outstation': 'Outstation',
        'oneway': 'Outstation Oneway',
    }

    context = {
        'city': city,
        'fares_by_category': taxi_fares_by_category,
        'category_labels': category_labels,
    }

    return render(request, 'views/city_detail.html', context)


def all_cities(request):
    cities = CityPage.objects.all().order_by('name')
    return render(request, 'views/all_cities.html', {'cities': cities})



def taxi_list(request):
    taxis = Taxi.objects.all()
    cities = CityPage.objects.all()
    city_pages = CityPage.objects.all()

    city_data = {}
    for city in city_pages:
        if city.thumbnail_image:
            city_data[city.name.lower()] = city.thumbnail_image.url

    source_city = ''
    
    if request.method == 'POST':
        source_city = request.POST.get('source_city')
        # You can use this to filter taxis if needed
        taxis = Taxi.objects.filter(source_city__icontains=source_city)
    else:
        taxis = Taxi.objects.all()

    return render(request, 'views/taxi_list.html', {
        'taxis': taxis,
        'source_city': source_city,
        'cities': cities,
        'city_pages': city_pages,
        'city_data_json': json.dumps(city_data)
    })


def booking_detail_view(request, booking_id):
    booking = get_object_or_404(BookingDetail, id=booking_id)

    if request.method == 'POST':
        form = BookingRequestForm(request.POST)
        if form.is_valid():
            booking_request = form.save(commit=False)
            booking_request.booking = booking
            booking_request.save()


            # ✅ Redirect to confirmation view (will send SMS)
            return redirect('booking_confirmation', booking_id=booking_request.id)
    else:
        form = BookingRequestForm()

    return render(request, 'views/booking_detail.html', {'booking': booking, 'form': form})



def send_booking_sms(mobile, booking_id, link):

    print(f"[SIMULATED SMS] To: {mobile} | Booking ID: {booking_id} | Link: {link}")

import urllib.parse

def booking_confirmation(request, booking_id):
    booking_request = get_object_or_404(BookingRequest, id=booking_id)

    booking_url = request.build_absolute_uri(
        reverse('booking_confirmation', args=[booking_request.id])
    )

    send_booking_sms(
        mobile=booking_request.mobile,
        booking_id=booking_request.booking.booking_id,
        link=booking_url
    )

    # ✅ Use quote_plus instead of quote
    short_id = f"TW{str(booking_request.booking.booking_id)[-6:]}"
    message = (
        f"Hi TaxiWala!\n\n"
        f"I just booked a cab through your website.\n\n"
        f"Here are my booking details:\n"
        f"Booking ID: {short_id}\n"
        f"Mobile: {booking_request.mobile}\n"
        f" Name: {booking_request.full_name}\n\n"
        f"Please confirm the ride at your earliest convenience.\n"
        f"Looking forward to a great journey!\n\n"
        f"Thanks,\n"
        f"{booking_request.full_name}"
    )
    encoded_message = urllib.parse.quote_plus(message)

    whatsapp_url = f"https://wa.me/916394005588?text={encoded_message}"

    return render(request, 'views/confirmation.html', {
        'booking_request': booking_request,
        'booking_id': booking_request.booking.booking_id,
        'whatsapp_url': whatsapp_url
    })

def submit_rating(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(BookingDetail, id=booking_id)
        rating = request.POST.get("rating")
        if rating and rating.isdigit() and 1 <= int(rating) <= 5:
            booking.rating = int(rating)
            booking.save()

            # ✅ Update Taxi rating
            taxi = booking.taxi
            taxi.total_rating += booking.rating
            taxi.num_ratings += 1
            taxi.save()

            messages.success(request, "⭐ Thanks for rating us! Please come again to get the service by TaxiWala.")
        return redirect('main') 
    

# Static Views

def about_us(request):
    return render(request, 'static_pages/about.html')

def privacy_policy(request):
    return render(request, 'static_pages/privacy_policy.html')

def terms_and_conditions(request):
    return render(request, 'static_pages/terms_and_conditions.html')

def careers(request):
    return render(request, 'static_pages/careers.html')