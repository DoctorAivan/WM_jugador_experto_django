from rest_framework import serializers
from django.contrib.auth.models import User

from apps.api.models import (League,
                             Team,
                             Player,
                             Match,
                             Match_player)

#       #       #       #       #       #       #       #       #       #       #       #

# Sign Up Serializer
class SignUpSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField(required=False)
    password = serializers.CharField()
    year = serializers.CharField()
    month = serializers.CharField()
    day = serializers.CharField()
    team = serializers.CharField()

# Sign In Serializer
class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

# Sign Response Serializer
class SignResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    token = serializers.CharField()
    team = serializers.IntegerField()

# Sign Response Serializer
class SignBackendResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    name = serializers.CharField()
    token = serializers.CharField()

# Vote Serializer
class VoteSerializer(serializers.Serializer):
    match = serializers.IntegerField()
    player = serializers.IntegerField()

#       #       #       #       #       #       #       #       #       #       #       #

# Leagues Serializer
class LeaguesSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = ('id', 'name', 'description')
        read_only_fields = ('id',)

#       #       #       #       #       #       #       #       #       #       #       #

# Teams Serializer
class TeamsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name', 'code')
        read_only_fields = ('id',)

#       #       #       #       #       #       #       #       #       #       #       #

# Teams Serializer
class PlayersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'type', 'name', 'number')
        read_only_fields = ('id',)

#       #       #       #       #       #       #       #       #       #       #       #

# Matchs Serializer
class MatchsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ('id', 'status', 'archived', 'league', 'team_local', 'team_visit', 'date', 'time')
        read_only_fields = ('id',)

# Matchs Players Serializer
class MatchsPlayersSerializer(serializers.ModelSerializer):

    name = serializers.CharField(source='player.name', read_only=True)
    type = serializers.CharField(source='player.type', read_only=True)

    class Meta:
        model = Match_player
        fields = ('id','order', 'type','player','name', 'captain', 'number')

# Matchs Players Serializer
class MatchsPlayersUpdateSerializer(serializers.ModelSerializer):

    name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Match_player
        fields = ('name', 'number', 'captain')

    def update(self, instance, validated_data):
        instance.number = validated_data.get('number', instance.number)
        instance.captain = validated_data.get('captain', instance.captain)

        name = validated_data.get('name')
        if name:
            instance.player.name = name
            instance.player.save()

        instance.save()
        return instance

#       #       #       #       #       #       #       #       #       #       #       #

# User Serializer
class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'email', 'is_staff')
        read_only_fields = ('id','password',)

# Users List Serializer
class UsersListSerializer(serializers.ModelSerializer):

    type = serializers.CharField(source='account.type', read_only=True)
    verification = serializers.CharField(source='account.verification', read_only=True)
    points = serializers.CharField(source='account.points', read_only=True)
    birthday = serializers.CharField(source='account.birthday', read_only=True)
    team = serializers.CharField(source='account.team', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'type', 'verification', 'points', 'birthday', 'team')

#       #       #       #       #       #       #       #       #       #       #       #

# Winner Details
class WinnerDetailsSerializer(serializers.Serializer):
    month = serializers.CharField()
    year = serializers.IntegerField()

# Winner Choise
class WinnerChoiseSerializer(serializers.Serializer):
    user = serializers.IntegerField()
    month = serializers.CharField()
    year = serializers.IntegerField()