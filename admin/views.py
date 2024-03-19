from django import views
from django.shortcuts import render


# Create your views here.

class AdminIndexView(views.View):
    def get(self, request):
        return render(request, 'admin_base.html')

    def post(self, request):
        pass
