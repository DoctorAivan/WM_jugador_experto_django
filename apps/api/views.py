from django.db import connection
from django.core.cache import cache
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils.timezone import now
from django.http import HttpResponse

from core.permissions import Admin, Staff, Branded, Authenticated, Visitors

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework import views, status

from apps.api.task import Format
from apps.api.models import (Account,
                             League,
                             Team,
                             Player,
                             Match,
                             Match_player,
                             Vote,
                             Winner)

from apps.api.serializers import (SignUpSerializer,
                                  SignInSerializer,
                                  VoteSerializer,
                                  UsersSerializer,
                                  SignResponseSerializer,
                                  SignBackendResponseSerializer,
                                  ProfileSerializer,
                                  LeaguesSerializer,
                                  TeamsSerializer,
                                  PlayersSerializer,
                                  MatchsSerializer,
                                  MatchsPlayersSerializer,
                                  MatchsPlayersUpdateSerializer,
                                  WinnerDetailsSerializer)

from apps.api.results import (results_match_list,
                              results_match,
                              results_match_votes,
                              results_match_archive,
                              result_all_match_list,
                              user_vote_history,
                              results_users_download,
                              result_users_list,
                              results_match_archived_list,
                              results_votes_per_day,
                              results_most_voted_matchs,
                              results_most_voted_teams,
                              results_most_voted_players)

from apps.api.winners import (winner_month_choise)

# Index 200
def index(request):
    return HttpResponse('.')

#       #       #       #       #       #       #       #       #       #       #       #
# Sequencers
#       #       #       #       #       #       #       #       #       #       #       #

# Update ID sequencers
class UpdateSequencerView(views.APIView):

    def get(self, request):

        # Update ID in sequencer
        reset_sequence('api_league')
        reset_sequence('api_team')
        reset_sequence('api_player')

        return Response('Sequencer Updated', status=status.HTTP_200_OK)

