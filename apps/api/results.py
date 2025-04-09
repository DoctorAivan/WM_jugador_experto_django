import csv
from django.conf import settings
from django.http import HttpResponse

from django.conf import settings
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import TruncDate
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage

from apps.api.task import Format
from apps.api.models import (Account, Match, Vote)
from apps.api.serializers import (MatchsPlayersSerializer,
                                  LeaguesSerializer,
                                  TeamsSerializer)

#       #       #       #       #       #       #       #       #       #       #       #
# Match results

# Create match election
def results_match(id):

    # Get match data
    match = Match.objects.get(pk=id)

    # Player List
    players_local = []
    players_visit = []

    # Create team list
    for player in match.match_player_set.all():

        # Create player
        player_data = MatchsPlayersSerializer(player).data

        # Assign team
        if player.team.id == match.team_local.id:
            players_local.append(player_data)
        else:
            players_visit.append(player_data)

    # Validate minimun players in scheme
    if len(players_local) > settings.MIN_SCHEME and len(players_visit) > settings.MIN_SCHEME:
        match.scheme = True
    else:
        match.scheme = False
    match.save()

    # Create json structure
    match = {
        'league' : LeaguesSerializer(match.league).data,
        'match' : {
            'id' : match.id,
            'status' : match.status,
            'date' : Format.new_date(match.date),
            'time' : Format.new_time(match.time),
            'date_digits' : match.date,
            'local' : {
                'id' : match.team_local.id,
                'name' : match.team_local.name,
                'code' : match.team_local.code,
                'players' : players_local
            },
            'visit' : {
                'id' : match.team_visit.id,
                'name' : match.team_visit.name,
                'code' : match.team_visit.code,
                'players' : players_visit
            }
        }
    }

    # ID for cache
    cache_key = f"match_{id}"

    # Refresh cache indefinitely
    cache.set(cache_key, match, timeout=None)
    return match

# Create match results
def results_match_votes(id):

    # Get match data
    match = Match.objects.get(pk=id)

    # Get match votes results
    results = match_top_three_players(id)

    # Create json structure
    match = {
        'league' : LeaguesSerializer(match.league).data,
        'match' : {
            'id' : match.id,
            'status' : match.status,
            'date' : Format.new_date(match.date),
            'time' : Format.new_time(match.time),
            'date_digits' : match.date,
            'local' : {
                'id' : match.team_local.id,
                'name' : match.team_local.name,
                'code' : match.team_local.code
            },
            'visit' : {
                'id' : match.team_visit.id,
                'name' : match.team_visit.name,
                'code' : match.team_visit.code
            },
            'results' : {
                'list' : results['list'],
                'total' : results['total'],
            }
        }
    }

    # ID for cache
    cache_key = f"match_results_{id}"

    # Refresh cache indefinitely
    cache.set(cache_key, match, timeout=10)
    return match

#       #       #       #       #       #       #       #       #       #       #       #

# Delete match from cache
def results_match_archive(id):

    # ID for cache
    cache_key = f"match_{id}"

    # Get match cache
    match_cache = cache.get(cache_key)

    # Validate if cache exist
    if match_cache is not None:
        cache.delete(cache_key)

# Create match list json file
def results_match_list(matchs=[]):

    # Validate match ID list
    if len(matchs) == 0:

        # Get active match list
        active_matchs = Match.objects.filter(status=True, archived=False)
        matchs = [match.id for match in active_matchs]

    # Create match list to json file
    matchs_list = []

    # Iterate match Save orden and add to list
    for order, id in enumerate(matchs):

        # Get match and save order
        match = Match.objects.get(pk=id)
        match.order = order
        match.save()

        # Create match object
        matchs_list.append({
            'id' : match.id,
            'order' : match.order,
            'date' : Format.new_date(match.date),
            'time' : Format.new_time(match.time),
            'league' : LeaguesSerializer(match.league).data,
            'local' : TeamsSerializer(match.team_local).data,
            'visit' : TeamsSerializer(match.team_visit).data
        })

    # ID for cache
    cache_key = "matchs_list"

    # Refresh cache indefinitely
    cache.set(cache_key, matchs_list, timeout=None)
    return matchs_list

#       #       #       #       #       #       #       #       #       #       #       #

