from django.db import models
from django.contrib.auth.models import User
from matches.models import Match

class UserProfile(models.Model):
    AVATAR_CHOICES = [
        ('https://api.dicebear.com/7.x/avataaars/svg?seed=Felix', 'Avatar 1'),
        ('https://api.dicebear.com/7.x/avataaars/svg?seed=Aneka', 'Avatar 2'),
        ('https://api.dicebear.com/7.x/avataaars/svg?seed=Sawyer', 'Avatar 3'),
        ('https://api.dicebear.com/7.x/avataaars/svg?seed=Lilly', 'Avatar 4'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profiles')
    name = models.CharField(max_length=50)
    avatar = models.URLField(default='https://api.dicebear.com/7.x/avataaars/svg?seed=Felix')

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_user_profile_name')
        ]

class Watchlist(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='watchlist')
    item = models.ForeignKey(Match, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'item')

    def __str__(self):
        return f"{self.profile.name} - {self.item.title}"
