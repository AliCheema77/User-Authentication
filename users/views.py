# import cStringIO as StringIO
import datetime
# from django.http import HttpResponse
# from cgi import escape
from html import escape
from io import BytesIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files import File
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import Context
from django.template.loader import get_template
from django.urls import reverse
from django.views import View
from django.views.generic import (
    DetailView,
    RedirectView,
    UpdateView,
)

# from portpass.encrypt import decrypt_data
# from portpass.s3_signed import get_pre_signed_s3_url
# from users.models import CompanyPeople
# from vaccinations.models import UserQRCode

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, UpdateView):

    model = User
    fields = ["name"]

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        return User.objects.get(username=self.request.user.username)


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()


class InvitationVerification(View):

    def get(self, request):
        data = request.GET.get("key")
        cancel = request.GET.get("cancel")
        if data:
            if " " in data:
                data = data.replace(" ", "+")
            decrypted = decrypt_data(data)
            key, user_id = decrypted.split("-")
            check = CompanyPeople.objects.filter(key=key).first()
            sender = User.objects.get(id=user_id)
            if check:
                if check.key == key:
                    if cancel:
                        check.status = "canceled"
                    else:
                        check.status = "joined"
                        check.joined_date = datetime.datetime.now()
                    check.company = sender
                    check.key = ""
                    check.save()
                    return redirect("/")
                else:
                    return HttpResponse("key does not match")
            else:
                return HttpResponse("Invitations link does not exists")
        else:
            return HttpResponse("You are not allowed.")
