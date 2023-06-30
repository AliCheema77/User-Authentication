from django.urls import path
from users.views import (
    InvitationVerification
)

urlpatterns = [
    path("invitation/", InvitationVerification.as_view(), name="invitation"),
]
