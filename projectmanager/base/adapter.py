
from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect

class MyAccountAdapter(DefaultAccountAdapter, SuccessMessageMixin):
    success_message = 'ล็อกอินเรียบร้อยแล้ว'
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user
        if user.id and not sociallogin.is_existing:
            sociallogin.connect(request, user)

    def get_login_redirect_url(self, request):
        # print(dir(request))
        # print(request.path)
        if request.path == "/accounts/line/login/callback/":
            path = "https://liff.line.me/2006388485-NY13dxAd/profile/"
        else:
            path = "/profile"
        return path.format(username=request.user.username)
    
    def get_signup_redirect_url(self, request):
        # print(dir(request))
        # print(request.path)
        if request.path == "/accounts/line/login/callback/":
            path = "https://liff.line.me/2006388485-NY13dxAd/profile/"
        else:
            path = "/profile"
        return path.format(username=request.user.username)