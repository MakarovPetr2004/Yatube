from django.shortcuts import render
from django.http import HttpResponse


def group_posts(request, slug):
    return HttpResponse(f'Страница группы {slug}')