# Get match top three voted players
def match_top_three_players(id):

    # Set results list
    limit = 5

    # Create query
    match_votes = (
        Vote.objects.filter(match_id=id)
        .values(
            player_id=F('match_player__player__id'),
            player_name=F('match_player__player__name'),
            team_name=F('match_player__team__name'),
            team_code=F('match_player__team__code')
        )
        .annotate(
            votes=Count('id')
        )
        .order_by('-votes')[:limit]
    )

    # Count all votes in match
    total_votes = Vote.objects.filter(match_id=id).count()
    #total_votes = sum(item['votes'] for item in match_votes)

    # Create response and percentages
    players = [
        {
            'name': player['player_name'],
            'team' : {
                'code': player['team_code'],
                'name': player['team_name'],
            },
            'votes': player['votes'],
            'percentage': Format.persentage(player['votes'], total_votes)
        }
        for player in match_votes
    ]

    response = {
        'total' : total_votes,
        'list' : players
    }

    return response

# Get all user's list
def result_all_match_list(page=1):

    # Set results list
    list_results = 12

    # Query to obtain the user's voting history
    matchs = (
        Match.objects.all().values(
            'id',
            'league__id',
            'league__name',
            'team_local__id',
            'team_local__name',
            'team_local__code',
            'team_visit__id',
            'team_visit__name',
            'team_visit__code',
            'date',
            'time',
        )
        .order_by('-date','-time')
    )

    # Create a pager with results per page
    paginator = Paginator(matchs, list_results)

    try:
        # Get the requested page
        paginated_votes = paginator.page(page)

    except EmptyPage:
        # If the requested page is out of range, return an empty page
        paginated_votes = []

    # Create a structured list for history
    matchs_list = [
        {
            'id' : match['id'],
            'date' : Format.new_date(match['date']),
            'time' : Format.new_time(match['time']),
            'league' : {
                'id' : match['league__id'],
                'name' : match['league__name']
            },
            'team_local' : {
                'id' : match['team_local__id'],
                'name' : match['team_local__name'],
                'code' : match['team_local__code']
            },
            'team_visit' : {
                'id' : match['team_visit__id'],
                'name' : match['team_visit__name'],
                'code' : match['team_visit__code']
            }
        }
        for match in paginated_votes
    ]

    return {
        'matchs': matchs_list,
        'page': page,
        'pages': paginator.num_pages
    }

#       #       #       #       #       #       #       #       #       #       #       #
# User results

# Get user profile votes history
def user_vote_history(user_id, page=1):

    # Set results list
    list_results = 10

    # Amount of points per game
    matchs_points = 3

    # Count the total votes cast by the user
    matchs_voted = Vote.objects.filter(user_id=user_id).count()

    # Query to obtain the user's voting history
    votes = (
        Vote.objects.filter(user_id=user_id)
        .select_related(
            'match',
            'match_player__player',
            'match_player__team'
        ).values(
            'id',
            'match__id',
            'match__date',
            'match__time',
            'match__league__id',
            'match__league__name',
            'match__team_local__name',
            'match__team_local__code',
            'match__team_visit__name',
            'match__team_visit__code',
            'match_player__player__name',
            'match_player__team__name'
        )
        .order_by('-id')
    )

    # Create a pager with 10 results per page
    paginator = Paginator(votes, list_results)

    try:
        # Get the requested page
        paginated_votes = paginator.page(page)

    except EmptyPage:
        # If the requested page is out of range, return an empty page
        paginated_votes = []

    # Create a structured list for history
    matches = [
        {
            'id': vote['match__id'],
            'date' : Format.new_date(vote['match__date']),
            'time' : Format.new_time(vote['match__time']),
            'league': {
                'id': vote['match__league__id'],
                'name': vote['match__league__name']
            },
            'local': {
                'code': vote['match__team_local__code'],
                'name': vote['match__team_local__name']
            },
            'visit': {
                'code': vote['match__team_visit__code'],
                'name': vote['match__team_visit__name']
            },
            'voted': {
                'name': vote['match_player__player__name'],
                'team': vote['match_player__team__name'],
            },
        }
        for vote in paginated_votes
    ]

    history = {
        'votes': matchs_voted,
        'points': Format.number(matchs_voted * matchs_points),
        'page': page,
        'pages': paginator.num_pages,
        'matches': matches
    }

    # ID for cache
    #cache_key = f"history_{user_id}"

    # Refresh cache indefinitely
    #cache.set(cache_key, history, timeout=15)

    return history

#       #       #       #       #       #       #       #       #       #       #       #
# User results

