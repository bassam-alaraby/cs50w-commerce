from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.aggregates import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid, Comment


def listing_detail_context(request, listing, message=None):
    highest_bid = listing.bids.order_by("-amount").first()

    is_winner = (
        not listing.is_active
        and highest_bid is not None
        and request.user.is_authenticated
        and highest_bid.bidder == request.user
    )

    return {
        "listing": listing,
        "highest_bid": highest_bid,
        "is_winner": is_winner,
        "message": message,
    }


def index(request):
    listings = Listing.objects.filter(is_active=True).annotate(
        highest_bid=Max("bids__amount")
    )

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


def view_listing(request, listing_id):
    try:
        listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        return HttpResponse("Listing not found.", status=404)

    return render(
        request,
        "auctions/view_listing.html",
        listing_detail_context(request, listing)
    )


@login_required
def view_my_listings(request):
    listings = Listing.objects.filter(owner=request.user)
    return render(request, "auctions/my_listings.html", {
        "listings": listings
    })


@login_required
def disable_listing(request, listing_id):
    try:
        listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        return HttpResponse("Listing not found.", status=404)

    # Check if the logged-in user is the owner of the listing
    if request.user != listing.owner:
        return HttpResponse("You are not authorized to disable this listing.", status=403)

    # Disable the listing
    listing.is_active = False
    listing.save()

    return HttpResponseRedirect(reverse("listing_detail", args=[listing_id]))


@login_required
def view_my_wins(request):
    listings = Listing.objects.filter(
        is_active=False,
        bids__bidder=request.user
    ).distinct()

    won_listings = []

    for listing in listings:
        highest_bid = listing.bids.order_by("-amount").first()

        if highest_bid and highest_bid.bidder == request.user:
            won_listings.append({
                "listing": listing,
                "highest_bid": highest_bid,
            })

    return render(request, "auctions/my_wins.html", {
        "won_listings": won_listings
    })


@login_required
def add_bid(request, listing_id):
    if request.method != "POST":
        return HttpResponse("Method not allowed.", status=405)

    try:
        listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        return HttpResponse("Listing not found.", status=404)

    bid_amount = request.POST["bid_amount"]
    highest_bid = listing.bids.order_by('-amount').first()

    # Check if the listing is not active
    if not listing.is_active:
        return render(
            request,
            "auctions/view_listing.html",
            listing_detail_context(request, listing, "This auction is closed.")
        )

    # Check if the user is the owner of the listing
    if request.user == listing.owner:
        return render(
            request,
            "auctions/view_listing.html",
            listing_detail_context(request, listing, "You cannot bid on your own listing.")
        )

    # Validate the bid amount
    try:
        decimal_bid_amount = Bid._meta.get_field("amount").clean(
            bid_amount,
            None
        )
    except ValidationError:
        return render(
            request,
            "auctions/view_listing.html",
            listing_detail_context(request, listing, "Invalid bid amount.")
        )

    # Check if the bid is higher than the current highest bid or initial price
    if highest_bid and decimal_bid_amount <= highest_bid.amount:
        return render(
            request,
            "auctions/view_listing.html",
            listing_detail_context(request, listing, "Your bid must be higher than the current highest bid.")
        )
    elif not highest_bid and decimal_bid_amount <= listing.initial_price:
        return render(
            request,
            "auctions/view_listing.html",
            listing_detail_context(request, listing, "Your bid must be higher than the initial price.")
        )

    # Create a new bid
    new_bid = Bid(
        amount=decimal_bid_amount,
        listing=listing,
        bidder=request.user
    )
    new_bid.save()

    return HttpResponseRedirect(reverse("listing_detail", args=[listing_id]))


@login_required
def add_comment(request, listing_id):
    if request.method != "POST":
        return HttpResponse("Method not allowed.", status=405)

    try:
        listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        return HttpResponse("Listing not found.", status=404)

    comment_content = request.POST["comment_content"]

    # Validate the comment content
    if not comment_content.strip():
        return render(
            request,
            "auctions/view_listing.html",
            listing_detail_context(request, listing, "Comment cannot be empty.")
        )

    # Create a new comment
    new_comment = Comment(
        content=comment_content,
        listing=listing,
        author=request.user
    )
    new_comment.save()

    return HttpResponseRedirect(reverse("listing_detail", args=[listing_id]))


@login_required
def add_to_watchlist(request, listing_id):
    try:
        listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        return HttpResponse("Listing not found.", status=404)

    if not request.user.is_authenticated:
        return HttpResponse("You must be logged in to add items to your watchlist.", status=403)

    request.user.watchlist.add(listing)
    return HttpResponseRedirect(reverse("listing_detail", args=[listing_id]))


@login_required
def remove_from_watchlist(request, listing_id):
    try:
        listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        return HttpResponse("Listing not found.", status=404)

    if not request.user.is_authenticated:
        return HttpResponse("You must be logged in to remove items from your watchlist.", status=403)

    request.user.watchlist.remove(listing)
    return HttpResponseRedirect(reverse("listing_detail", args=[listing_id]))


@login_required
def view_watchlist(request):
    watchlist_items = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "watchlist_items": watchlist_items
    })