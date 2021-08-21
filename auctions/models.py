from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime


class User(AbstractUser):
    pass


class auctions_listing(models.Model):
    name = models.CharField(max_length=70)
    date_creation = models.DateTimeField(auto_now_add=True, blank=True)
    description = models.CharField(max_length=400)
    category = models.CharField(max_length=64, blank=True)
    image = models.CharField(max_length=265)
    start_bid = models.IntegerField()
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owner_list")
    active = models.BooleanField()
    winner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="winner_list", null=True, blank=True)

    def __str__(self):
        return f"{self.name} Owner: {self.owner}"


class watch_list(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, name="user")
    item = models.ForeignKey(
        auctions_listing, on_delete=models.CASCADE, name="item")

    def __str__(self):
        return f"{self.user} {self.item}"


class Bid(models.Model):
    user_bid = models.ForeignKey(User, on_delete=models.CASCADE, name="user")
    bid_list = models.ForeignKey(
        auctions_listing, on_delete=models.CASCADE, name="bid_list")
    bid = models.IntegerField()

    def __str__(self):
        return f"{self.user_bid} {self.bid_list} {self.bid}"


class comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, name="user")
    item = models.ForeignKey(
        auctions_listing, on_delete=models.CASCADE, name="item")
    comment = models.CharField(max_length=400)
    date = models.DateField(auto_now_add=True, blank=True)

    def __str__(self):
        return f"{self.user} {self.item} {self.date}"
