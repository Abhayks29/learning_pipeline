from django.contrib import admin
from .models import UserProfile, Episode, StageSubmission


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'team']
    list_filter = ['team']


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ['title', 'current_stage', 'created_by', 'created_at']
    list_filter = ['current_stage']
    search_fields = ['title', 'tags']


@admin.register(StageSubmission)
class StageSubmissionAdmin(admin.ModelAdmin):
    list_display = ['episode', 'stage', 'submitted_by', 'submitted_at']
    list_filter = ['stage']
