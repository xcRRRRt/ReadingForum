from django import views
from django.shortcuts import render
from utils.view_decorator import AuthRequired


# Create your views here.

@AuthRequired.admin_required
class AdminIndexView(views.View):

    def get(self, request, *args, **kwargs):
        return render(request, 'admin_base.html')

    def post(self, request, *args, **kwargs):
        pass


@AuthRequired.admin_required
def test(request):
    return render(request, 'admin_base.html')
