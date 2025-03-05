from django.urls import path, include
from rest_framework.routers import SimpleRouter

from apps.api.views import (CreateOwner,
                            SignUpView,
                            SignInView,
                            SignInBackendView,
                            VoteView,
                            UserHistory,
                            LeagueTeamsView,
                            LeagueWithTeamsView,
                            TeamPlayersView,
                            TeamPlayersDetailsView,
                            TeamPlayerClearView,
                            MatchListView,
                            MatchListBrandedView,
                            MatchActionsView,
                            MatchStatusView,
                            MatchSortListView,
                            MatchArchivedtView,
                            MatchArchivedUpdateView,
                            MatchUpdateListView,
                            MatchSettingsView,
                            MatchResultsView,
                            MatchSchemeView,
                            MatchPlayersView,
                            MatchPlayersActionsView,

                            UpdateSequencerView,

                            WinnerMonthsView,
                            WinnerDetailsView,
                            WinnerChoiseView,
                            WinnerEmptyView,
                            WinnerAnnulateView,
                            
                            UsersDownloadViewSet,
                            UsersListViewSet,
                            UserEditViewSet,
                            LeaguesViewSet,
                            TeamsViewSet,
                            
                            JsonMatchs,
                            JsonMatchsDetails,
                            JsonMatchsResults)

router = SimpleRouter(trailing_slash=False)
#router.register('users', UserstViewSet, basename='users')
#router.register(r'data', DataSampleViewSet, basename='data')
#router.register(r'players', PlayersViewSet, basename='players')
router.register(r'leagues', LeaguesViewSet, basename='leagues')
router.register(r'teams', TeamsViewSet, basename='teams')

urlpatterns = [

    path('', include(router.urls)),

    #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   
    # ADMINISTRATOR

    # Update sequencers
    path('update-sequencers', UpdateSequencerView.as_view(), name='update-sequencers'),

    # Leagues teams
    path('leagues-teams/<int:pk>', LeagueTeamsView.as_view(), name='league-teams'),
    path('leagues-with-teams', LeagueWithTeamsView.as_view(), name='leagues-with-teams'),

    # Teams
    path('teams-details/<int:pk>', TeamPlayersView.as_view(), name='team-details'),

    # Teams players
    path('teams-players/<int:pk>', TeamPlayersView.as_view(), name='team-players'),
    path('teams-players-clear/<int:pk>', TeamPlayerClearView.as_view(), name='team-players-clear'),
    path('teams-players-details/<int:pk>', TeamPlayersDetailsView.as_view(), name='team-players-details'),

    # Matchs archived
    path('matchs-archived/<int:page>', MatchArchivedtView.as_view(), name='match-archived'),

    # Matchs branded
    path('matchs-branded/<int:page>', MatchListBrandedView.as_view(), name='matchs-branded'),

    # Matchs actions
    path('matchs-list', MatchListView.as_view(), name='matchs'),
    path('matchs-sort', MatchSortListView.as_view(), name='match-sort'),
    path('matchs-update', MatchUpdateListView.as_view(), name='match-update'),
    path('matchs/<int:pk>/actions', MatchActionsView.as_view(), name='match-actions'),
    path('matchs/<int:pk>/status', MatchStatusView.as_view(), name='match-status'),
    path('matchs/<int:pk>/settings', MatchSettingsView.as_view(), name='match-settings'),
    path('matchs/<int:pk>/results', MatchResultsView.as_view(), name='match-results'),
    path('matchs/<int:pk>/scheme', MatchSchemeView.as_view(), name='match-scheme'),
    path('matchs/<int:pk>/archived', MatchArchivedUpdateView.as_view(), name='match-archived-set'),
    path('matchs/<int:pk>/players', MatchPlayersView.as_view(), name='match-players'),
    path('matchs/<int:pk>/players/<int:player>', MatchPlayersActionsView.as_view(), name='match-players'),

    # Users actions
    path('users-list/<int:page>', UsersListViewSet.as_view(), name='users-list'),
    path('users-branded-resourses/<str:token>-<int:month>-<int:year>', UsersDownloadViewSet.as_view(), name='users-branded-resourses'),
    path('users/<int:pk>/edit', UserEditViewSet.as_view(), name='user-edit'),

    # Winners actions
    path('winners-months', WinnerMonthsView.as_view(), name='winner-months'),
    path('winners-details', WinnerDetailsView.as_view(), name='winner-details'),
    path('winners-choise', WinnerChoiseView.as_view(), name='winner-choise'),
    path('winners-annulate', WinnerAnnulateView.as_view(), name='winner-annulate'),

    #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   
    # VISITORS

    # Sign account
    path('create-owner', CreateOwner.as_view(), name='create-owner'),
    path('sign-up', SignUpView.as_view(), name='sign-up'),
    path('sign-in', SignInView.as_view(), name='sign-in'),
    path('sign-in-backend', SignInBackendView.as_view(), name='signin-backend'),

    # Vote
    path('vote', VoteView.as_view(), name='vote'),

    # User History
    path('user-history/<int:page>', UserHistory.as_view(), name='user-history'),

    # Match
    path('match-list', JsonMatchs.as_view(), name='json-matchs'),
    path('match-election/<int:pk>', JsonMatchsDetails.as_view(), name='api-match-election'),
    path('match-results/<int:pk>', JsonMatchsResults.as_view(), name='api-match-results'),

]
