from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    TEAM_CHOICES = [
        ('scripting', 'Scripting'),
        ('recording', 'Recording'),
        ('animation', 'Animation'),
        ('editing', 'Editing'),
        ('admin', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    team = models.CharField(max_length=20, choices=TEAM_CHOICES, default='admin')

    def __str__(self):
        return f"{self.user.username} ({self.get_team_display()})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Episode(models.Model):
    STAGE_CHOICES = [
        ('scripting', 'Scripting'),
        ('recording', 'Recording'),
        ('animation', 'Animation'),
        ('editing', 'Editing'),
        ('done', 'Done'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tags = models.CharField(max_length=300, blank=True, help_text='Comma separated tags')
    current_stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='scripting')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_episodes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def stage_index(self):
        stages = ['scripting', 'recording', 'animation', 'editing', 'done']
        return stages.index(self.current_stage)

    def progress_percent(self):
        return (self.stage_index() / 4) * 100


class StageSubmission(models.Model):
    STAGE_CHOICES = [
        ('scripting', 'Scripting'),
        ('recording', 'Recording'),
        ('animation', 'Animation'),
        ('editing', 'Editing'),
    ]

    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name='submissions')
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES)
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to='submissions/%Y/%m/', blank=True, null=True)
    notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.episode.title} — {self.get_stage_display()}"
