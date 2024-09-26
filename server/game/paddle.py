async def move_paddle(consumer, data):
    y = data['y']

    if data["player_number"] == 1:
        consumer.paddle1["y"] = y
        await broadcast_paddle_positions(consumer, consumer.paddle1, 1)
    elif data["player_number"] == 2:
        consumer.paddle2["y"] = y
        await broadcast_paddle_positions(consumer, consumer.paddle2, 2)

async def update_paddle(consumer, data):
    y = data['y']
    if data["player_number"] == 1:
        consumer.paddle1["y"] = y
    elif data["player_number"] == 2:
        consumer.paddle2["y"] = y

async def broadcast_paddle_positions(consumer, paddle, nb):
    data = {"type": "paddle_update", "y": paddle["y"], "player_number": nb}

    if nb == 2 and consumer.isGaming:
        await consumer.channel_layer.group_send(
            f"user_{consumer.player1_username}",
            {"type": "paddle_update", "data": data}
        )
    elif nb == 1 and consumer.isGaming:
        await consumer.channel_layer.group_send(
            f"user_{consumer.player2_username}",
            {"type": "paddle_update", "data": data}
        )
