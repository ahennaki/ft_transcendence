from django.db                  import models
from django.utils.translation   import gettext_lazy as _
from .profile                   import Profile

class Notification(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='notifications')
    content = models.TextField()
    from_user = models.CharField(max_length=150)
    isrouted = models.BooleanField(default=False)
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)

    class Meta:
        ordering = ['created_at']
