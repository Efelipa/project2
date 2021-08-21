from django.contrib import admin
from .models import User, auctions_listing, watch_list, Bid, comment
# Register your models here.
admin.site.register(User)
admin.site.register(auctions_listing)
admin.site.register(watch_list)
admin.site.register(Bid)
admin.site.register(comment)
