from django.http import HttpResponse


def show_map(request):
    print('Кто-то зашёл на главную!')
    return HttpResponse('Привет!')