from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from django.utils.html import format_html
from multiselectfield import MultiSelectField
from decimal import Decimal
import uuid
import urllib.parse


class Enquiry(models.Model):
    VEHICLE_CHOICES = [
        ('Sedan', 'Sedan'),
        ('SUV', 'SUV'),
        ('Mini', 'Mini'),
        ('Luxury', 'Luxury'),
    ]

    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    pickup_city = models.CharField(max_length=100)
    vehicle = models.CharField(max_length=20, choices=VEHICLE_CHOICES)
    travellers = models.PositiveIntegerField()
    pickup_date = models.DateField()
    drop_date = models.DateField()
    trip_details = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    # New fields
    enquiry_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    enquiry_sms = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.mobile}"

    def generate_enquiry_sms(self):
        link = f"http://taxiwala.co/enquiry/{self.id}"
        short_id = f"TWE{str(self.enquiry_id)[-6:]}"
        message = f"""🚖 Hello {self.name}! We’ve received your trip enquiry 🎉

📞 Mobile: {self.mobile}
🆔 Enquiry ID: {short_id}
🗓️ Pickup: {self.pickup_date.strftime('%d-%b-%Y')} | Drop: {self.drop_date.strftime('%d-%b-%Y')}
🚘 Vehicle: {self.vehicle} | 🧍 Travellers: {self.travellers}
📍 Pickup City: {self.pickup_city}
🔗 View your enquiry details:
👉 {link}

Thank you for contacting TaxiWala! 🚕✨
We’ll reach out to you shortly!
"""
        return message

    def simulated_sms_message(self):
        message = self.generate_enquiry_sms()
        self.enquiry_sms = message  # Save to field
        self.save(update_fields=['enquiry_sms'])

        return format_html(
            '''
            <pre id="sms_{0}" style="white-space: pre-wrap; background: #f4f4f4; padding: 10px; border-radius: 5px; border: 1px solid #ccc;">{1}</pre>
            
            <button onclick="navigator.clipboard.writeText(document.getElementById('sms_{0}').innerText)"
                    style="margin-top: 6px; margin-right: 10px; padding: 6px 12px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">
                📋 Copy SMS
            </button>

            <a href="https://wa.me/91{2}?text={3}" target="_blank"
            style="padding: 7px 14px; background-color: #25D366; color: white; border-radius: 4px; text-decoration: none; font-weight: bold;">
                💬 Send on WhatsApp
            </a>
            ''',
            self.id,
            message,
            self.mobile,
            urllib.parse.quote(message)
        )

    simulated_sms_message.short_description = "Simulated Enquiry SMS"


class ChatQA(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)  # added for consistency

    def __str__(self):
        return self.question


class RideSearch(models.Model):
    RIDE_TYPE_CHOICES = [
        ("Local Rental", "Local Rental"),
        ("One Way", "One Way"),
        ("Round Trip", "Round Trip"),
        ("Road Trip", "Road Trip"),
        ("Local Transfer", "Local Transfer"),
    ]

    source_city = models.CharField(max_length=100)
    ride_type = models.CharField(max_length=20, choices=RIDE_TYPE_CHOICES)
    pickup_datetime = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source_city} - {self.ride_type} @ {self.pickup_datetime}"



PACKAGE_CHOICES = [
    ('Mini Ride - 4h/40km', 'Mini Ride - 4h/40km'),
    ('Half Day - 8h/80km', 'Half Day - 8h/80km'),
    ('Full Day - 12h/120km', 'Full Day - 12h/120km'),
    ('Custom', 'Custom'),
]

