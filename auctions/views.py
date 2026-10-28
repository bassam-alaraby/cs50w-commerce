from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Listing, User


def index(request):
    # Display all active listings
    listings = Listing.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        category = request.POST.get("category", "")
        image_url = request.POST.get("image_url", "")
        initial_price = request.POST["initial_price"]

        # Validate the input data
        if not title or not description or not initial_price:
            return render(request, "auctions/create_listing.html", {
                "message": "Title, description, and initial price are required."
            })

        try:
            decimal_initial_price = Listing._meta.get_field("initial_price").clean(
                initial_price,
                None
            )
        except ValidationError:
            return render(request, "auctions/create_listing.html", {
                "message": "Invalid initial price."
            })
        
        # Check if the initial price is a positive number
        if not decimal_initial_price.is_finite() or decimal_initial_price <= 0:
            return render(request, "auctions/create_listing.html", {
                "message": "Initial price must be a positive number."
            })

        # Create a new listing
        listing = Listing(
            title=title,
            description=description,
            category=category,
            image_url=image_url,
            initial_price=decimal_initial_price,
            owner=request.user
        )
        listing.save()

        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/create_listing.html")
