from django.urls import reverse
from django.shortcuts import redirect
class ValidarUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        #print('aca esta el username:',request.user.username)
        if not request.user.is_authenticated :  #el usuario no es autenticado
            print('el de aca,',request.path)
            print('imprimo aca',request.user.username)
            if request.path not in ['/login/auth0','/complete/auth0'] :
                print('aca es donde debe de redirigir aca',request.path)
                return  redirect('/login/auth0')

        response = self.get_response(request)
            # Code to be executed for each request/response after
            # the view is called.
        return response
