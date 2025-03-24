from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from Chikara.views import header,BASE_DIR,STATIC_ROOT
def usersettings(request):
    html = header(request) + open(str(BASE_DIR) + "/" + STATIC_ROOT + "/html/usersettings.html").read()
    return HttpResponse(html)