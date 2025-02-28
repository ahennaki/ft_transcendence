# Generated by Django 5.0.7 on 2024-11-02 09:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('prfl', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InviteQueue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invite_id', models.IntegerField()),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='prfl.profile')),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player1_score', models.IntegerField(default=0)),
                ('player2_score', models.IntegerField(default=0)),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='waiting', max_length=20)),
                ('player1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player1', to='prfl.profile')),
                ('player2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player2', to='prfl.profile')),
            ],
        ),
        migrations.CreateModel(
            name='MatchHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('winner_score', models.IntegerField()),
                ('loser_score', models.IntegerField()),
                ('ended_at', models.DateTimeField(auto_now_add=True)),
                ('loser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loser', to='prfl.profile')),
                ('match', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='matchHistory', to='game.match')),
                ('winner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='winner', to='prfl.profile')),
            ],
        ),
        migrations.CreateModel(
            name='PlayerQueue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='prfl.profile')),
            ],
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mapname', models.CharField(default='default', max_length=100)),
                ('ballcolor', models.CharField(default='green', max_length=100)),
                ('score', models.CharField(default='Five', max_length=100)),
                ('botlevel', models.FloatField(default=0.1)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='settings', to='prfl.profile')),
            ],
        ),
    ]
