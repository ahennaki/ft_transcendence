from django.db import models
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_totp.models import random_hex

class BackupCode(models.Model):
    device = models.ForeignKey(TOTPDevice, on_delete=models.CASCADE, related_name='backup_codes')
    code = models.CharField(max_length=8)
    used = models.BooleanField(default=False)