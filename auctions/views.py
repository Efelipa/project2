from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.forms.widgets import Widget
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import User, auctions_listing, Bid, watch_list, comment
from django.db.models import Max
from django import forms


class bid_form(forms.Form):
    bid_form = forms.IntegerField(required=True, label=(
        "Make a Bid"))
    bid_form.widget.attrs.update({"class": "form-control"})


class comment_form(forms.Form):
    comment_form = forms.CharField(widget=forms.Textarea(
    ), label='Comment Here')
    comment_form.widget.attrs.update({"class": "form-control", "rows": "4"})


def index(request):
    listing = auctions_listing.objects.all()
    return render(request, "auctions/index.html", {
        "lists": listing,
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


# Listing function
@login_required(login_url='/login')
def add_auction(request):
    if request.method == "POST":
        name = request.POST["name"]
        description = request.POST["description"]
        category = request.POST["category"]
        image = request.POST["image"]
        bid_start = request.POST["bid_start"]
        owner = request.POST["owner"]
        user_owner = User.objects.get(username=owner)
        try:
            listing = auctions_listing(name=name, description=description,
                                       category=category, image=image, start_bid=bid_start, owner=user_owner)
            listing.save()
            return HttpResponseRedirect(reverse("index"))
        except IntegrityError:
            return render(request, "auctions/add_auction.html", {
                "message": "Error, the auction cannot be added"
            })
    return render(request, "auctions/add_auction.html")


# Listing Page
@login_required(login_url='/login')
def list_pages(request, auction_id):
    try:
        listing = auctions_listing.objects.get(id=auction_id)
        current_user = request.user.id
        bid = Bid.objects.filter(bid_list=auction_id).count()
        if bid > 0:
            max_bid = Bid.objects.filter(
                item_bid=auction_id).aggregate(Max('bid'))
            max_bid = max_bid['bid__max']
        else:
            max_bid = listing.start_bid
        if watch_list.objects.filter(user=current_user, item=auction_id).exists():
            watchlist = False
        else:
            watchlist = True
    except auctions_listing.DoesNotExist:
        raise Http404("This Page does not exist")
    # comments = comment.objects.get(item=auction_id)
    context = {
        "bid_form": bid_form,
        "comment_form": comment_form,
    }
    return render(request, "auctions/auctions.html", context)
