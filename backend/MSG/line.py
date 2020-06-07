import requests
from django.conf import settings
import logging
from linebot import LineBotApi
from linebot.models import TextSendMessage
from django.shortcuts import render, redirect
from django.http import HttpResponse
from backend.models import line_user

line_client_id = settings.LINE_CLIENT_ID
line_client_secret = settings.LINE_CLIENT_SECRET

def send_msg(office, title, link):
    users = line_user.objects.all()
    for user in users:
        msg = f"{office}公告：\n{title}\n{link}"
        headers = {
            "Authorization": "Bearer " + user.token,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = {'message': msg}
        r = requests.post("https://notify-api.line.me/api/notify", headers=headers,
                        params=payload)
    logging.info(f"Line - office: {msg}")


def auth(request):
    # the annotation can not work
    url = 'https://notify-bot.line.me/oauth/authorize?'
    response_type = 'code'
    client_id = line_client_id
    redirect_uri = 'http://127.0.0.1:8000/callback/'
    scope = 'notify'
    state = 'NO_STATE'
    url = f'{url}response_type={response_type}&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&state={state}'

    return redirect(url)


def callback(request):
    token = request.GET['code']
    url = 'https://notify-bot.line.me/oauth/token'
    payload = {'grant_type': 'authorization_code', 
            'code': token,
            'redirect_uri': 'http://127.0.0.1:8000/callback/',
            'client_id': line_client_id,
            'client_secret': line_client_secret
    }
    r = requests.post(url, params = payload)
    if(r.ok):
        token = r.json()['access_token']
        (target_type, target) = get_status(token)
        unit = line_user.objects.create(token=token, target_type=target_type, target=target) 
        unit.save()
        return HttpResponse("Succeed")
    else:
        return HttpResponse("Fail")


def get_status(token):
    url = 'https://notify-api.line.me/api/status'
    headers = {'Authorization': 'Bearer ' + token}
    r = requests.get(url, headers=headers)
    if(r.ok):
        target_type = r.json()['targetType']
        target = r.json()['target']
        return target_type, target
    else:
        return 'fail'