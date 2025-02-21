from django.db.models import Count
from random import choice

from apps.api.task import Format
from apps.api.models import (Account, Winner, Vote)

#       #       #       #       #       #       #       #       #       #       #       #
# Match results

# Get winners month choise users
def winner_month_choise(month, year):

    # Get IDs of users who are already winners in the year
    winner_users = Winner.objects.filter(year=year).values_list('user_id', flat=True)

    # Filter votes by month and year, excluding winning users
    possible_winners = (
        Vote.objects.filter(
            match__date__month=month,
            match__date__year=year,
            user__account__type='D'
        )
        .exclude(user_id__in=winner_users)
        .values('user__id')
        .annotate(total_votes=Count('id'))
        .order_by('-total_votes')[:10]
    )

    # Validate possible winners lenght
    if len(possible_winners) > 0:

        # Choise winner user
        winner = choice(possible_winners)

        # Save winner user
        winner_new = Winner.objects.create(
            user_id=winner['user__id'],
            month=month,
            year=year
        )

        # Get account details
        account = Account.objects.get(user=winner['user__id'])

        # Create response
        response = {
            'exist' : True,
            'month' : month,
            'year' : year,
            'winner' : {
                'id' : account.user.id,
                'name' : account.user.first_name,
                'email' : account.user.email,
                'phone' : account.phone,
                'age' : Format.age(account.birthday),
                'joined' : Format.new_datetime(account.user.date_joined),
                'created' : Format.new_datetime(winner_new.created)
            }
        }

    else:

        response = {
            'exist' : False,
            'month' : month,
            'year' : year
        }

    return response