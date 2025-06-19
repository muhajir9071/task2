from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Token, User

class CustomTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Token '):
            return None

        token_key = auth_header.split(' ')[1]
        try:
            token = Token.objects.get(key=token_key)
            user = User.objects.get(id=token.user_id)  # ✅ MATCHES your model
            return (user, None)
        except (Token.DoesNotExist, User.DoesNotExist):
            raise AuthenticationFailed('Invalid or expired token')



