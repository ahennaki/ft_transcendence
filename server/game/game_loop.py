import asyncio
import time
from channels.db                import database_sync_to_async
from authentication.utils       import print_red, print_green, print_yellow
from .game_end                  import end_game
from .helpers                   import reinitialize_data

async def game_loop(consumer):
    await reinitialize_data(consumer)
    while consumer.isGaming:
        update_ball_position(consumer)
        # print_yellow(f'ball: {consumer.ball}')

        data = {"type": "game_update", "ball": consumer.ball}

        await consumer.channel_layer.group_send(
            f"user_{consumer.player1_username}",
            {"type": "game_update", "data": data}
        )
        await consumer.channel_layer.group_send(
            f"user_{consumer.player2_username}",
            {"type": "game_update", "data": data}
        )

        elapsed_time = time.time() - consumer.start_time
        if elapsed_time > 10:
            increase_ball_speed(consumer)
            consumer.start_time = time.time()

        await asyncio.sleep(0.020)

def update_ball_position(consumer):
    consumer.ball["x"] += consumer.ball["dx"]
    consumer.ball["y"] += consumer.ball["dy"]

    if consumer.ball["y"] <= consumer.ball["rd"] or consumer.ball["y"] >= consumer.canvas["h"] - consumer.ball["rd"]:
        consumer.ball["dy"] = -consumer.ball["dy"]

    if consumer.ball["x"] <= consumer.paddle2["x"] + consumer.ball["rd"]:
        if consumer.paddle2["y"] <= consumer.ball["y"] <= consumer.paddle2["y"] + consumer.paddleHeight:
            consumer.ball["x"] = consumer.paddle2["x"] + consumer.ball["rd"]
            consumer.ball["dx"] = -consumer.ball["dx"] if abs(consumer.ball["dx"]) > 0.5 else 3
            
            hit_pos = (consumer.ball["y"] - consumer.paddle2["y"]) / consumer.paddleHeight
            consumer.ball["dy"] = (hit_pos - 0.5) * 10
            if abs(consumer.ball["dy"]) < 1:
                consumer.ball["dy"] = 3 if consumer.ball["dy"] > 0 else -3

    if consumer.ball["x"] >= consumer.paddle1["x"] - consumer.ball["rd"]:
        if consumer.paddle1["y"] <= consumer.ball["y"] <= consumer.paddle1["y"] + consumer.paddleHeight:
            consumer.ball["x"] = consumer.paddle1["x"] - consumer.ball["rd"]
            consumer.ball["dx"] = -consumer.ball["dx"] if abs(consumer.ball["dx"]) > 0.5 else -3

            hit_pos = (consumer.ball["y"] - consumer.paddle1["y"]) / consumer.paddleHeight
            consumer.ball["dy"] = (hit_pos - 0.5) * 10
            if abs(consumer.ball["dx"]) < 1:
                consumer.ball["dx"] = 3 if consumer.ball["dx"] > 0 else -3

    if consumer.ball["x"] <= 0:
        player1_scores(consumer)

    if consumer.ball["x"] >= consumer.canvas["w"]:
        player2_scores(consumer)

def player1_scores(consumer):
    consumer.score1 += 1
    reset_ball(consumer)
    asyncio.create_task(send_score_update(consumer))

def player2_scores(consumer):
    consumer.score2 += 1
    reset_ball(consumer)
    asyncio.create_task(send_score_update(consumer))

def reset_ball(consumer):
    consumer.ball["x"] = consumer.canvas["w"] / 2
    consumer.ball["y"] = consumer.canvas["h"] / 2
    consumer.ball["dx"] = -consumer.ball["dx"]
    consumer.ball["dy"] = 5

def increase_ball_speed(consumer):
    if consumer.ball["dx"] > 0:
        consumer.ball["dx"] += 0.5
    else:
        consumer.ball["dx"] -= 0.5
    if consumer.ball["dy"] > 0:
        consumer.ball["dy"] += 0.5
    else:
        consumer.ball["dy"] -= 0.5

async def send_score_update(consumer):
    score_update = {
        "type": "score_update",
        "player1_score": consumer.score1,
        "player2_score": consumer.score2
    }

    # print_yellow(f'send score1: {consumer.score1}')
    # print_yellow(f'send score2: {consumer.score2}')

    if consumer.isGaming:
        await consumer.channel_layer.group_send(
            f"user_{consumer.player1_username}",
            {"type": "score_update", "data": score_update}
        )
        await consumer.channel_layer.group_send(
            f"user_{consumer.player2_username}",
            {"type": "score_update", "data": score_update}
        )