class LocalRental(models.Model):
    city = models.CharField(max_length=100)
    package = models.CharField(max_length=50, choices=PACKAGE_CHOICES)
    pickup_datetime = models.DateTimeField()
    contact_number = models.CharField(max_length=15)

    enquiry_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    enquiry_sms = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.city} - {self.package}"

    def generate_enquiry_sms(self):
        link = f"http://taxiwala.co/local-rental/{self.id}"
        short_id = f"TWE{str(self.enquiry_id)[-6:]}"
        message = f"""🚖 Hello! We’ve received your Local Rental request 🎉

📞 Mobile: {self.contact_number}
🆔 Enquiry ID: {short_id}
📍 City: {self.city}
🧾 Package: {self.package}
🗓️ Pickup Date & Time: {self.pickup_datetime.strftime('%d-%b-%Y %I:%M %p')}
🔗 View enquiry:
👉 {link}

Thank you for choosing TaxiWala! 🚕✨
"""
        return message

    def simulated_sms_message(self):
        message = self.generate_enquiry_sms()
        self.enquiry_sms = message
        self.save(update_fields=['enquiry_sms'])
        return format_html(
            '''
            <pre id="sms_{0}" style="white-space: pre-wrap; background: #f4f4f4; padding: 10px; border-radius: 5px; border: 1px solid #ccc;">{1}</pre>
            <button onclick="navigator.clipboard.writeText(document.getElementById('sms_{0}').innerText)"
                style="margin-top: 6px; margin-right: 10px; padding: 6px 12px; background-color: #007bff; color: white; border: none; border-radius: 4px;">📋 Copy SMS</button>
            <a href="https://wa.me/91{2}?text={3}" target="_blank"
                style="padding: 7px 14px; background-color: #25D366; color: white; border-radius: 4px; text-decoration: none;">💬 Send on WhatsApp</a>
            ''',
            self.id,
            message,
            self.contact_number,
            urllib.parse.quote(message)
        )

    simulated_sms_message.short_description = "Simulated SMS"




class OneWay(models.Model):
    source_city = models.CharField(max_length=100)
    destination_city = models.CharField(max_length=100)
    pickup_datetime = models.DateTimeField()
    contact_number = models.CharField(max_length=15)

    enquiry_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    enquiry_sms = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.source_city} to {self.destination_city} at {self.pickup_datetime.strftime('%Y-%m-%d %H:%M')}"

    def generate_enquiry_sms(self):
        link = f"http://taxiwala.co/oneway/{self.id}"
        short_id = f"TWE{str(self.enquiry_id)[-6:]}"
        message = f"""🚖 Hello! Your One-Way Trip enquiry has been received 🎉

📞 Mobile: {self.contact_number}
🆔 Enquiry ID: {short_id}
📍 From: {self.source_city}
📍 To: {self.destination_city}
🗓️ Pickup Date & Time: {self.pickup_datetime.strftime('%d-%b-%Y %I:%M %p')}
🔗 View enquiry:
👉 {link}

Thank you for choosing TaxiWala! 🚕✨
"""
        return message

    def simulated_sms_message(self):
        message = self.generate_enquiry_sms()
        self.enquiry_sms = message
        self.save(update_fields=['enquiry_sms'])
        return format_html(
            '''
            <pre id="sms_{0}" style="white-space: pre-wrap; background: #f4f4f4; padding: 10px; border-radius: 5px; border: 1px solid #ccc;">{1}</pre>
            <button onclick="navigator.clipboard.writeText(document.getElementById('sms_{0}').innerText)"
                style="margin-top: 6px; margin-right: 10px; padding: 6px 12px; background-color: #007bff; color: white; border: none; border-radius: 4px;">📋 Copy SMS</button>
            <a href="https://wa.me/91{2}?text={3}" target="_blank"
                style="padding: 7px 14px; background-color: #25D366; color: white; border-radius: 4px; text-decoration: none;">💬 Send on WhatsApp</a>
            ''',
            self.id,
            message,
            self.contact_number,
            urllib.parse.quote(message)
        )

    simulated_sms_message.short_description = "Simulated SMS"




class RoundTrip(models.Model):
    source_city = models.CharField(max_length=100)
    pickup_datetime = models.DateTimeField()
    return_datetime = models.DateTimeField()
    contact_number = models.CharField(max_length=15)

    enquiry_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    enquiry_sms = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.source_city} Round Trip on {self.pickup_datetime.strftime('%Y-%m-%d %H:%M')}"

    def generate_enquiry_sms(self):
        link = f"http://taxiwala.co/roundtrip/{self.id}"
        short_id = f"TWE{str(self.enquiry_id)[-6:]}"
        message = f"""🚖 Hello! Your Round Trip enquiry is confirmed 🎉

📞 Mobile: {self.contact_number}
🆔 Enquiry ID: {short_id}
📍 Source: {self.source_city}
🗓️ Pickup: {self.pickup_datetime.strftime('%d-%b-%Y %I:%M %p')}
🔁 Return: {self.return_datetime.strftime('%d-%b-%Y %I:%M %p')}
🔗 View enquiry:
👉 {link}

Thank you for choosing TaxiWala! 🚕✨
"""
        return message

    def simulated_sms_message(self):
        message = self.generate_enquiry_sms()
        self.enquiry_sms = message
        self.save(update_fields=['enquiry_sms'])
        return format_html(
            '''
            <pre id="sms_{0}" style="white-space: pre-wrap; background: #f4f4f4; padding: 10px; border-radius: 5px; border: 1px solid #ccc;">{1}</pre>
            <button onclick="navigator.clipboard.writeText(document.getElementById('sms_{0}').innerText)"
                style="margin-top: 6px; margin-right: 10px; padding: 6px 12px; background-color: #007bff; color: white; border: none; border-radius: 4px;">📋 Copy SMS</button>
            <a href="https://wa.me/91{2}?text={3}" target="_blank"
                style="padding: 7px 14px; background-color: #25D366; color: white; border-radius: 4px; text-decoration: none;">💬 Send on WhatsApp</a>
            ''',
            self.id,
            message,
            self.contact_number,
            urllib.parse.quote(message)
        )

    simulated_sms_message.short_description = "Simulated SMS"