# Reset sequencer ID
def reset_sequence(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT MAX(id) FROM {table_name}")
        max_id = cursor.fetchone()[0] or 1
        cursor.execute(f"ALTER SEQUENCE {table_name}_id_seq RESTART WITH {max_id + 1}")

#       #       #       #       #       #       #       #       #       #       #       #
# API View
#       #       #       #       #       #       #       #       #       #       #       #

# Create Owner Admin User
class CreateOwner(views.APIView):
    permission_classes = [Visitors]

    def get(self, request):

        # Update user data
        user = User.objects.get(pk=1)
        user.is_staff = True
        user.save()

        # Update account data
        account = Account.objects.get(user=user)
        account.type = 'A'
        account.verification = True
        account.save()

        return Response('created', status=status.HTTP_200_OK)

#       #       #       #       #       #       #       #       #       #       #       #

# Sign Up Action
class SignUpView(views.APIView):
    permission_classes = [Visitors]

    def post(self, request):

        # Serializer validation
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get validated data
        name = serializer.validated_data['name']
        username = serializer.validated_data['email']
        email = serializer.validated_data['email']
        phone = request.data['phone']
        password = serializer.validated_data['password']
        year = serializer.validated_data['year']
        month = serializer.validated_data['month']
        day = serializer.validated_data['day']
        team = serializer.validated_data['team']

        # Create birthday
        birthday = f"{year}-{month}-{day}"

        # Query Authentication
        if User.objects.filter(username=email).exists():

            # Create json response
            response = { 'error' : 'El correo ingresado ya esta registrado' }

            # Send response
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        
        else:

            # Create user data
            user = User.objects.create_user(
                first_name = name,
                username = username,
                email = email,
                password = password
            )

            # Create account data
            account = Account.objects.create(
                user = user,
                birthday = birthday,
                phone = phone,
                team = team
            )

            # Generate token for authentication
            token, _ = Token.objects.get_or_create(user=user)

            # Create json response
            response = {
                'id': user.id,
                'name': user.first_name,
                'team': account.team,
                'token': token
            }

        return Response(SignResponseSerializer(response).data , status=status.HTTP_200_OK)

# Sign In Action
class SignInView(views.APIView):
    permission_classes = [Visitors]

    def post(self, request):

        # Serializer validation
        serializer = SignInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get validated data
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        # Query Authentication
        user = authenticate(request, username=email, password=password)

        # Query Authentication
        if user is not None:
            
            login(request, user)

            # Get account data
            account = Account.objects.get(user=user)

            # Get token
            token = Token.objects.get(user=user)

            # Create json response
            response = {
                'id': user.id,
                'name': user.first_name,
                'team': account.team,
                'token': token
            }

            # Send response
            return Response(SignResponseSerializer(response).data, status=status.HTTP_200_OK)

        else:

            # Create json response
            response = { 'error' : 'User not found' }

            # Send response
            return Response(response, status=status.HTTP_403_FORBIDDEN)

# Sign In Backend Action
class SignInBackendView(views.APIView):
    permission_classes = [Visitors]

    def post(self, request):

        # Serializer validation
        serializer = SignInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get validated data
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        # Query Authentication
        user = authenticate(request, username=email, password=password)

        # Query Authentication
        if user is not None:
            
            # Persist a user id and a backend in the request
            login(request, user)

            # Get account data
            account = Account.objects.get(user=user)

            # Validate account type
            if account.type != 'D':

                # Delete token
                Token.objects.filter(user=user).delete()

                # Create new token
                token = Token.objects.create(user=user)

                # Create json response
                response = {
                    'id': user.id,
                    'name': user.first_name,
                    'type': account.type,
                    'token': token.key
                }

                # Send response
                return Response(SignBackendResponseSerializer(response).data, status=status.HTTP_200_OK)

            else:

                # Send response
                return Response(status=status.HTTP_403_FORBIDDEN)

        else:

            # Send response
            return Response(status=status.HTTP_403_FORBIDDEN)

#       #       #       #       #       #       #       #       #       #       #       #

# Vote Action
class VoteView(views.APIView):
    permission_classes = [Authenticated]

    def post(self, request):
        try:

            # Serializer validation
            serializer = VoteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            # Create instances
            user = request.user
            match = data['match']
            player = data['player']

            # Validate emited vote
            if Vote.objects.filter(user=user, match=match).exists():
                return Response('ready', status=status.HTTP_200_OK)

            # Create instances
            match = Match.objects.get(pk=match)
            player = Match_player.objects.get(pk=player)

            # Create vote
            Vote.objects.create(
                user = user,
                match = match,
                match_player = player
            )

            # Send response
            return Response('voted', status=status.HTTP_200_OK)
        
        except:
            return Response('error', status=status.HTTP_400_BAD_REQUEST)

#       #       #       #       #       #       #       #       #       #       #       #

# User History
class UserHistory(views.APIView):
    permission_classes = [Authenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, page):
        try:

            # Create instances
            user = request.user

            # Get user history vote
            response = user_vote_history(user.id, page)
            return Response( response , status = status.HTTP_200_OK)

        except:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

# Profile edit
class UserProfileView(views.APIView):
    permission_classes = [Authenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        try:

            # Create instances
            user = request.user

            # Get account data
            account = Account.objects.get(user=user)

            # Create response
            response = {
                'name' : user.first_name,
                'email' : user.email,
                'phone' : account.phone,
                'year' : account.birthday.year,
                'month' : account.birthday.month,
                'day' : account.birthday.day,
                'team' : account.team,
            }

            return Response(response, status = status.HTTP_200_OK)
        except:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
                
            # Create instances
            user = request.user

            # Get account data
            account = Account.objects.get(user=user)

            # Get token
            token = Token.objects.get(user=user)

            # Serializer validation
            serializer = ProfileSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Get validated data
            name = serializer.validated_data['name']
            username = serializer.validated_data['email']
            email = serializer.validated_data['email']
            phone = request.data['phone']
            year = serializer.validated_data['year']
            month = serializer.validated_data['month']
            day = serializer.validated_data['day']
            team = serializer.validated_data['team']

            # Create birthday
            birthday = f"{year}-{month}-{day}"

            # Save user
            user.first_name = name
            user.username = username
            user.email = email
            user.save()

            # Save Account
            account.birthday = birthday
            account.phone = phone
            account.team = team
            account.save()

            # Create json response
            response = {
                'id': user.id,
                'name': name,
                'team': account.team,
                'token': token.key
            }

            return Response(response, status = status.HTTP_200_OK)
        except:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

#       #       #       #       #       #       #       #       #       #       #       #

# Get Match List
class JsonMatchs(APIView):

    def get(self, request):
        try:

            # Get cache data
            response = cache.get("matchs_list")

            # Validate cache data
            if response is not None:
                return Response( response , status = status.HTTP_200_OK)

            # Set cache data
            response = results_match_list()
            return Response( response , status = status.HTTP_200_OK)

        except:
            return Response([], status=status.HTTP_400_BAD_REQUEST)

# Get Match Details
class JsonMatchsDetails(APIView):

    def get(self, request, pk):
        try:

            # Get cache data
            response = cache.get(f"match_{pk}")

            # Validate cache data
            if response is not None:
                return Response( response , status = status.HTTP_200_OK)

            # Set cache data
            response = results_match(pk)
            return Response( response , status = status.HTTP_200_OK)

        except:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

# Get Match Results
class JsonMatchsResults(APIView):

    def get(self, request, pk):
        try:

            # Get cache data
            response = cache.get(f"match_results_{pk}")

            # Validate cache data
            if response is not None:
                return Response( response , status = status.HTTP_200_OK)

            # Set cache data
            response = results_match_votes(pk)
            return Response( response , status = status.HTTP_200_OK)

        except:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

#       #       #       #       #       #       #       #       #       #       #       #

# League list with teams
class LeagueWithTeamsView(views.APIView):
    permission_classes = [Staff]

    # Get team list
    def get(self, request):
        try:

            leagues = League.objects.all()

            response = []

            for league in leagues:
                teams = league.teams.all()

                response.append({
                    'id' : league.id,
                    'name' : league.name,
                    'teams' : TeamsSerializer(teams, many=True).data
                })


            return Response(response , status=status.HTTP_200_OK)
        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

# League Teams
class LeagueTeamsView(views.APIView):
    permission_classes = [Staff]

    # Get team list
    def get(self, request, pk):
        try:

            # Get list
            response = self.list(pk)
            return Response(response , status=status.HTTP_200_OK)

        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

    # Add team list
    def post(self, request, pk):
        try:

            # Get league data
            league = League.objects.get(pk=pk)

            # Add Teams list
            for team in request.data['teams']:
                league.teams.add(team)

            # Get list
            response = self.list(pk)
            return Response(response , status=status.HTTP_200_OK)
        
        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

    # Delete team list
    def delete(self, request, pk):
        try:

            # Get league data
            league = League.objects.get(pk=pk)

            # Remove Teams list
            for team in request.data['teams']:
                league.teams.remove(team)

            # Get list
            response = self.list(pk)
            return Response(response, status=status.HTTP_200_OK)

        except:
            return Response('error', status=status.HTTP_400_BAD_REQUEST)

    # Create team list
    def list(self, pk):

        # Get league data
        league = League.objects.get(pk=pk)

        # Team List
        teams = []

        # Create team list
        for team in league.teams.all():
            teams.append({
                'id' : team.id,
                'name' : team.name,
                'code' : team.code
            })

        return teams

#       #       #       #       #       #       #       #       #       #       #       #

# Team Players
class TeamPlayersView(views.APIView):
    permission_classes = [Staff]

    # Get player list
    def get(self, request, pk):
        try:

            # Get list
            response = self.list(pk)
            return Response(response , status=status.HTTP_200_OK)

        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

    # Add player list
    def post(self, request, pk):
        try:

            # Get team data
            team = Team.objects.get(pk=pk)

            # Get player list
            players_add = request.data.get('players', None)

            # Validate player list
            if not players_add or not isinstance(players_add, list):
                return Response({"error": "El arreglo 'players' es requerido y debe ser una lista."}, status=status.HTTP_400_BAD_REQUEST)

            # Add Teams list
            for player in players_add:
                try:
                    team.players.add(player)
                except:
                    pass

            # Get list
            response = self.list(pk)
            return Response(response , status=status.HTTP_200_OK)

        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

    # Delete player list
    def delete(self, request, pk):
        try:

            # Get team data
            team = Team.objects.get(pk=pk)

            # Remove player from list
            for player in request.data['players']:
                try:
                    team.players.remove(player)
                except:
                    pass

            # Get list
            response = self.list(pk)
            return Response(response, status=status.HTTP_200_OK)
        
        except:
            return Response('error', status=status.HTTP_400_BAD_REQUEST)

    # Create player list
    def list(self, pk):
        
        # Get player list
        team = Team.objects.prefetch_related('players').get(pk=pk)
        players = team.players.all()

        # Create player list
        serializer = PlayersSerializer(players, many=True)

        # Create response
        response = {
            'team' : TeamsSerializer(team).data,
            'players' : serializer.data
        }

        return response

# Team Players Details
class TeamPlayersDetailsView(views.APIView):
    permission_classes = [Staff]

    # Get player data
    def get(self, request, pk):
        try:

            player = Player.objects.get(pk=pk)

            response = {
                'id' : player.id,
                'type' : player.type,
                'number' : player.number,
                'name' : player.name,
            }

            return Response(response , status=status.HTTP_200_OK)

        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

    # Update player data
    def put(self, request, pk):
        try:

            # Get player data
            data = request.data

            # Get and set new data
            player = Player.objects.get(pk=pk)
            player.type = data['type']
            player.number = data['number']
            player.name = data['name']
            player.save()

            response = {
                'id' : player.id,
                'type' : player.type,
                'number' : player.number,
                'name' : player.name,
            }

            return Response(response , status=status.HTTP_200_OK)

        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

    # Create player
    def post(self, request, pk):
        try:

            # Get player data
            data = request.data

            # Get team data
            team = Team.objects.get(pk=data['team'])

            # Create player
            player = Player.objects.create(
                type = data['type'],
                number = data['number'],
                name = data['name']
            )

            # Add player to team
            team.players.add(player)

            return Response('ok' , status=status.HTTP_200_OK)

        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

    # Delete player
    def delete(self, request, pk):
        try:

            # Get player data
            data = request.data

            # Get team data
            team = Team.objects.get(pk=data['team'])

            # Remove player to team
            team.players.remove(data['player'])

            # Delete player
            player = Player.objects.get(pk=data['player'])
            player.delete()

            return Response('ok' , status=status.HTTP_200_OK)

        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

# Team Players Clear
class TeamPlayerClearView(views.APIView):
    permission_classes = [Staff]

    def get(self, reques, pk):

        team = Team.objects.prefetch_related('players').get(pk=pk)
        team.players.clear()

        return Response('clear team' , status=status.HTTP_200_OK)

#       #       #       #       #       #       #       #       #       #       #       #

# Users download list
class UsersDownloadViewSet(views.APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request, token, month, year):

        # Validate token
        if token:
            user = self.authenticate_token(token)
            if not user:
                return Response(status=status.HTTP_404_NOT_FOUND)

        # Download all users list
        return results_users_download(month,year)

    # Validate request permissions
    def authenticate_token(self, token):
        try:

            # Get instances
            token = Token.objects.get(key=token)
            account = Account.objects.get(user=token.user)

            # Validate account type
            if account.type == 'A' or account.type == 'C':
                return token.user
            else:
                return None

        except Token.DoesNotExist:
            return None

# Users List
class UsersListViewSet(views.APIView):
    permission_classes = [Branded]

    def get(self, request, page):

        # Create instances
        response = result_users_list(page)

        # Send response
        return Response(response, status=status.HTTP_200_OK)

# Users Edit
class UserEditViewSet(views.APIView):
    permission_classes = [Admin]

    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            account = Account.objects.get(user=user)
            
            response = {
                'id' : user.id,
                'staff' : user.is_staff,
                'email' : user.email,
                'verification' : account.verification,
                'type' : account.type,
                'birthday' : account.birthday,
                'phone' : account.phone,
                'name' : user.first_name,
            }

            return Response(response , status=status.HTTP_200_OK)

        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:

            # Get data
            data = request.data

            # Update user data
            user = User.objects.get(pk=pk)
            user.first_name = data['name']
            user.email = data['email']
            user.is_staff = data['staff']
            user.save()

            # Update account data
            account = Account.objects.get(user=user)
            account.type = data['type']
            account.verification = data['verification']
            account.save()

            return Response('update' , status=status.HTTP_200_OK)
        
        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

#       #       #       #       #       #       #       #       #       #       #       #

# Matchs list
class MatchListView(views.APIView):
    permission_classes = [Staff]

    def get(self, request):

        matchs_list = []

        for match in Match.objects.filter(archived=False).order_by('order'):
            matchs_list.append({
                'id' : match.id,
                'order' : match.order,
                'scheme' : match.scheme,
                'status' : match.status,
                'date' : Format.new_date(match.date),
                'time' : Format.new_time(match.time),
                'league' : LeaguesSerializer(match.league).data,
                'team_local' : TeamsSerializer(match.team_local).data,
                'team_visit' : TeamsSerializer(match.team_visit).data
            })

        return Response(matchs_list , status=status.HTTP_200_OK)

# Matchs list branded
class MatchListBrandedView(views.APIView):
    permission_classes = [Branded]

    def get(self, request, page):

        response = result_all_match_list(page)

        return Response(response , status=status.HTTP_200_OK)

# Matchs Actions
class MatchActionsView(views.APIView):
    permission_classes = [Staff]

    def get(self, request, pk):

        # Get all leagues
        leagues = League.objects.all()
        leagues_data = []

        # Add league to list
        for league in leagues:
            leagues_data.append({
                'id' : league.id,
                'name' : league.name
            })

        # Get match details
        match = get_object_or_404(Match, pk=pk)

        # Create match object
        match_data = {
            'id' : match.id,
            'date' : match.date,
            'time' : match.time,
            'league' : match.league.id,
            'team_local' : TeamsSerializer(match.team_local).data,
            'team_visit' : TeamsSerializer(match.team_visit).data
        }

        # Create json response
        response = {
            'leagues' : leagues_data,
            'match' : match_data
        }

        return Response(response , status=status.HTTP_200_OK)

    def post(self, request, pk):
        try:

            # Get request data
            data = request.data

            # Create match data
            league = League.objects.get(pk=data['league'])
            team_local = Team.objects.get(pk=data['team_local'])
            team_visit = Team.objects.get(pk=data['team_visit'])
            date = data['date']
            time = data['time']

            # Create match
            match = Match.objects.create(
                league = league,
                team_local = team_local,
                team_visit = team_visit,
                date = date,
                time = time
            )

            return Response( MatchsSerializer(match).data , status=status.HTTP_200_OK)

        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:

            date = request.data['date']
            time = request.data['time']

            match = Match.objects.get(pk=pk)
            match.date = date
            match.time = time
            match.save()

            results_match(pk)

            return Response( MatchsSerializer(match).data , status=status.HTTP_200_OK)
        
        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            match = Match.objects.get(pk=pk)
            match.delete()

            return Response('ok', status=status.HTTP_200_OK)
        
        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

# Match Status
class MatchStatusView(views.APIView):
    permission_classes = [Staff]

    # Update match status
    def put(self, request, pk):
        try:

            # Get match status
            match_status = request.data['status']

            # Get match data
            match = Match.objects.get(pk=pk)
            match.status = match_status
            match.save()

            return Response('update' , status=status.HTTP_200_OK)
        
        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

# Match Sort List
class MatchSortListView(views.APIView):
    permission_classes = [Staff]

    # Update match order
    def put(self, request):
        try:
            order = 0
            for id in request.data['matchs']:
                match = Match.objects.get(pk=id)
                match.order = order
                match.save()

                order += 1

            return Response('sorted' , status=status.HTTP_200_OK)
        
        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

# Match archived update
class MatchArchivedUpdateView(views.APIView):
    permission_classes = [Staff]

    # Update match archived
    def post(self, request, pk):

        # Get match archived status
        archived = request.data['archived']

        # Get match data
        match = Match.objects.get(pk=pk)
        match.status = False
        match.archived = archived
        match.save()

        # Validate status
        if archived == True:
            results_match_archive(pk)
        else:
            results_match(pk)

        return Response('archived' , status=status.HTTP_200_OK)

# Match Update List
class MatchUpdateListView(views.APIView):
    permission_classes = [Staff]

    # Update match archived
    def post(self, request):
        try:

            # Get matchs list
            matchs = request.data['matchs']

            # Create match list json file
            results_match_list(matchs)

            return Response('ok' , status=status.HTTP_200_OK)

        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

# Match archived list
class MatchArchivedtView(views.APIView):
    permission_classes = [Staff]

    def get(self, request, page):

        # Create match list
        matchs_list = results_match_archived_list(10, page)

        return Response(matchs_list , status=status.HTTP_200_OK)

# Match Settings
class MatchSettingsView(views.APIView):
    permission_classes = [Staff]

    # Get player list
    def get(self, request, pk):
        try:
            # Get list
            response = self.list(pk)
            return Response(response , status=status.HTTP_200_OK)
        
        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

    # Create player list
    def list(self, pk):

        # Get match data
        match = Match.objects.get(pk=pk)

        # Get team squads
        team_local_squad = match.team_local.players.all()
        team_visit_squad = match.team_visit.players.all()

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

        players = {
            'league' : LeaguesSerializer(match.league).data,
            'match' : {
                'id' : match.id,
                'date' : match.date,
                'time' : match.time,
                'local' : {
                    'id' : match.team_local.id,
                    'name' : match.team_local.name,
                    'code' : match.team_local.code,
                    'squad' : PlayersSerializer(team_local_squad, many=True).data,
                    'players' : players_local
                },
                'visit' : {
                    'id' : match.team_visit.id,
                    'name' : match.team_visit.name,
                    'code' : match.team_visit.code,
                    'squad' : PlayersSerializer(team_visit_squad, many=True).data,
                    'players' : players_visit
                }
            }
        }

        return players

# Match Results
class MatchResultsView(views.APIView):
    permission_classes = [Branded]

    def get(self, request, pk):

        # Create match json file
        response = results_match_votes(pk)
        return Response( response , status = status.HTTP_200_OK)

# Match Save Scheme
class MatchSchemeView(views.APIView):
    permission_classes = [Staff]

    # Update match archived
    def post(self, request, pk):
        
        # Create match json file
        results_match(pk)

        return Response('ok' , status=status.HTTP_200_OK)

# Match Players
class MatchPlayersView(views.APIView):
    permission_classes = [Staff]

    # Get player list
    def get(self, request, pk):
        try:

            # Get list
            response = self.list(pk)
            return Response(response , status=status.HTTP_200_OK)
        
        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

    # Add player list
    def post(self, request, pk):
        try:

            # Get match data
            match = Match.objects.get(pk=pk)
            team = Team.objects.get(pk=request.data['team'])

            # Get player data
            player = Player.objects.get(pk=request.data['player'])

            # Get new order
            player_count = Match_player.objects.filter( match = match,team = team ).count()

            # Create player
            match_player = Match_player.objects.create(
                match = match,
                team = team,
                player = player,
                number = player.number,
                order = player_count + 1
            )

            # Create response
            response = MatchsPlayersSerializer(match_player).data
            return Response(response , status=status.HTTP_200_OK)
        
        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

    # Update order list
    def put(self, request, pk):

        # Get player list
        player_order = request.data.get('players', None)

        # Validate player list
        if not player_order or not isinstance(player_order, list):
            return Response({"error": "El arreglo 'players' es requerido y debe ser una lista."}, status=status.HTTP_400_BAD_REQUEST)

        # Order player list
        for order, id in enumerate(player_order):
            try:
                match_player = Match_player.objects.get(pk=id)
                match_player.order = order
                match_player.save()
            except:
                pass

        return Response('ok' , status=status.HTTP_200_OK)

    # Delete player list
    def delete(self, request, pk):
        try:

            # Get player list
            player = request.data['player']

            # Remove player from match
            player_delete = Match_player.objects.get(pk=player)
            player_respose = player_delete
            player_delete.delete()

            response = MatchsPlayersSerializer(player_respose).data
            return Response(response, status=status.HTTP_200_OK)
        
        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

    # Delete player list
    def delete_res(self, request, pk):
        try:
            # Get team
            team = request.data['team']

            # Get player list
            players = request.data['players']

            # Remove player from match
            objects_to_delete = Match_player.objects.filter(
                match = pk,
                team = team,
                player__in = [i for i in players]
            )
            objects_to_delete.delete()

            # Get list
            response = self.list(pk)
            return Response(response, status=status.HTTP_200_OK)
        
        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

    # Create player list
    def list(self, pk):

        # Get match data
        match = Match.objects.get(pk=pk)

        # Player List
        players_local = []
        players_visit = []

        # Create team list
        for player in match.match_player_set.all().order_by('order'):

            # Create player
            player_data = MatchsPlayersSerializer(player).data

            # Assign team
            if player.team.id == match.team_local.id:
                players_local.append(player_data)
            else:
                players_visit.append(player_data)

        players = {
            'league' : LeaguesSerializer(match.league).data,
            'match' : {
                'id' : match.id,
                'date' : match.date,
                'time' : match.time,
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

        return players

# Match Players Actions
class MatchPlayersActionsView(views.APIView):
    permission_classes = [Staff]

    # Get player
    def get(self, request, pk, player):

        # Valid match player exist
        match_player = get_object_or_404(Match_player, pk=player)

        # Response
        response = MatchsPlayersSerializer(match_player)
        return Response(response.data, status=status.HTTP_200_OK)

    # Update player
    def put(self, request, pk, player):

        # Valid match player exist
        match_player = get_object_or_404(Match_player, pk=player)

        # Update data
        serializer = MatchsPlayersUpdateSerializer(match_player, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Response
        response = MatchsPlayersSerializer(match_player)
        return Response(response.data, status=status.HTTP_200_OK)

#       #       #       #       #       #       #       #       #       #       #       #

# Winner Months
class WinnerMonthsView(views.APIView):
    permission_classes = [Branded]

    def get(self, request):

        try:

            winners = Winner.objects.all()

            winners_list = []

            for winner in winners:
                winners_list.append({
                    'month' : winner.month
                })

            return Response(winners_list , status=status.HTTP_200_OK)

        except:

            return Response([], status=status.HTTP_200_OK)

# Winner Details
class WinnerDetailsView(views.APIView):
    permission_classes = [Branded]

    def post(self, request):
        try:

            # Serializer validation
            serializer = WinnerDetailsSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Get validated data
            month = serializer.validated_data['month']
            year = serializer.validated_data['year']

            # Get winner details
            winner = Winner.objects.get(month=month,year=year)
            account = Account.objects.get(user=winner.user)

            # Create response
            response = {
                'exist' : True,
                'month' : month,
                'year' : year,
                'winner' : {
                    'id' : winner.user.id,
                    'name' : winner.user.first_name,
                    'email' : winner.user.email,
                    'phone' : account.phone,
                    'age' : Format.age(account.birthday),
                    'joined' : Format.new_datetime(winner.user.date_joined),
                    'created' : Format.new_datetime(winner.created)
                }
            }

            return Response(response , status=status.HTTP_200_OK)

        except:

            response = {
                'exist' : False,
                'month' : month,
                'year' : year
            }

            return Response(response, status=status.HTTP_200_OK)

# Winner Choise
class WinnerChoiseView(views.APIView):
    permission_classes = [Branded]

    def post(self, request):

        # Serializer validation
        serializer = WinnerDetailsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get validated data
        month = serializer.validated_data['month']
        year = serializer.validated_data['year']

        # Return list of possible winners
        users = winner_month_choise(month, year)

        return Response(users, status=status.HTTP_200_OK)

# Winner Empty
class WinnerEmptyView(views.APIView):
    #permission_classes = [Admin]

    def get(self, request):

        winners = Winner.objects.all()

        for winner in winners:
            winner.delete()

        return Response('delete', status=status.HTTP_200_OK)

# Winner Annulate
class WinnerAnnulateView(views.APIView):
    permission_classes = [Admin]

    def post(self, request):

        try:

            # Serializer validation
            serializer = WinnerDetailsSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Get validated data
            month = serializer.validated_data['month']
            year = serializer.validated_data['year']

            # Annulate winner
            winner = Winner.objects.get(month=month,year=year)
            winner.delete()

            return Response('annulated', status=status.HTTP_200_OK)
        
        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

#       #       #       #       #       #       #       #       #       #       #       #

# Statistics
class StatisticsView(views.APIView):
    permission_classes = [Staff]

    def get(self, request):

        # Get cache data
        response = cache.get(f"statistics")

        # Validate cache data
        if response is not None:
            return Response( response , status = status.HTTP_200_OK)
        else:

            # Limit of results
            limit = 5

            # Filter Settings
            current_date = now()
            year = current_date.year
            month = current_date.month
            month_name = Format.month_name(month)
            previous_month = month - 1 if month > 1 else 12
            previous_month_name = Format.month_name(previous_month)
            previous_year = year if month > 1 else year - 1

            # Create results list
            result = {
                'days' : results_votes_per_day(month, previous_month, year, previous_year),
                'matchs' : results_most_voted_matchs(limit, month, previous_month, year, previous_year),
                'teams' : results_most_voted_teams(limit, month, previous_month, year, previous_year),
                'players' : results_most_voted_players(limit, month, previous_month, year, previous_year),
                'title' : {
                    'month' : month_name,
                    'previous_month' : previous_month_name,
                    'year' : year,
                    'previous_year' : previous_year
                }
            }

            # ID for cache
            cache_key = "statistics"

            # Refresh cache indefinitely
            cache.set(cache_key, result, timeout=20)

            # Create response
            return Response( result , status = status.HTTP_200_OK)

#       #       #       #       #       #       #       #       #       #       #       #
#       #       #       #       #       #       #       #       #       #       #       #

# Leagues ViewSet [REVISION]
class LeaguesViewSet(viewsets.ModelViewSet):
    permission_classes = [Staff]
    serializer_class = LeaguesSerializer
    queryset = League.objects.all()

    # Add teams
    @action(methods=["get"], detail=True, url_path="teams")
    def teams_list(self, request, pk):
        try:
            # Get league data
            league = League.objects.get(pk=pk)

            # Team List
            teams = []

            for team in league.teams.all().order_by('name'):
                teams.append({
                    'id' : team.id,
                    'name' : team.name,
                    'code' : team.code
                })

            return Response(teams , status=status.HTTP_200_OK)
        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

    # Add teams
    @action(methods=["post"], detail=True, url_path="teams-add")
    def teams_add(self, request, pk):
        try:
            # Get league data
            league = League.objects.get(pk=pk)

            # Add Teams list
            for team in request.data['teams']:
                league.teams.add(team)

            return Response('ok' , status=status.HTTP_200_OK)
        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

    # Remove teams
    @action(methods=["delete"], detail=True, url_path="teams-remove")
    def teams_delete(self, request, pk):
        try:
            # Get league data
            league = League.objects.get(pk=pk)

            # Remove Teams list
            for team in request.data['teams']:
                league.teams.remove(team)

            return Response('ok' , status=status.HTTP_200_OK)
        except:
            return Response('error' , status=status.HTTP_400_BAD_REQUEST)

#       #       #       #       #       #       #       #       #       #       #       #
# Model View Set
#       #       #       #       #       #       #       #       #       #       #       #

# Teams ViewSet
class TeamsViewSet(viewsets.ModelViewSet):
    permission_classes = [Staff]
    serializer_class = TeamsSerializer
    queryset = Team.objects.all()

#       #       #       #       #       #       #       #       #       #       #       #

# Players ViewSet
class PlayersViewSet(viewsets.ModelViewSet):
    permission_classes = [Staff]
    serializer_class = PlayersSerializer
    queryset = Player.objects.all()

#       #       #       #       #       #       #       #       #       #       #       #

# User List
class UserstViewSet(viewsets.ModelViewSet):
    permission_classes = [Admin]
    serializer_class = UsersSerializer
    queryset = User.objects.all()

#       #       #       #       #       #       #       #       #       #       #       #
