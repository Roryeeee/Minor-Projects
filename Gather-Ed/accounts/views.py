# Path: accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .forms import SignUpForm, LoginForm, ProfileUpdateForm, RoleForm
from .models import Profile, Friendship, Role, UserRole
from django.views.decorators.http import require_http_methods

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('eventpollapp:dashboard')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('eventpollapp:dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('eventpollapp:dashboard')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})
# ...existing code...

def get_friends_for_user(user):
    friendships = Friendship.objects.filter(
        Q(from_user=user, status='accepted') |
        Q(to_user=user, status='accepted')
    ).select_related('from_user', 'to_user')
    friends = []
    for f in friendships:
        if f.from_user == user:
            friends.append(f.to_user)
        else:
            friends.append(f.from_user)
    # Remove duplicates and invalid users
    return [friend for friend in set(friends) if friend and friend.id]

@login_required
def profile_view(request, user_id=None):
    if user_id:
        user = get_object_or_404(User, id=user_id)
    else:
        user = request.user
    
    profile = user.profile
    is_own_profile = user == request.user
    
    # Check friendship status
    friendship_status = None
    if not is_own_profile:
        friendship = Friendship.objects.filter(
            Q(from_user=request.user, to_user=user) |
            Q(from_user=user, to_user=request.user)
        ).first()
        
        if friendship:
            friendship_status = friendship.status
    
    context = {
        'profile_user': user,
        'profile': profile,
        'is_own_profile': is_own_profile,
        'friendship_status': friendship_status,
    }
    return render(request, 'accounts/profile.html', context)

def get_pending_requests(user):
    return Friendship.objects.filter(
        to_user=user,
        status='pending'
    ).select_related('from_user')

@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})

@login_required
def friends_view(request):
    # All friendships where current user is involved and accepted
    friendships = Friendship.objects.filter(
        Q(from_user=request.user, status="accepted") |
        Q(to_user=request.user, status="accepted")
    ).select_related("from_user", "to_user")

    # Extract the actual friends (the other user in the relation)
    friends = []
    for f in friendships:
        if f.from_user == request.user:
            friends.append(f.to_user)
        else:
            friends.append(f.from_user)

    friends = get_friends_for_user(request.user)  # Should return User objects
    roles = Role.objects.filter(created_by=request.user)
    pending_requests = get_pending_requests(request.user)
    return render(request, 'accounts/friends.html', {
        'friends': friends,
        'roles': roles,
        'pending_requests': pending_requests,
    })
    # Remove invalid/null users just in case
    friends = [friend for friend in friends if friend and friend.id]

    pending_requests = Friendship.objects.filter(
        to_user=request.user, status="pending"
    ).select_related("from_user")

    roles = Role.objects.filter(created_by=request.user)

    context = {
        "friends": friends,
        "pending_requests": pending_requests,
        "roles": roles,
    }
    return render(request, "accounts/friends.html", context)




@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    
    if to_user == request.user:
        messages.error(request, "You can't send a friend request to yourself!")
        return redirect('accounts:profile', user_id=user_id)
    
    # Check if friendship already exists
    existing_friendship = Friendship.objects.filter(
        Q(from_user=request.user, to_user=to_user) |
        Q(from_user=to_user, to_user=request.user)
    ).first()
    
    if existing_friendship:
        messages.warning(request, "Friend request already exists!")
    else:
        Friendship.objects.create(from_user=request.user, to_user=to_user)
        messages.success(request, f"Friend request sent to {to_user.username}!")
    
    return redirect('accounts:profile', user_id=user_id)

@login_required
def respond_friend_request(request, friendship_id, action):
    friendship = get_object_or_404(Friendship, id=friendship_id, to_user=request.user)
    
    if action == 'accept':
        friendship.status = 'accepted'
        friendship.save()
        messages.success(request, f"You are now friends with {friendship.from_user.username}!")
    elif action == 'reject':
        friendship.status = 'rejected'
        friendship.save()
        messages.info(request, "Friend request rejected.")
    
    return redirect('accounts:friends')

@login_required
def search_users(request):
    query = request.GET.get('q', '')
    users = []
    
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id)[:10]
    
    return render(request, 'accounts/search_users.html', {'users': users, 'query': query})

@login_required
def manage_roles(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save(commit=False)
            role.created_by = request.user
            role.save()
            messages.success(request, f'Role "{role.name}" created successfully!')
            return redirect('accounts:manage_roles')
    else:
        form = RoleForm()
    
    user_roles = Role.objects.filter(created_by=request.user)
    return render(request, 'accounts/manage_roles.html', {'form': form, 'roles': user_roles})

@login_required
def assign_role(request, user_id, role_id):
    user = get_object_or_404(User, id=user_id)
    role = get_object_or_404(Role, id=role_id, created_by=request.user)
    
    # Check if they're friends
    are_friends = Friendship.objects.filter(
        Q(from_user=request.user, to_user=user, status='accepted') |
        Q(from_user=user, to_user=request.user, status='accepted')
    ).exists()
    
    if not are_friends:
        messages.error(request, "You can only assign roles to friends!")
        return redirect('accounts:friends')
    
    user_role, created = UserRole.objects.get_or_create(
        user=user, 
        role=role,
        defaults={'assigned_by': request.user}
    )
    
    if created:
        messages.success(request, f'Role "{role.name}" assigned to {user.username}!')
    else:
        messages.warning(request, f'{user.username} already has the role "{role.name}"!')
    
    return redirect('accounts:friends')

# @login_required
# @require_http_methods(["GET", "POST"])
# def logout_view(request):
#     logout(request)
#     return render(request, 'accounts/logout.html')