class Destination(models.Model):
    round_trip = models.ForeignKey(RoundTrip, related_name='destinations', on_delete=models.CASCADE)
    destination_city = models.CharField(max_length=100)

    def __str__(self):
        return self.destination_city


class RoadTripBooking(models.Model):
    start_city = models.CharField(max_length=100)
    destination = models.CharField(max_length=200)
    start_datetime = models.DateTimeField()
    contact_number = models.CharField(max_length=15)

    enquiry_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    enquiry_sms = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.start_city} ➜ {self.destination} at {self.start_datetime.strftime('%Y-%m-%d %H:%M')}"

    def generate_enquiry_sms(self):
        link = f"http://taxiwala.co/roadtrip/{self.id}"
        short_id = f"TWE{str(self.enquiry_id)[-6:]}"
        message = f"""🚖 Hello! Your Road Trip enquiry has been received 🎉

📞 Mobile: {self.contact_number}
🆔 Enquiry ID: {short_id}
📍 From: {self.start_city}
📍 To: {self.destination}
🗓️ Start Date & Time: {self.start_datetime.strftime('%d-%b-%Y %I:%M %p')}
🔗 View enquiry:
👉 {link}

Thanks for trusting TaxiWala! 🚕✨
"""
        return message

    def simulated_sms_message(self):
        message = self.generate_enquiry_sms()
        self.enquiry_sms = message
        self.save(update_fields=['enquiry_sms'])
        return format_html(
            '''
            <pre id="sms_{0}" style="white-space: pre-wrap; background: #f4f4f4; padding: 10px; border-radius: 5px; border: 1px solid #ccc;">{1}</pre>
            <button onclick="navigator.clipboard.writeText(document.getElementById('sms_{0}').innerText)"
                style="margin-top: 6px; margin-right: 10px; padding: 6px 12px; background-color: #007bff; color: white; border: none; border-radius: 4px;">📋 Copy SMS</button>
            <a href="https://wa.me/91{2}?text={3}" target="_blank"
                style="padding: 7px 14px; background-color: #25D366; color: white; border-radius: 4px; text-decoration: none;">💬 Send on WhatsApp</a>
            ''',
            self.id,
            message,
            self.contact_number,
            urllib.parse.quote(message)
        )

    simulated_sms_message.short_description = "Simulated SMS"



class LocalTransfer(models.Model):
    source_city = models.CharField(max_length=100)
    drop_location = models.CharField(max_length=100)
    pickup_time = models.DateTimeField()
    contact_number = models.CharField(max_length=15)

    enquiry_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    enquiry_sms = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.source_city} to {self.drop_location} at {self.pickup_time.strftime('%Y-%m-%d %H:%M')}"

    def generate_enquiry_sms(self):
        link = f"http://taxiwala.co/local-transfer/{self.id}"
        short_id = f"TWE{str(self.enquiry_id)[-6:]}"
        message = f"""🚖 Hello! Your Local Transfer enquiry has been received 🎉

📞 Mobile: {self.contact_number}
🆔 Enquiry ID: {short_id}
📍 From: {self.source_city}
📍 To: {self.drop_location}
🗓️ Pickup Time: {self.pickup_time.strftime('%d-%b-%Y %I:%M %p')}
🔗 View enquiry:
👉 {link}

Thank you for contacting TaxiWala! 🚕✨
"""
        return message

    def simulated_sms_message(self):
        message = self.generate_enquiry_sms()
        self.enquiry_sms = message
        self.save(update_fields=['enquiry_sms'])
        return format_html(
            '''
            <pre id="sms_{0}" style="white-space: pre-wrap; background: #f4f4f4; padding: 10px; border-radius: 5px; border: 1px solid #ccc;">{1}</pre>
            <button onclick="navigator.clipboard.writeText(document.getElementById('sms_{0}').innerText)"
                style="margin-top: 6px; margin-right: 10px; padding: 6px 12px; background-color: #007bff; color: white; border: none; border-radius: 4px;">📋 Copy SMS</button>
            <a href="https://wa.me/91{2}?text={3}" target="_blank"
                style="padding: 7px 14px; background-color: #25D366; color: white; border-radius: 4px; text-decoration: none;">💬 Send on WhatsApp</a>
            ''',
            self.id,
            message,
            self.contact_number,
            urllib.parse.quote(message)
        )

    simulated_sms_message.short_description = "Simulated SMS"




