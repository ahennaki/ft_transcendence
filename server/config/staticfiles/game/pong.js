document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("pongCanvas");
    if (!canvas) {
        console.error("Canvas element not found in the DOM.");
        return;
    }
    console.log("Canvas element found in the DOM.");
    const ctx = canvas.getContext("2d");
    const score1Element = document.getElementById("score1");
    const score2Element = document.getElementById("score2");

    const paddleWidth = 10;
    const paddleHeight = 100;
    const ballRadius = 10;

    let paddle1 = { x: 0, y: (canvas.height - paddleHeight) / 2 };
    let paddle2 = { x: canvas.width - paddleWidth, y: (canvas.height - paddleHeight) / 2 };
    let ball = { x: canvas.width / 2, y: canvas.height / 2, dx: 5, dy: 5, radius: ballRadius };
    let score1 = 0;
    let score2 = 0;
    let playerNumber;
    let gameStarted = false;

    const roomName = JSON.parse(document.getElementById('room-name').textContent);

    // console.log("matchId: ", matchId);
    const socket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/game/'
        + roomName
        + '/'
    );

    socket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        console.log('Received data:', data);
        if (data.type === 'game_update') {
            ball = data.ball;
        } else if (data.type === 'score_update') {
            score1 = data.player1_score;
            score2 = data.player2_score;
            score1Element.textContent = score1;
            score2Element.textContent = score2;
        } else if (data.type === 'paddle_update') {
            paddle1 = data.paddle1;
            paddle2 = data.paddle2;
        } else if (data.type === 'player_number') {
            playerNumber = data.player_number;
            console.log('Assigned player number:', playerNumber);
        } else if (data.type === 'game_start') {
            gameStarted = true;
        }
    };

    socket.onopen = () => {
        console.log('WebSocket connection opened');
    };

    socket.onclose = () => {
        console.log('WebSocket connection closed');
    };

    function drawPaddle(paddle) {
        ctx.fillStyle = "#fff";
        ctx.fillRect(paddle.x, paddle.y, paddleWidth, paddleHeight);
    }
    
    function drawBall() {
        ctx.beginPath();
        ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
        ctx.fillStyle = "#fff";
        ctx.fill();
        ctx.closePath();
    }
    
    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        // console.log('start draw paddle1', paddle1);
        drawPaddle(paddle1);
        // console.log('end draw paddle1');
        console.log('start draw paddle2', paddle2);
        drawPaddle(paddle2);
        // console.log('end draw paddle2');
        drawBall();
        requestAnimationFrame(draw);
    }
    
    draw();
    
    document.addEventListener('keydown', function(event) {
        // console.log("player is ", playerNumber)
        if (playerNumber === 1 || playerNumber === 2) {
            const action = { type: 'move_paddle', y: 0 };
            if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {
                let paddleToUpdate = playerNumber === 1 ? paddle1 : paddle2;
                
                if (event.key === 'ArrowUp') {
                    action.y = Math.max(0, paddleToUpdate.y - 10);
                } else if (event.key === 'ArrowDown') {
                    action.y = Math.min(canvas.height - paddleHeight, paddleToUpdate.y + 10);
                }
                // console.log(`after paddle${playerNumber} keymove:`, paddleToUpdate);
                // console.log(`after keymove action:`, action);
                // console.log('paddle${playerNumber} value ', paddleToUpdate);

                socket.send(JSON.stringify(action));
            }
        }
    });
    
    canvas.addEventListener('mousemove', function(event) {
            if (playerNumber === 1 || playerNumber === 2) {
                    const action = {
                            type: 'move_paddle',
                y: Math.max(0, Math.min(canvas.height - paddleHeight, event.clientY - canvas.offsetTop - paddleHeight / 2))
            };
            // console.log(`Sending paddle${playerNumber} mousemove:`, action);
            // console.log('Sending paddle move action:', action);
            socket.send(JSON.stringify(action));
        }
    });
});
