
from django.shortcuts import redirect
from dbview.models import User
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from Chikara.views import checklogin

class CheckUserAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Check if the user is authenticated (you could use other conditions here)
        username = request.COOKIES.get('username')
        password = request.COOKIES.get('password')  # Get the session ID (assuming this is how it's stored)

            # Use the checklogin function to verify the credentials
        accept = checklogin(username, password)[0]
            
        if not accept and username != None and password != None:
            # If the credentials are invalid, revoke session and cookies
            request.session.flush()  # Clear the session
            response = redirect(request.META.get('HTTP_REFERER', '/'))  # Redirect to the previous URL or homepage
            response.delete_cookie('username')
            response.delete_cookie('password')
            return response  # Return the response (user will be redirected)