PAGE_CHOICES = (
    ('home', 'Home Page'),
    ('local_rental', 'Local Rental'),
    ('one_way', 'One Way'),
    ('round_trip', 'Round Trip'),
    ('road_trip', 'Road Trip'),
    ('local_transfer', 'Local Transfer'),
)

class CityPage(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    thumbnail_image = models.ImageField(upload_to='city_thumbnails/')
    description = models.TextField(blank=True, null=True)
    show_on_pages = MultiSelectField(choices=PAGE_CHOICES, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "City Page"
        verbose_name_plural = "City Pages"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


FARE_CATEGORIES = (
    ('local', '8Hrs/80Kms'),
    ('outstation', 'Outstation'),
    ('oneway', 'Outstation Oneway'),
)

class TaxiFare(models.Model):
    city = models.ForeignKey('CityPage', related_name='taxi_fares', on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=FARE_CATEGORIES)
    car_name = models.CharField(max_length=100)
    fare_amount = models.CharField(max_length=50)  # Use CharField for flexibility like "Rs. 9.5/Km"

    class Meta:
        verbose_name = "Taxi Fare"
        verbose_name_plural = "Taxi Fares"
        ordering = ['category', 'car_name']

    def __str__(self):
        return f"{self.city.name} - {self.car_name} ({self.get_category_display()})"
    
    


# taxi/models.py

class Taxi(models.Model):
    CAR_TYPE_CHOICES = [
        ('SEDAN', 'Sedan'),
        ('SEDAN_ETIOS', 'Sedan Etios'),
        ('MARUTI SUZUKI', 'Maruti Suzuki'),
        ('SWIFT', 'Swift'),
        ('XUV', 'XUV'),
        ('INNOVA', 'Innova'),
        ('INNOVA_CRYSTA', 'Innova Crysta'),
        ('ERTIGA', 'Ertiga'),
        ('HYCROSS', 'Hycross'),
        ('TEMPO_16', 'Tempo Traveler 16 Seater'),
        ('TEMPO_18', 'Tempo Traveler 18 Seater'),
    ]
    PACKAGE_CHOICES = [
    ('Mini Ride - 4h/40km', 'Mini Ride - 4h/40km'),
    ('Half Day - 8h/80km', 'Half Day - 8h/80km'),
    ('Full Day - 12h/120km', 'Full Day - 12h/120km'),
    ('Custom', 'Custom'),
    ]
    name = models.CharField(max_length=100)
    car_type = models.CharField(max_length=20, choices=CAR_TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    package_info = models.CharField(max_length=20, choices=PACKAGE_CHOICES)
    charge_info = models.CharField(max_length=100)
    image = models.ImageField(upload_to='taxi_images/')
    included_gst = models.BooleanField(default=True)

    # New fields
    source_city = models.CharField(max_length=100, help_text="Enter the name of the source city")
    destination_cities = models.TextField(help_text="Enter multiple destination cities, separated by commas")
    total_rating = models.PositiveIntegerField(default=0)
    num_ratings = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    def get_destination_cities_list(self):
        """Returns the list of destination cities"""
        return [city.strip() for city in self.destination_cities.split(',') if city.strip()]
    
    def average_rating(self):
        if self.num_ratings == 0:
            return 0
        return round(self.total_rating / self.num_ratings, 1) 
    
    
class BookingDetail(models.Model):
    PACKAGE_CHOICES = [
    ('Mini Ride - 4h/40km', 'Mini Ride - 4h/40km'),
    ('Half Day - 8h/80km', 'Half Day - 8h/80km'),
    ('Full Day - 12h/120km', 'Full Day - 12h/120km'),
    ('Custom', 'Custom'),
    ]
    # Passenger Info
    full_name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)

    taxi = models.ForeignKey(Taxi, on_delete=models.CASCADE, null=True, blank=True)
    taxi_name = models.CharField(max_length=100)
    trip_location = models.CharField(max_length=255)
    package_name = models.CharField(max_length=20, choices=PACKAGE_CHOICES)
    pickup_datetime = models.DateTimeField(default=timezone.now)
    base_fare = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    gst = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)
    total_fare = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)

    extra_km_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('12.00'))
    extra_hour_rate = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('120.00'))
    
    PAYMENT_CHOICES = [
        ('UPI', 'UPI Transfer'),
        ('QR', 'Scan QR Code'),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='UPI')
    
    # System Info
    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.taxi_name} ({self.trip_location}) - ₹{self.total_fare}"

    def calculate_gst(self):
        return self.base_fare * Decimal('0.05')

    def calculate_total_fare(self):
        return self.base_fare + self.gst

    def save(self, *args, **kwargs):
        # Calculate GST as 5% of base fare
        self.gst = self.calculate_gst()
        # Calculate total fare
        self.total_fare = self.calculate_total_fare()
        super().save(*args, **kwargs)

