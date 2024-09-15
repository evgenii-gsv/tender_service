from django.contrib import admin

from .models import Bid, BidDecision, BidReview, BidVersion

admin.site.register(Bid)
admin.site.register(BidVersion)
admin.site.register(BidReview)
admin.site.register(BidDecision)
