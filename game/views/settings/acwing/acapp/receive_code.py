from django.http import JsonResponse
from django.shortcuts import redirect
from django.core.cache import cache
from django.contrib.auth.models import User
from game.models.player.player import Player
from django.contrib.auth import login
from random import randint
import requests


def receive_code(request):
    # 接收acwing回传的授权码和授权状态
    data = request.GET

    if "errcode" in data:
        return JsonResponse({
            'result': "apply code failed!",
            'errcode': data['errcode'],
            'errmsg': data['errmsg']
        })

    code = data.get("code")
    state = data.get("state")

    # 如果当前授权状态state不一致
    if not cache.has_key(state):
        return JsonResponse({
            'result': "state not exist"
        })
    cache.delete(state)

    # 请求access_token和openid
    apply_access_token_url = "https://www.acwing.com/third_party/api/oauth2/access_token/"
    params = {
        'appid': "7117",
        'secret': "1f93829fda1842bbbaa122bb73243a19",
        'code': code,
    }

    access_token_res = requests.get(apply_access_token_url, params=params).json()

    access_token = access_token_res.get("access_token")
    openid = access_token_res.get("openid");

    players = Player.objects.filter(openid=openid)
    if players.exists(): # 该用户已存在，则无需重新获取信息，直接登录即可
        player = players[0]
        return JsonResponse({
            'result': "success",
            'username': player.user.username,
            'photo': player.photo
        })

    get_userinfo_url = "https://www.acwing.com/third_party/api/meta/identity/getinfo/"
    params = {
        'access_token': access_token,
        'openid': openid,
    }

    userinfo_res = requests.get(get_userinfo_url, params=params).json()

    username = userinfo_res.get("username")
    photo = userinfo_res.get("photo")

    # 如果该用户名已经存在修改该用户名直到完成
    while User.objects.filter(username=username):
        username += str(randint(0, 9))

    # web端数据库新增用户、玩家
    user = User.objects.create(username=username)
    player = Player.objects.create(user=user, photo=photo, openid=openid)

    return JsonResponse({
        'result': "success",
        'username': player.user.username,
        'photo': player.photo
    })
