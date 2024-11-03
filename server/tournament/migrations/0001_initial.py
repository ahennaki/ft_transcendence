# Generated by Django 5.0.7 on 2024-11-02 09:44

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('prfl', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('status', models.CharField(choices=[('upcoming', 'Upcoming'), ('ongoing', 'Ongoing'), ('completed', 'Completed')], default='upcoming', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tournaments_created', to='prfl.profile')),
            ],
        ),
        migrations.CreateModel(
            name='TournamentMatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('round_number', models.IntegerField(choices=[(1, 'Quarterfinal'), (2, 'Semifinal'), (3, 'Final')])),
                ('number_player', models.IntegerField(default=2)),
                ('completed', models.BooleanField(default=False)),
                ('interupted', models.BooleanField(default=False)),
                ('score_player1', models.IntegerField(default=0)),
                ('score_player2', models.IntegerField(default=0)),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches', to='tournament.tournament')),
            ],
        ),
        migrations.CreateModel(
            name='TournamentParticipant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.CharField(max_length=255)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('isDisconnect', models.BooleanField(default=False)),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='tournament.tournament')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tournaments_participated', to='prfl.profile')),
            ],
            options={
                'unique_together': {('tournament', 'user', 'alias')},
            },
        ),
        migrations.CreateModel(
            name='TournamentMatchHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('winner_score', models.IntegerField()),
                ('loser_score', models.IntegerField()),
                ('ended_at', models.DateTimeField(auto_now_add=True)),
                ('tournamentMatch', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tournamentMatchHistory', to='tournament.tournamentmatch')),
                ('loser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tournamentLoser', to='tournament.tournamentparticipant')),
                ('winner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tournamentWinner', to='tournament.tournamentparticipant')),
            ],
        ),
        migrations.AddField(
            model_name='tournamentmatch',
            name='player1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='matches_as_player1', to='tournament.tournamentparticipant'),
        ),
        migrations.AddField(
            model_name='tournamentmatch',
            name='player2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='matches_as_player2', to='tournament.tournamentparticipant'),
        ),
        migrations.AddField(
            model_name='tournamentmatch',
            name='winner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='matches_won', to='tournament.tournamentparticipant'),
        ),
    ]
