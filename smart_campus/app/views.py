from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required

from .models import (
    User, Reward, Permission,
    Station,
)


@csrf_exempt
@require_POST
def signup(request):
    """
    API

    Signup for APP users
    """
    email = request.POST.get('email')
    password = request.POST.get('password')
    nickname = request.POST.get('nickname')

    if User.objects.filter(email=email).exists():
        return JsonResponse({'status': 'false', 'message': 'User already exists!'})

    try:
        User.objects.create_user(email, password, nickname)
    except ValueError as error:
        return JsonResponse({'status': 'false', 'message': error})

    return JsonResponse({'status': 'true', 'message': 'Success'})


@csrf_exempt
@require_POST
def signin(request):
    """
    API

    Sign in for APP users
    """
    email = request.POST.get('email')
    password = request.POST.get('password')
    user = authenticate(request, username=email, password=password)
    if user is not None:
        login(request, user)
        user_data = {
            'nickname': user.nickname,
            'experience_point': user.experience_point,
            'coins': user.earned_coins,
            'reward': [reward.id for reward in user.received_rewards.all()],
            'favorite_stations': [station.id for station in user.favorite_stations.all()],
        }
        return JsonResponse({'status': 'true', 'message': 'Success', 'data': user_data})

    return JsonResponse({'status': 'false', 'message': 'Login failed'})


@csrf_exempt
@require_POST
def signout(request):
    """
    API

    Sign out for APP users
    """
    logout(request)
    return JsonResponse({'status': 'true', 'message': 'Success'})


@csrf_exempt
def log_in(request):
    """
    Login for Management Backend Page
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')

    email = request.POST.get('email')
    password = request.POST.get('password')
    user = authenticate(request, username=email, password=password)

    if user is not None and user.can(Permission.EDIT):
        login(request, user)
        return HttpResponseRedirect('/')
    return render(request, 'app/login.html')


def log_out(request):
    logout(request)
    return HttpResponseRedirect('/login/')


@login_required
def index(request):
    return render(request, 'app/index.html')


@csrf_exempt
def get_all_rewards(request):
    """
    API

    Retrieve all rewards (NOT personal)
    """
    data = []
    for reward in Reward.objects.all():
        entry = {
            'id': reward.id,
            'name': reward.name,
            'image_url': reward.image.url
        }
        data.append(entry)

    return JsonResponse({'status': 'true', 'message': 'Success', 'data': data})


@csrf_exempt
def get_all_stations(request):
    """
    API

    Retrieve contents of all Stations
    """
    data = []
    for station in Station.objects.all():
        entry = {
            'id': station.id,
            'name': station.name,
            'content': station.content,
            'category': str(station.category),
            'image': [{'image_url': img.image.url, 'primary': img.is_primary}
                      for img in station.stationimage_set.all()]
        }
        data.append(entry)

    return JsonResponse({'status': 'true', 'message': 'Success', 'data': data})
