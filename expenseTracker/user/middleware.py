
from django.http import JsonResponse

# auth middleware

def auth_middleware(get_response):
    def middleware(request):
        # Check if the request has a valid JWT token
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                # Validate the token here (e.g., using a JWT library)
                # If valid, set user in request
                request.user = 'Authenticated User'  # Replace with actual user object
            except Exception as e:
                return JsonResponse({'message': 'Invalid token'}, status=401)
        else:
            return JsonResponse({'message': 'Authorization header missing'}, status=401)

        response = get_response(request)
        return response

    return middleware

