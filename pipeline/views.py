from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Episode, StageSubmission, UserProfile
from .forms import LoginForm, EpisodeForm, StageSubmissionForm, UserProfileForm

STAGE_ORDER = ['scripting', 'recording', 'animation', 'editing', 'done']


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('dashboard')
    return render(request, 'pipeline/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    episodes = Episode.objects.all().prefetch_related('submissions')
    stage_counts = {stage: episodes.filter(current_stage=stage).count() for stage, _ in Episode.STAGE_CHOICES}
    return render(request, 'pipeline/dashboard.html', {
        'episodes': episodes,
        'stage_counts': stage_counts,
        'stages': Episode.STAGE_CHOICES,
    })


@login_required
def episode_create(request):
    if request.method == 'POST':
        form = EpisodeForm(request.POST)
        if form.is_valid():
            episode = form.save(commit=False)
            episode.created_by = request.user
            episode.save()
            messages.success(request, f'Episode "{episode.title}" created.')
            return redirect('episode_detail', pk=episode.pk)
    else:
        form = EpisodeForm()
    return render(request, 'pipeline/episode_form.html', {'form': form, 'action': 'Create'})


@login_required
def episode_detail(request, pk):
    episode = get_object_or_404(Episode, pk=pk)
    submissions = episode.submissions.select_related('submitted_by').order_by('stage', '-submitted_at')
    user_team = request.user.profile.team
    can_submit = (episode.current_stage == user_team) or (user_team == 'admin')
    can_advance = can_submit and episode.current_stage != 'done'
    return render(request, 'pipeline/episode_detail.html', {
        'episode': episode,
        'submissions': submissions,
        'can_submit': can_submit,
        'can_advance': can_advance,
        'stage_order': STAGE_ORDER,
    })


@login_required
def stage_submit(request, pk):
    episode = get_object_or_404(Episode, pk=pk)
    user_team = request.user.profile.team

    if episode.current_stage == 'done':
        messages.error(request, 'This episode is already complete.')
        return redirect('episode_detail', pk=pk)

    if user_team not in ['admin', episode.current_stage]:
        messages.error(request, "You can only submit for your team's current stage.")
        return redirect('episode_detail', pk=pk)

    if request.method == 'POST':
        form = StageSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.episode = episode
            submission.stage = episode.current_stage
            submission.submitted_by = request.user
            submission.save()

            current_index = STAGE_ORDER.index(episode.current_stage)
            episode.current_stage = STAGE_ORDER[current_index + 1]
            episode.save()

            messages.success(request, f'Submitted! Episode moved to {episode.get_current_stage_display()} stage.')
            return redirect('episode_detail', pk=pk)
    else:
        form = StageSubmissionForm()

    return render(request, 'pipeline/stage_submit.html', {
        'form': form,
        'episode': episode,
        'stage_label': dict(Episode.STAGE_CHOICES).get(episode.current_stage, ''),
    })


@login_required
def team_view(request, team):
    valid_teams = [s for s, _ in Episode.STAGE_CHOICES if s != 'done']
    if team not in valid_teams:
        return redirect('dashboard')
    episodes_active = Episode.objects.filter(current_stage=team)
    episodes_done = Episode.objects.filter(submissions__stage=team).distinct().exclude(current_stage=team)
    return render(request, 'pipeline/team_view.html', {
        'team': team,
        'team_label': dict(Episode.STAGE_CHOICES)[team],
        'episodes_active': episodes_active,
        'episodes_done': episodes_done,
    })


@login_required
def admin_users(request):
    if request.user.profile.team != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Admin only.')
        return redirect('dashboard')
    users = User.objects.select_related('profile').all()
    return render(request, 'pipeline/admin_users.html', {'users': users})


@login_required
def edit_user_team(request, user_id):
    if request.user.profile.team != 'admin' and not request.user.is_superuser:
        return redirect('dashboard')
    target_user = get_object_or_404(User, pk=user_id)
    form = UserProfileForm(request.POST or None, instance=target_user.profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"{target_user.username}'s team updated.")
        return redirect('admin_users')
    return render(request, 'pipeline/edit_user_team.html', {'form': form, 'target_user': target_user})
