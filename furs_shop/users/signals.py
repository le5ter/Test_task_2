from django.db.models.signals import post_save
from django.dispatch import receiver
from social_django.models import UserSocialAuth
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=UserSocialAuth)
def create_user_from_social_account(sender, instance, created, **kwargs):
    if created:
        social_account = instance
        user = social_account.user

        if not user.username:
            user.username = social_account.extra_data.get('name', '')
        if not user.email:
            user.email = social_account.extra_data.get('email', '')
        user.save()
