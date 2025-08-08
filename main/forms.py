from django import forms
from .models import Enquiry, RideSearch, LocalRental, OneWay, RoundTrip, Destination, RoadTripBooking, LocalTransfer, BookingRequest


from django.forms import modelformset_factory

class EnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        exclude = ['created_at']  # Exclude auto field

        widgets = {
            'pickup_date': forms.DateInput(attrs={'type': 'date'}),
            'drop_date': forms.DateInput(attrs={'type': 'date'}),
            'trip_details': forms.Textarea(attrs={'rows': 4}),
        }


class RideSearchForm(forms.ModelForm):
    class Meta:
        model = RideSearch
        fields = ['source_city', 'ride_type', 'pickup_datetime']
        widgets = {
            'source_city': forms.TextInput(attrs={
                'id': 'source_city',
                'class': 'form-control',
                'placeholder': 'Enter Source City',
                'autocomplete': 'off'
            }),
            'ride_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'pickup_datetime': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
        }


class LocalRentalForm(forms.ModelForm):
    class Meta:
        model = LocalRental
        fields = ['city', 'package', 'pickup_datetime', 'contact_number']
        widgets = {
            'pickup_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your city name'}),
            'package': forms.Select(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Contact Number'}),
        }


class OneWayForm(forms.ModelForm):
    class Meta:
        model = OneWay
        fields = ['source_city', 'destination_city', 'pickup_datetime', 'contact_number']
        widgets = {
            'pickup_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'source_city': forms.TextInput(attrs={'placeholder': 'Enter Source City', 'class': 'form-control'}),
            'destination_city': forms.TextInput(attrs={'placeholder': 'Enter Destination City', 'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Contact Number'}),
        }


class RoundTripForm(forms.ModelForm):
    class Meta:
        model = RoundTrip
        fields = ['source_city', 'pickup_datetime', 'return_datetime', 'contact_number']
        widgets = {
            'source_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Source City'}),
            'pickup_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'return_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Contact Number'}),
        }


class DestinationFormSet(forms.ModelForm):
    class Meta:
        model = Destination
        fields = ['destination_city',]
        widgets = {
            'destination_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Destination City'}),
        }


class RoadTripBookingForm(forms.ModelForm):
    class Meta:
        model = RoadTripBooking
        fields = ['start_city', 'destination', 'start_datetime', 'contact_number']
        widgets = {
            'start_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Starting City'
            }),
            'destination': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Trip Route or Destination'
            }),
            'start_datetime': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Contact Number'}),
        }


class LocalTransferForm(forms.ModelForm):
    class Meta:
        model = LocalTransfer
        fields = ['source_city', 'drop_location', 'pickup_time', 'contact_number']
        widgets = {
            'source_city': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter Source City'
            }),
            'drop_location': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter Drop Location'
            }),
            'pickup_time': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'type': 'datetime-local'
            }),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Contact Number'}),
        }



class BookingRequestForm(forms.ModelForm):
    accepted_terms = forms.BooleanField(required=True, label="I accept the Terms & Conditions")

    class Meta:
        model = BookingRequest
        fields = [
            'full_name', 'mobile', 'email', 'pickup_location',
            'pickup_datetime', 'payment_method', 'payment_screenshot',
            'pay_later', 'accepted_terms'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Enter Full Name'}),
            'mobile': forms.TextInput(attrs={'placeholder': 'Enter Your Mobile Number'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter Email Address'}),
            'pickup_location': forms.TextInput(attrs={'placeholder': 'Enter Pickup Location'}),
            'pickup_datetime': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'placeholder': 'Select Pickup Date and Time'
            }),
            'payment_method': forms.RadioSelect(),
        }