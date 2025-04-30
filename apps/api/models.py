from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models

#       #       #       #       #       #       #       #       #       #       #       #

class Winner(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='winner')
    month = models.IntegerField(default=0)
    year = models.IntegerField(default=0)
    created = models.DateTimeField(default=timezone.now)

class Account(models.Model):
    users_types = (
        ('A', 'Admin'),
        ('B', 'Staff'),
        ('C', 'Branded'),
        ('D', 'Users'),
        ('E', 'Switch')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='account')
    type = models.CharField(max_length=1, choices=users_types, default='D')
    verification = models.BooleanField(default=False)
    points = models.IntegerField(default=100)
    birthday = models.DateField()
    team = models.IntegerField(default=0)
    phone = models.CharField(max_length=64, blank=True, default='')

#       #       #       #       #       #       #       #       #       #       #       #

class Player(models.Model):
    player_types = (
        ('A', 'Goalkeepers'),
        ('B', 'Defenders'),
        ('C', 'Midfielders'),
        ('D', 'Forwards')
    )

    status = models.BooleanField(default=True)
    type = models.CharField(max_length=1, choices=player_types, default='M')
    name = models.CharField(max_length=64)
    fullname = models.CharField(max_length=64, default='', null=False, blank=False)
    number = models.IntegerField(default=10)

    class Meta:
        ordering = ['type','number']

    def __str__(self):
        return self.name

#       #       #       #       #       #       #       #       #       #       #       #

class Team(models.Model):
    status = models.BooleanField(default=True)
    name = models.CharField(max_length=32)
    code = models.CharField(max_length=6)
    players = models.ManyToManyField(Player, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

#       #       #       #       #       #       #       #       #       #       #       #

class League(models.Model):
    status = models.BooleanField(default=True)
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=140)
    teams = models.ManyToManyField(Team, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name

#       #       #       #       #       #       #       #       #       #       #       #

class Match(models.Model):
    status = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    scheme = models.BooleanField(default=False)
    order = models.IntegerField(default=-1)
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="matchs")
    team_local = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team_local")
    team_visit = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team_visit")
    date = models.DateField()
    time = models.TimeField()
    manual_votes = models.BooleanField(default=False, null=False, blank=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.order} : {self.team_local.name} - {self.team_visit.name}"

#       #       #       #       #       #       #       #       #       #       #       #

class Match_player(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, db_index=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, db_index=True)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, db_index=True)
    order = models.IntegerField(default=0)
    captain = models.BooleanField(default=False)
    number = models.IntegerField(default=0)
    manual_votes = models.IntegerField(default=0, null=False, blank=False )

    class Meta:
        ordering = ['order']
        constraints = [models.UniqueConstraint(fields=['match', 'team', 'player'], name='unique_match_team_player')]

#       #       #       #       #       #       #       #       #       #       #       #

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes', db_index=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='votes', db_index=True)
    match_player = models.ForeignKey(Match_player, on_delete=models.CASCADE, related_name='votes', db_index=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'match'], name='unique_vote_per_user_match')]