# Download all user's
def results_users_download(month, year):

    # Query to obtain all user's register
    accounts = (
        Account.objects.filter(
            user__date_joined__month=month,
            user__date_joined__year=year,
            type='D'
        )
        .select_related(
            'user'
        ).values(
            'id',
            'verification',
            'birthday',
            'phone',
            'user__id',
            'user__first_name',
            'user__email',
        ).annotate(
            votes=Count('user__votes')
        ).order_by('user__date_joined')
    )

    # Create a structured list
    accounts_list = [
        {
            'id': account['user__id'],
            'name': account['user__first_name'],
            'email': account['user__email'],
            'verification': account['verification'],
            'phone': account['phone'],
            'birthday': account['birthday'],
            'age': f"{Format.age(account['birthday'])} años",
            'votes': account['votes'],
        }
        for account in accounts
    ]

    # Create file name
    filename = Format.file_name('Accounts','csv')

    # Create HTTP Response
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )

    # Create CSV File
    writer = csv.writer(response)
    writer.writerow(['ID', 'NAME', 'EMAIL' ,'VERIFICATION', 'PHONE', 'BIRTHDAY', 'AGE', 'VOTES'])
    for row in accounts_list:
        writer.writerow(row.values())

    return response

# Get all user's list
def result_users_list(page=1):

    # Totals only in first page
    if page == 1:

        # Count the total votes cast by the user
        accounts_total = Account.objects.all().count()
        accounts_verificated_total = Account.objects.filter(verification=True).count()
        accounts_not_verificated_total = accounts_total - accounts_verificated_total

        matchs_total = Match.objects.all().count()
        votes_total = Vote.objects.all().count()

    # Set results list
    list_results = 10

    # Query to obtain the user's voting history
    accounts = (
        Account.objects.all()
        .select_related(
            'user',
        ).values(
            'id',
            'type',
            'verification',
            'birthday',
            'user__id',
            'user__first_name'
        )
        .order_by('-user__date_joined')
    )

    # Create a pager with results per page
    paginator = Paginator(accounts, list_results)

    try:
        # Get the requested page
        paginated_votes = paginator.page(page)

    except EmptyPage:
        # If the requested page is out of range, return an empty page
        paginated_votes = []

    # Create a structured list for history
    accounts_list = [
        {
            'id': account['user__id'],
            'type': account['type'],
            'status': account['verification'],
            'name': account['user__first_name'],
            'age': Format.age(account['birthday']),
        }
        for account in paginated_votes
    ]

    # Response
    if page == 1:
        return {
            'totals' : {
                'accounts' : Format.number(accounts_total),
                'verificated' : Format.number(accounts_verificated_total),
                'verificated_p' : Format.persentage(accounts_verificated_total, accounts_total),
                'not_verificated' : Format.number(accounts_not_verificated_total),
                'not_verificated_p' : Format.persentage(accounts_not_verificated_total, accounts_total),
                'matches' : Format.number(matchs_total),
                'votes' : Format.number(votes_total)
            },
            'accounts': accounts_list,
            'page': page,
            'pages': paginator.num_pages
        }
    else:
        return {
            'accounts': accounts_list,
            'page': page,
            'pages': paginator.num_pages
        }

#       #       #       #       #       #       #       #       #       #       #       #
# Matchs Archived

# Get user profile votes history
def results_match_archived_list(limit, page=1):

    # Count the total votes cast by the user
    matchs_total = Match.objects.filter(archived=True).count()

    # Set results list
    list_results = limit

    # Query to obtain the user's voting history
    matchs = (
        Match.objects.filter(archived=True)
        .values(
            'id',
            'league__id',
            'league__name',
            'team_local__id',
            'team_local__name',
            'team_local__code',
            'team_visit__id',
            'team_visit__name',
            'team_visit__code',
            'date',
            'time'
        )
        .order_by('-date','-time')
    )

    # Create a pager with results per page
    paginator = Paginator(matchs, list_results)

    try:
        # Get the requested page
        paginated_votes = paginator.page(page)

    except EmptyPage:
        # If the requested page is out of range, return an empty page
        paginated_votes = []

    # Create a structured list for history
    matchs_list = [
        {
            'id' : match['id'],
            'date' : Format.new_date(match['date']),
            'time' : Format.new_time(match['time']),
            'league' : {
                'id' : match['league__id'],
                'name' : match['league__name']
            },
            'team_local' : {
                'id' : match['team_local__id'],
                'name' : match['team_local__name'],
                'code' : match['team_local__code']
            },
            'team_visit' : {
                'id' : match['team_visit__id'],
                'name' : match['team_visit__name'],
                'code' : match['team_visit__code']
            }
        }
        for match in paginated_votes
    ]

    return {
        'totals': matchs_total,
        'matchs': matchs_list,
        'page': page,
        'pages': paginator.num_pages
    }

#       #       #       #       #       #       #       #       #       #       #       #

