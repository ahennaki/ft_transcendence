from .game_end		            import end_game
from authentication.utils       import print_red, print_green, print_yellow
import asyncio
import time

async def initialize_data(consumer):
    consumer.paddle1 = {"y": 190, "x": 685}
    consumer.paddle2 = {"y": 190, "x": 15}
    consumer.paddleHeight = 70
    consumer.ball = {"x": 350, "y": 225, "dx": 5, "dy": 5, "rd": 10}
    consumer.canvas = {"w": 700, "h": 450}
    consumer.score1 = 0
    consumer.score2 = 0
    consumer.player1_username = None
    consumer.player2_username = None
    consumer.match = None
    consumer.match_id = None
    consumer.player_number = None
    consumer.isGaming = False
    consumer.isTournament = False
    consumer.tournament_id = None

async def score_update(consumer, data):
    consumer.score1 = data["player1_score"]
    consumer.score2 = data["player2_score"]

    if consumer.score1 >= 10 or consumer.score2 >= 10:
        consumer.isGaming = False
        if consumer.score1 > consumer.score2 and consumer.user.username == consumer.player1_username:
            await end_game(consumer, False)
        elif consumer.score2 > consumer.score1 and consumer.user.username == consumer.player2_username:
            await end_game(consumer, False)
