from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.expressions import Value
from django.forms.widgets import Widget
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import User, auctions_listing, Bid, watch_list, comment
from django.db.models import Max
from django import forms


class bid_form(forms.Form):
    bid_form = forms.IntegerField(required=True, label=(
        "Make a Bid"), )
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
        count = Bid.objects.filter(bid_list=auction_id).count()
        if count > 0:
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
    comments = comment.objects.filter(item_id=auction_id)
    listing = auctions_listing.objects.all()
    if request.method == 'POST':
        form = bid_form(request.POST)
        current_user = request.user.id
        auction_id = request.POST['auction_id']
        list_item = auctions_listing.objects.get(id=auction_id)
        user_bid = User.objects.get(id=current_user)
        listing = auctions_listing.objects.get(id=auction_id)
        if form.is_valid():
            current_bid = form.cleaned_data['bid_form']
            count = Bid.objects.filter(bid_list=auction_id).count()
            if current_bid >= 1:
                max_bid = Bid.objects.filter(
                    bid_list=auction_id).aggregate(Max('bid'))
                max_bid = max_bid['bid__max']
            else:
                max_bid = list_item.start_bid
            if current_bid >= max_bid:
                bid = Bid(user_bid=user_bid,
                          bid_list=list_item.id, bid=current_bid)
                bid.save()
                return render(request, "auctions/auctions.html", {
                    "bid_form": bid_form(),
                    "comment_form": comment_form(),
                    "max_bid": max_bid,
                    "count": count,
                    "comments": comments,
                    "lists": list_item,
                    "success": f"Sucessfull Bid ({current_bid}).",
                })
            else:
                return render(request, "auctions/auctions.html", {
                    "bid_form": bid_form(),
                    "comment_form": comment_form(),
                    "max_bid": max_bid,
                    "count": count,
                    "comments": comments,
                    "lists": list_item,
                    "error": "Error: The bid can't be less than current bid."
                })
        else:
            return HttpResponseBadRequest("Form not valid")
    return render(request, 'auctions/auctions.html', {
        "lists": auctions_listing.objects.get(id=auction_id),
        "bid_form": bid_form(),
        "comment_form": comment_form(),
        "comments": comments,
        "watch_list": watchlist,
    })


# Comment creation
# def comments(request):
#     current_user = request.user.id
#     current_user = User.objects.get(id=current_user)
#     comment_forms = comment_form(request.POST)
#     if request.method == 'POST':
#         auction_id = request.POST['auction_id']
#         items = auctions_listing.objects.get(id=auction_id)
#         if comment.is_valid():
#             current_comment = comment_forms.cleaned_data['comment']
#             create_comment = comment(
#                 user=current_user, item_comment=items, comment=current_comment)
#             create_comment.save()
#             return HttpResponseRedirect(reverse("list_pages", args=(auction_id)))
#         else:
#             raise forms.ValidationError(comment_forms.errors)


# Categories
def category(request, category):
    categories = auctions_listing.objects.filter(category=category)
    return render(request, "auctions/category.html", {
        "category": category,
        "categories": categories,
    })
