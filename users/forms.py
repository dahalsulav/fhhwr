from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Customer, Worker


class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "phone_number", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.phone_number = self.cleaned_data["phone_number"]
        user.is_customer = True
        if commit:
            user.save()
            Customer.objects.create(user=user)
        return user


class WorkerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    location = forms.CharField(max_length=255, required=True)
    skills = forms.CharField(max_length=255, required=True)
    hourly_rate = forms.FloatField(required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "phone_number",
            "location",
            "skills",
            "hourly_rate",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.phone_number = self.cleaned_data["phone_number"]
        user.is_worker = True
        if commit:
            user.save()
            worker = Worker.objects.create(
                user=user,
                location=self.cleaned_data["location"],
                skills=self.cleaned_data["skills"],
                hourly_rate=self.cleaned_data["hourly_rate"],
            )
        return user

    def save_worker(self, user):
        worker = Worker.objects.create(
            user=user,
            location=self.cleaned_data["location"],
            skills=self.cleaned_data["skills"],
            hourly_rate=self.cleaned_data["hourly_rate"],
        )
        return worker


class CustomerUpdateForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = Customer
        fields = ("location", "profile_picture")

    def __init__(self, *args, **kwargs):
        customer = kwargs.pop("instance")
        user = customer.user
        super(CustomerUpdateForm, self).__init__(*args, **kwargs)
        self.fields["phone_number"].initial = user.phone_number
        self.fields["location"].initial = customer.location
        self.fields["profile_picture"].initial = customer.profile_picture

    def save(self, commit=True):
        instance = super(CustomerUpdateForm, self).save(commit=False)
        instance.user.phone_number = self.cleaned_data["phone_number"]
        if commit:
            instance.user.save()
            instance.save()
        return instance


class WorkerUpdateForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = Worker
        fields = (
            "location",
            "skills",
            "hourly_rate",
            "is_available",
            "profile_picture",
        )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("instance").user
        super(WorkerUpdateForm, self).__init__(*args, **kwargs)
        self.fields["phone_number"].initial = user.phone_number

    def save(self, commit=True):
        instance = super(WorkerUpdateForm, self).save(commit=False)
        instance.user.phone_number = self.cleaned_data["phone_number"]
        if commit:
            instance.user.save()
            instance.save()
        return instance
