from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from .middleware import auth_middleware
import json


@csrf_exempt
def register_view(request):

    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))

            name = data.get('name')    
            email = data.get('email')
            password = data.get('password')

            if not name or not email or not password:
                return JsonResponse({'message': 'All fields are required.'}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({'message': 'Username already taken.'}, status=400)

            user = User.objects.create(
                username=name,
                email=email,
                password=make_password(password)
            )

            return JsonResponse({
               'message': 'User registered successfully.',
               'username': user.username,
               'email': user.email,
             }, status=200)


        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON.'}, status=400)

        except Exception as e:
            return JsonResponse({'message': 'Something went wrong.', 'error': str(e)}, status=500)

    return JsonResponse({'message': 'Invalid request method.'}, status=405)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('name')  # name means username here
            password = data.get('password')
        except Exception:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)

        if not username or not password:
            return JsonResponse({'message': 'Username and password required.'}, status=400)

        user = authenticate(request, username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return JsonResponse({
             'message': 'Login successful',
             'username': user.username,
             'email': user.email,
             'access': str(refresh.access_token),
             'refresh': str(refresh),
            }, status=200)
        
        else:
            return JsonResponse({'message': 'Invalid credentials'}, status=401)

    return JsonResponse({'message': 'Invalid request method'}, status=405)

@csrf_exempt
# @auth_middleware
def logout_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            refresh_token = data.get('refresh')

            if not refresh_token:
                return JsonResponse({'message': 'Refresh token is required.'}, status=400)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return JsonResponse({'message': 'User logged out and token blacklisted.'}, status=200)

        except Exception as e:
            return JsonResponse({'message': 'Error logging out.', 'error': str(e)}, status=500)

@csrf_exempt
def refresh_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            refresh_token = data.get('refresh')

            if not refresh_token:
                return JsonResponse({'message': 'Refresh token is required.'}, status=400)

            serializer = TokenRefreshSerializer(data={'refresh': refresh_token})
            if serializer.is_valid():
                return JsonResponse(serializer.validated_data, status=200)
            else:
                return JsonResponse({'message': 'Invalid refresh token.', 'errors': serializer.errors}, status=401)

        except Exception as e:
            return JsonResponse({'message': 'Something went wrong.', 'error': str(e)}, status=500)

    return JsonResponse({'message': 'Invalid request method.'}, status=405)