def send_booking_sms(mobile, booking_id, link):
    message = f"""🚖 Hello! Your booking with TaxiWala is confirmed 🎉

📞 Mobile: {mobile}
🆔 Booking ID: TW{str(booking_id)[-6:]}
🔗 Track or manage your booking:
👉 {link}

Thank you for choosing TaxiWala! 🚕✨
Safe travels!
"""
    print(f"{message}")
    return message

class BookingRequest(models.Model):
    PAYMENT_CHOICES = [
        ('upi', 'UPI Transfer'),
        ('qr', 'Scan QR Code'),
    ]

    booking = models.ForeignKey('BookingDetail', on_delete=models.CASCADE, related_name="requests")
    full_name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    pickup_location = models.CharField(max_length=255)
    pickup_datetime = models.DateTimeField(default=timezone.now)

    # OPTIONAL payment method
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_CHOICES, blank=True, null=True
    )

    # Payment screenshot upload
    payment_screenshot = models.ImageField(upload_to='payment_screenshots/', blank=True, null=True)

    pay_later = models.BooleanField(default=False)
    accepted_terms = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.mobile}"
    
    def simulated_sms_message(self):
        if not self.booking:
            return "(No linked booking)"

        # Construct the link using Django reverse
        link = f"http://taxiwala.co{reverse('booking_confirmation', args=[self.id])}"

        # Call your SMS function and capture the returned string
        message = send_booking_sms(self.mobile, self.booking.booking_id, link)

        return format_html(
            '''
            <pre id="sms_{0}" style="white-space: pre-wrap; background: #f4f4f4; padding: 10px; border-radius: 5px; border: 1px solid #ccc;">{1}</pre>
            
            <button onclick="navigator.clipboard.writeText(document.getElementById('sms_{0}').innerText)"
                    style="margin-top: 6px; margin-right: 10px; padding: 6px 12px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">
                📋 Copy SMS
            </button>

            <a href="https://wa.me/91{2}?text={3}" target="_blank"
            style="padding: 7px 14px; background-color: #25D366; color: white; border-radius: 4px; text-decoration: none; font-weight: bold;">
                💬 Send on WhatsApp
            </a>
            ''',
            self.id,
            message,
            self.mobile,
            urllib.parse.quote(message)
        )

    simulated_sms_message.short_description = "Simulated SMS"


class Vendor(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    vehicle_type = models.CharField(max_length=50)
    vehicle_number = models.CharField(max_length=20)
    city = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.vehicle_number})"


class VendorAllotment(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='allotments')
    customer_name = models.CharField(max_length=100)
    customer_mobile = models.CharField(max_length=15)
    pickup_location = models.CharField(max_length=255)
    drop_location = models.CharField(max_length=255, blank=True)
    trip_date = models.DateField(default=timezone.now)
    vehicle_type = models.CharField(max_length=50)
    booking_reference = models.CharField(max_length=50, blank=True, help_text="Internal or external booking reference")
    remarks = models.TextField(blank=True)
    allotted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vendor.name} → {self.customer_name} on {self.trip_date}"