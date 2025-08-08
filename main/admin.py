from django.contrib import admin
from .models import Enquiry, ChatQA, RideSearch, LocalRental, OneWay, RoundTrip, Destination, RoadTripBooking, LocalTransfer, CityPage, TaxiFare, CityPage, Taxi , BookingDetail ,BookingRequest, PAGE_CHOICES, Vendor, VendorAllotment
from django.utils.html import format_html

from django.contrib.admin import SimpleListFilter


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "mobile", "pickup_city", "pickup_date", "simulated_sms_message")
    readonly_fields = ("simulated_sms_message", "enquiry_sms")

admin.site.register(ChatQA)

@admin.register(RideSearch)
class RideSearchAdmin(admin.ModelAdmin):
    list_display = ('source_city', 'ride_type', 'pickup_datetime', 'created_at')

@admin.register(LocalRental)
class LocalRentalAdmin(admin.ModelAdmin):
    readonly_fields = ('simulated_sms_message',)
    list_display = ('city', 'package', 'pickup_datetime', 'contact_number', 'simulated_sms_message')

@admin.register(OneWay)
class OneWayAdmin(admin.ModelAdmin):
    readonly_fields = ('simulated_sms_message',)
    list_display = ('source_city', 'destination_city', 'pickup_datetime', 'contact_number', 'simulated_sms_message')

class DestinationInline(admin.TabularInline):
    model = Destination
    extra = 1

class RoundTripAdmin(admin.ModelAdmin):
    inlines = [DestinationInline]
    readonly_fields = ('simulated_sms_message',)
    list_display = ('source_city', 'pickup_datetime', 'return_datetime', 'contact_number', 'simulated_sms_message')

admin.site.register(RoundTrip, RoundTripAdmin)


@admin.register(RoadTripBooking)
class RoadTripBookingAdmin(admin.ModelAdmin):
    readonly_fields = ('simulated_sms_message',)
    list_display = ('start_city', 'destination', 'start_datetime', 'contact_number', 'simulated_sms_message')


@admin.register(LocalTransfer)
class LocalTransferAdmin(admin.ModelAdmin):
    readonly_fields = ('simulated_sms_message',)
    list_display = ('source_city', 'drop_location', 'pickup_time', 'contact_number', 'simulated_sms_message')

class ShowOnPagesFilter(SimpleListFilter):
    title = 'Show on Pages'
    parameter_name = 'show_on_pages'

    def lookups(self, request, model_admin):
        return PAGE_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(show_on_pages__icontains=self.value())
        return queryset



class TaxiFareInline(admin.TabularInline):
    model = TaxiFare
    extra = 1


@admin.register(CityPage)
class CityPageAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'last_updated',
        'is_home_page',
        'is_local_rental',
        'is_one_way',
        'is_round_trip',
        'is_road_trip',
        'is_local_transfer'
    )
    prepopulated_fields = {'slug': ('name',)}
    inlines = [TaxiFareInline]
    list_filter = (ShowOnPagesFilter,)
    search_fields = ('name',)

    def is_home_page(self, obj):
        return 'home' in obj.show_on_pages
    is_home_page.boolean = True
    is_home_page.short_description = "Home Page"

    def is_local_rental(self, obj):
        return 'local_rental' in obj.show_on_pages
    is_local_rental.boolean = True
    is_local_rental.short_description = "Local Rental"

    def is_one_way(self, obj):
        return 'one_way' in obj.show_on_pages
    is_one_way.boolean = True
    is_one_way.short_description = "One Way"

    def is_round_trip(self, obj):
        return 'round_trip' in obj.show_on_pages
    is_round_trip.boolean = True
    is_round_trip.short_description = "Round Trip"

    def is_road_trip(self, obj):
        return 'road_trip' in obj.show_on_pages
    is_road_trip.boolean = True
    is_road_trip.short_description = "Road Trip"

    def is_local_transfer(self, obj):
        return 'local_transfer' in obj.show_on_pages
    is_local_transfer.boolean = True
    is_local_transfer.short_description = "Local Transfer"


@admin.register(TaxiFare)
class TaxiFareAdmin(admin.ModelAdmin):
    list_display = ['city', 'category', 'car_name', 'fare_amount']
    list_filter = ['city', 'category']





admin.site.register(Taxi)
admin.site.register(BookingDetail)
@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'mobile', 'email', 'submitted_at')
    readonly_fields = ('simulated_sms_message',)
    fields = (
        'full_name', 'mobile', 'email',
        'pickup_location', 'pickup_datetime',
        'payment_method', 'payment_screenshot', 'pay_later', 'accepted_terms',
        'booking', 'simulated_sms_message',
    )


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile', 'vehicle_type', 'vehicle_number', 'city')
    search_fields = ('name', 'mobile', 'vehicle_number', 'city')


@admin.register(VendorAllotment)
class VendorAllotmentAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'customer_name', 'customer_mobile', 'pickup_location', 'trip_date', 'vehicle_type')
    list_filter = ('trip_date', 'vehicle_type', 'vendor')
    search_fields = ('customer_name', 'customer_mobile', 'pickup_location', 'drop_location', 'booking_reference')
    readonly_fields = ('allotted_at',)