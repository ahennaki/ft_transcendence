from rest_framework         import generics, status
from django.http            import JsonResponse
from django.contrib.auth    import get_user_model
from django.conf            import settings
from django.core.mail       import send_mail
from django.core.mail       import EmailMessage
from django.template.loader import render_to_string
from datetime               import datetime, timezone, timedelta
import jwt
import uuid

User = get_user_model()

def gen_token(user):
    expr = datetime.now(timezone.utc) + timedelta(hours=1)
    token = jwt.encode(
        payload= {
            'exp': expr,
            'user_id': user.id,
            'email': user.email,
            'jti': str(uuid.uuid4()),
        },
        key= settings.SIMPLE_JWT['SIGNING_KEY'],
        algorithm='HS256'
    )
    return token

class RequestReset(generics.GenericAPIView):
    def post(self, request):
        email = request.data['email']
        user = User.objects.filter(email=email).first()

        if not email:
            return JsonResponse(
                {"message": "Email is required"},
                status = status.HTTP_400_BAD_REQUEST
            )
        if user:
            token = gen_token(user)
            reset_url = f'http://localhost:3000/resetpassword/{token}'
            subject = 'Password Reset Request'
            message = render_to_string('email.html', {
                'user': user,
                'reset_url': reset_url,
            })
            try:
                email = EmailMessage(
                    subject,
                    message,
                    'postmaster@sandbox31269e2e227946aca04414c12fc2053f.mailgun.org',
                    [email]
                )
                email.content_subtype = 'html'
                email.send()
            except Exception as e:
                print(f'&&&&&&&&&& {str(e)}')
            return JsonResponse(
                {"message": "Password reset email sent"},
                status = status.HTTP_200_OK
            )
        return JsonResponse(
            {"message": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    