# Get votes per day
def results_votes_per_day(month, previous_month, year, previous_year):

    # Filtrar los votos por el mes y año especificado
    votes_by_day = (
        Vote.objects.filter(
            Q(match__date__year=year, match__date__month=month) |
            Q(match__date__year=previous_year, match__date__month=previous_month)
        )
        .annotate(day=TruncDate('match__date'))
        .values('day')
        .annotate(votes=Count('id'))
        .order_by('day')
    )

    # List
    series = []
    titles = []

    # Add data to list
    for vote in votes_by_day:
        series.append(vote['votes'])
        titles.append(Format.new_date(vote['day']))

    return {
        'series' : series,
        'titles' : titles
    }

# Get most voted matchs
def results_most_voted_matchs(limit, month, previous_month, year, previous_year):
    
    # Filter votes within the specific month and year
    match_votes = (
        Vote.objects.filter(
            Q(match__date__year=year, match__date__month=month)
        )
        .values(
            match_name=F('match__league__name'),
            league_code=F('match__league__description'),
            team_local_name=F('match__team_local__name'),
            team_local_code=F('match__team_local__code'),
            team_visit_name=F('match__team_visit__name'),
            team_visit_code=F('match__team_visit__code'),
            match_date=F('match__date'),
            match_time=F('match__time')
        )
        .annotate(total_votes=Count('id'))
        .order_by('-total_votes')
    )

    # Calculate the total votes for the month
    total_votes_month = match_votes.aggregate(total=Sum('total_votes'))['total'] or 1

    # Build response with percentages
    top_matches = [
        {
            'league': {
                'name': match['match_name'],
                'code': match['league_code']
            },
            'local': {
                'name': match['team_local_name'],
                'code': match['team_local_code']
            },
            'visit': {
                'name': match['team_visit_name'],
                'code': match['team_visit_code']
            },
            'date' : Format.new_date(match['match_date']),
            'time' : Format.new_time(match['match_time']),
            'votes': Format.number(match['total_votes']),
            'percentage': f"{(match['total_votes'] / total_votes_month) * 100:.1f}%"
        }
        for match in match_votes[:limit]
    ]

    return {
        "total": total_votes_month,
        "data": top_matches
    }

# Get most voted teams
def results_most_voted_teams(limit, month, previous_month, year, previous_year):
    
    # Count the total votes in the specified month and year
    total_votes = Vote.objects.filter(match__date__month=month, match__date__year=year).count()

    # Avoid division by zero
    if total_votes == 0:
        return {"total_votes": 0, "teams": []}

    # Q(match__date__year=previous_year, match__date__month=previous_month)

    # Get the teams with the most votes
    top_teams = (
        Vote.objects.filter(
            Q(match__date__year=year, match__date__month=month)
        )
        .values(
            team_id=F('match_player__team__id'),
            team_name=F('match_player__team__name'),
            team_code=F('match_player__team__code')
        )
        .annotate(total_votes=Count('id'))
        .order_by('-total_votes')[:limit]
    )

    # Format the data by adding the percentage
    teams_list = [
        {
            "team_id": team["team_id"],
            "team_name": team["team_name"],
            "team_code": team["team_code"],
            "votes": Format.number(team["total_votes"]),
            "percentage": f"{(team['total_votes'] / total_votes) * 100:.1f}%"
        }
        for team in top_teams
    ]

    return {
        "total": total_votes,
        "data": teams_list
    }

# Get most voted players
def results_most_voted_players(limit, month, previous_month, year, previous_year):

    # Count the total votes in the specified month and year
    total_votes = Vote.objects.filter(match__date__month=month, match__date__year=year).count()

    # Avoid division by zero
    if total_votes == 0:
        return {"total_votes": 0, "players": []}

    # Get the players with the most votes
    top_players = (
        Vote.objects.filter(
            Q(match__date__year=year, match__date__month=month)
        )
        .values(
            player_id=F('match_player__player__id'),
            player_name=F('match_player__player__name'),
            team_name=F('match_player__team__name'),
            team_code=F('match_player__team__code')
        )
        .annotate(total_votes=Count('id'))
        .order_by('-total_votes')[:limit]
    )

    # Format the data by adding the percentage
    players_list = [
        {
            "player_id": player["player_id"],
            "player_name": player["player_name"],
            "team": {
                "name": player["team_name"],
                "code": player["team_code"]
            },
            "votes": Format.number(player["total_votes"]),
            "percentage": f"{(player['total_votes'] / total_votes) * 100:.1f}%"
        }
        for player in top_players
    ]

    return {
        "total": total_votes,
        "data": players_list
    }