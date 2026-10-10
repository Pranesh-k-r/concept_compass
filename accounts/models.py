from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_teacher = models.BooleanField(default=False)
    
    # Gamification
    points = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.user.username
    
    def update_streak(self):
        today = timezone.now().date()
        if self.last_active_date == today:
            return # Already updated today
            
        if self.last_active_date == today - timezone.timedelta(days=1):
            self.current_streak += 1
        else:
            self.current_streak = 1
            
        self.last_active_date = today
        self.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
