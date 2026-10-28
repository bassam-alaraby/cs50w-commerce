from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    category = models.CharField(
        max_length=64,
        blank=True
    )
    image_url = models.URLField(blank=True)
    initial_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="listings"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

class Bid(models.Model):
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="bids"
    )
    bidder = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="bids"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    content = models.TextField()
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="comments"
    )
    timestamp = models.DateTimeField(auto_now_add=True)