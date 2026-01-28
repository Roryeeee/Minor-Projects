import os
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lusu_project.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Profile, Role, Friendship, UserRole
from eventpollapp.models import Event, DateOption, DateVote, EventRequirement, EventComment, EventParticipant
from bills.models import Bill, Expense

def create_sample_data():
    print("Creating sample data for LUSU...")
    
    # Create users
    users_data = [
        {'username': 'alice', 'email': 'alice@example.com', 'first_name': 'Alice', 'last_name': 'Johnson'},
        {'username': 'bob', 'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Smith'},
        {'username': 'charlie', 'email': 'charlie@example.com', 'first_name': 'Charlie', 'last_name': 'Brown'},
        {'username': 'diana', 'email': 'diana@example.com', 'first_name': 'Diana', 'last_name': 'Wilson'},
    ]
    
    users = {}
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'password': 'pbkdf2_sha256$260000$temp$temp'  # Password: 'password'
            }
        )
        if created:
            user.set_password('password')
            user.save()
            print(f"Created user: {user.username}")
        users[user_data['username']] = user
    
    # Update profiles
    for username, user in users.items():
        profile = user.profile
        profile.bio = f"Hi, I'm {user.first_name}! I love planning events and hanging out with friends."
        profile.save()
    
    # Create friendships
    friendships = [
        ('alice', 'bob'),
        ('alice', 'charlie'),
        ('alice', 'diana'),
        ('bob', 'charlie'),
        ('bob', 'diana'),
        ('charlie', 'diana'),
    ]
    
    for user1_name, user2_name in friendships:
        user1 = users[user1_name]
        user2 = users[user2_name]
        
        friendship, created = Friendship.objects.get_or_create(
            from_user=user1,
            to_user=user2,
            defaults={'status': 'accepted'}
        )
        if created:
            print(f"Created friendship: {user1_name} <-> {user2_name}")
    
    # Create roles
    roles_data = [
        {'name': 'Organizer', 'description': 'Main event organizers', 'created_by': 'alice'},
        {'name': 'Close Friends', 'description': 'Close friends group', 'created_by': 'alice'},
        {'name': 'Gaming Buddies', 'description': 'Gaming friends', 'created_by': 'bob'},
        {'name': 'Foodies', 'description': 'Food lovers', 'created_by': 'diana'},
    ]
    
    roles = {}
    for role_data in roles_data:
        role, created = Role.objects.get_or_create(
            name=role_data['name'],
            defaults={
                'description': role_data['description'],
                'created_by': users[role_data['created_by']]
            }
        )
        if created:
            print(f"Created role: {role.name}")
        roles[role_data['name']] = role
    
    # Assign roles to users
    role_assignments = [
        ('bob', 'Organizer', 'alice'),
        ('charlie', 'Organizer', 'alice'),
        ('diana', 'Close Friends', 'alice'),
        ('alice', 'Gaming Buddies', 'bob'),
        ('charlie', 'Gaming Buddies', 'bob'),
        ('alice', 'Foodies', 'diana'),
        ('bob', 'Foodies', 'diana'),
    ]
    
    for username, role_name, assigned_by in role_assignments:
        UserRole.objects.get_or_create(
            user=users[username],
            role=roles[role_name],
            defaults={'assigned_by': users[assigned_by]}
        )
    
    # Create events
    now = datetime.now()
    future_date1 = now + timedelta(days=7)
    future_date2 = now + timedelta(days=14)
    future_date3 = now + timedelta(days=21)
    
    events_data = [
        {
            'title': 'Weekend Gaming Session',
            'description': 'Let\'s get together for some gaming and pizza!',
            'creator': 'bob',
            'required_role': 'Gaming Buddies',
            'location': 'Bob\'s House',
            'date_options': [future_date1, future_date1 + timedelta(days=1)]
        },
        {
            'title': 'Food Festival Downtown',
            'description': 'Check out the new food festival with amazing vendors.',
            'creator': 'diana',
            'required_role': 'Foodies',
            'location': 'Downtown Food Plaza',
            'date_options': [future_date2, future_date2 + timedelta(hours=3)]
        },
        {
            'title': 'Movie Night',
            'description': 'Let\'s watch the latest Marvel movie!',
            'creator': 'alice',
            'required_role': None,  # Open to all
            'location': 'Alice\'s Place',
            'date_options': [future_date3, future_date3 + timedelta(days=1)]
        }
    ]
    
    created_events = []
    for event_data in events_data:
        event, created = Event.objects.get_or_create(
            title=event_data['title'],
            defaults={
                'description': event_data['description'],
                'creator': users[event_data['creator']],
                'required_role': roles.get(event_data['required_role']) if event_data['required_role'] else None,
                'location': event_data['location'],
            }
        )
        
        if created:
            print(f"Created event: {event.title}")
            
            # Create date options
            for date_option in event_data['date_options']:
                DateOption.objects.get_or_create(
                    event=event,
                    proposed_date=date_option,
                    defaults={'proposed_by': users[event_data['creator']]}
                )
            
            # Add some votes
            date_options = event.dateoption_set.all()
            if date_options:
                # Vote for first date option
                DateVote.objects.get_or_create(
                    date_option=date_options[0],
                    user=users[event_data['creator']]
                )
                
                # Add other voters based on role
                eligible_users = []
                if event.required_role:
                    eligible_users = [ur.user for ur in UserRole.objects.filter(role=event.required_role)]
                else:
                    eligible_users = list(users.values())
                
                for user in eligible_users[:2]:  # First 2 eligible users vote
                    DateVote.objects.get_or_create(
                        date_option=date_options[0],
                        user=user
                    )
            
            # Add participants
            eligible_users = []
            if event.required_role:
                eligible_users = [ur.user for ur in UserRole.objects.filter(role=event.required_role)]
            else:
                eligible_users = list(users.values())
            
            for user in eligible_users:
                EventParticipant.objects.get_or_create(
                    event=event,
                    user=user,
                    defaults={'status': 'going'}
                )
            
            # Add some requirements
            requirements_data = [
                {'type': 'food', 'title': 'Order Pizza', 'description': 'Order 3 large pizzas'},
                {'type': 'supplies', 'title': 'Get Drinks', 'description': 'Buy sodas and water'},
            ]
            
            for req_data in requirements_data:
                EventRequirement.objects.get_or_create(
                    event=event,
                    title=req_data['title'],
                    defaults={
                        'requirement_type': req_data['type'],
                        'description': req_data['description'],
                        'added_by': users[event_data['creator']],
                    }
                )
            
            # Add some comments
            EventComment.objects.get_or_create(
                event=event,
                user=users[event_data['creator']],
                defaults={'content': 'Looking forward to this event! Let me know if you have any suggestions.'}
            )
            
            created_events.append(event)
    
    # Finalize one event and create a bill for it
    if created_events:
        gaming_event = None
        for event in created_events:
            if event.title == 'Weekend Gaming Session':
                gaming_event = event
                break
        
        if gaming_event:
            # Finalize the date
            gaming_event.finalize_date()
            print(f"Finalized date for: {gaming_event.title}")
            
            # Create a bill for the gaming event
            bill, created = Bill.objects.get_or_create(
                event=gaming_event,
                title='Gaming Night Expenses',
                defaults={
                    'description': 'Pizza, drinks, and snacks for our gaming session',
                    'created_by': users['bob'],
                }
            )
            
            if created:
                print(f"Created bill: {bill.title}")
                
                # Add some expenses
                expenses_data = [
                    {
                        'description': 'Pizza (3 Large)',
                        'amount': 45.99,
                        'paid_by': 'bob',
                        'shared_by': ['alice', 'bob', 'charlie']  # Based on who has the Gaming Buddies role
                    },
                    {
                        'description': 'Drinks and Snacks',
                        'amount': 23.50,
                        'paid_by': 'alice',
                        'shared_by': ['alice', 'bob', 'charlie']
                    },
                    {
                        'description': 'Extra Controllers',
                        'amount': 15.99,
                        'paid_by': 'charlie',
                        'shared_by': ['bob', 'charlie']  # Only shared between these two
                    }
                ]
                
                for exp_data in expenses_data:
                    expense = Expense.objects.create(
                        bill=bill,
                        description=exp_data['description'],
                        amount=exp_data['amount'],
                        paid_by=users[exp_data['paid_by']]
                    )
                    
                    # Add shared_by users
                    for username in exp_data['shared_by']:
                        expense.shared_by.add(users[username])
                    
                    print(f"Added expense: {expense.description} - ${expense.amount}")
                
                # Recalculate bill total
                bill.calculate_total()
    
    print("\n" + "="*50)
    print("SAMPLE DATA CREATION COMPLETE!")
    print("="*50)
    print("\nTest Users Created (all with password 'password'):")
    for username in users.keys():
        print(f"  • {username}")
    
    print(f"\nEvents Created: {len(created_events)}")
    print("Roles and friendships have been set up.")
    print("One event has been finalized with expenses for testing bill splitting.")
    
    print("\nTo test the application:")
    print("1. Start the server: python manage.py runserver")
    print("2. Go to: http://127.0.0.1:8000/")
    print("3. Login with any of the usernames above (password: 'password')")
    print("4. Explore events, voting, bill splitting, and friend features!")

if __name__ == "__main__":
    create_sample_data()