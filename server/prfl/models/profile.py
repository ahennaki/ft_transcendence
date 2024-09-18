from django.db                  import models
from authentication.models      import CustomUser
from django.utils.translation   import gettext_lazy as _

class Profile(models.Model):
    BADGE_CHOICES = [
        ('BRONZE', 'Bronze'),
        ('SILVER', 'Silver'),
        ('GOLD', 'Gold'),
        ('PLATINUM', 'Platinum'),
        ('DIAMOND', 'Diamond'),
        ('HEROIC', 'Heroic'),
        ('GRAND_MASTER', 'Grand Master'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    email = models.CharField(_("email"), max_length=150, unique=True, blank=True)
    username = models.CharField(_("username"), max_length=150, unique=True, blank=True)
    first_name = models.CharField(_("first_name"), max_length=150, blank=True, null=True)
    last_name = models.CharField(_("last_name"), max_length=150, blank=True, null=True)
    is_online = models.BooleanField(_("is_online"), default=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    picture = models.CharField(_("profile picture"), max_length=150, blank=True)
    background_picture = models.CharField(_("background picture"), max_length=150, blank=True)
    rank = models.IntegerField(_("Rank"), default=0)
    total = models.IntegerField(_("total"), default=0)
    wins = models.IntegerField(_("wins"), default=0)
    loses = models.IntegerField(_("loses"), default=0)
    isSettings = models.BooleanField(_("isSettings"), default=False)
    # matchStatus = models.CharField(max_length=150, default='wait')
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated_at"), auto_now=True)

    badge = models.CharField(
        max_length=15,
        choices=BADGE_CHOICES,
        default='BRONZE',
    )

    def __str__(self):
        return self.username
