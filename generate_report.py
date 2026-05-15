import os

status = "Success"
message = "修正確認05:45"
# date 명령어 결과 뒤의 줄바꿈 문자를 깔끔하게 제거하기 위해 strip() 추가
date_info = os.popen('date').read().strip()

# CSS와 JavaScript 코드는 중괄호({})가 많아 f-string과 충돌하므로 별도의 문자열로 뺍니다.
game_style_and_script = """
<style>
    /* 전체 배경을 어둡게 처리하여 게임과 어울리게 설정 */
    body { font-family: sans-serif; text-align: center; padding-top: 20px; background-color: #1a1a1a; color: #f0f0f0; margin: 0; }
    hr { border: 1px solid #444; width: 80%; margin: 20px auto; }
    .report-section { background-color: #2a2a2a; padding: 20px; border-radius: 10px; display: inline-block; box-shadow: 0 4px 8px rgba(0,0,0,0.5); }
    #gameCanvas { background-color: #000; border: 2px solid #555; box-shadow: 0 0 15px rgba(0, 255, 255, 0.2); margin-top: 10px; }
</style>

<script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    
    let score = 0;
    let gameOver = false;
    
    const player = { x: canvas.width / 2 - 20, y: canvas.height - 40, width: 40, height: 30, speed: 5 };
    let bullets = [];
    let enemies = [];
    
    const enemyRows = 4;
    const enemyCols = 7;
    const enemyWidth = 30;
    const enemyHeight = 25;
    const enemyPadding = 15;
    let enemyDirection = 1;

    // 적군 초기화
    for (let c = 0; c < enemyCols; c++) {
        for (let r = 0; r < enemyRows; r++) {
            enemies.push({ 
                x: (c * (enemyWidth + enemyPadding)) + 35, 
                y: (r * (enemyHeight + enemyPadding)) + 30, 
                status: 1 
            });
        }
    }

    let rightPressed = false;
    let leftPressed = false;

    // 키보드 이벤트 리스너 (방향키, 스페이스바)
    document.addEventListener("keydown", (e) => {
        if (e.key === "Right" || e.key === "ArrowRight") rightPressed = true;
        else if (e.key === "Left" || e.key === "ArrowLeft") leftPressed = true;
        else if (e.key === " " || e.key === "Spacebar") {
            e.preventDefault(); // 스페이스바 스크롤 방지
            if (!gameOver) bullets.push({ x: player.x + player.width / 2 - 2, y: player.y, width: 4, height: 10 });
            else document.location.reload();
        }
    });

    document.addEventListener("keyup", (e) => {
        if (e.key === "Right" || e.key === "ArrowRight") rightPressed = false;
        else if (e.key === "Left" || e.key === "ArrowLeft") leftPressed = false;
    });

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        if (gameOver) {
            ctx.fillStyle = "white";
            ctx.font = "30px Arial";
            ctx.fillText("GAME OVER", canvas.width / 2 - 90, canvas.height / 2);
            ctx.font = "16px Arial";
            ctx.fillText("스페이스바를 눌러 재시작", canvas.width / 2 - 85, canvas.height / 2 + 30);
            return;
        }

        // 우주선 그리기
        ctx.fillStyle = "#00FFCC";
        ctx.beginPath();
        ctx.moveTo(player.x + player.width / 2, player.y);
        ctx.lineTo(player.x + player.width, player.y + player.height);
        ctx.lineTo(player.x, player.y + player.height);
        ctx.fill();

        // 미사일 그리기 및 이동
        ctx.fillStyle = "#FFDD00";
        for (let i = 0; i < bullets.length; i++) {
            let b = bullets[i];
            b.y -= 7;
            ctx.fillRect(b.x, b.y, b.width, b.height);
            if (b.y < 0) { bullets.splice(i, 1); i--; }
        }

        // 적군 그리기 및 이동
        ctx.fillStyle = "#FF3366";
        let hitEdge = false;
        enemies.forEach(e => {
            if (e.status === 1) {
                e.x += 1 * enemyDirection;
                if (e.x + enemyWidth > canvas.width || e.x < 0) hitEdge = true;
                ctx.fillRect(e.x, e.y, enemyWidth, enemyHeight);
            }
        });

        // 적군이 벽에 닿았을 때 아래로 이동
        if (hitEdge) {
            enemyDirection *= -1;
            enemies.forEach(e => {
                e.y += 15;
                if (e.status === 1 && e.y + enemyHeight >= player.y) gameOver = true;
            });
        }

        // 충돌 체크 (미사일 vs 적군)
        for (let i = 0; i < bullets.length; i++) {
            let b = bullets[i];
            for (let j = 0; j < enemies.length; j++) {
                let e = enemies[j];
                if (e.status === 1 && b.x > e.x && b.x < e.x + enemyWidth && b.y > e.y && b.y < e.y + enemyHeight) {
                    e.status = 0;
                    bullets.splice(i, 1);
                    i--;
                    score += 10;
                    break;
                }
            }
        }

        // 점수 표기
        ctx.fillStyle = "white";
        ctx.font = "16px Arial";
        ctx.fillText("Score: " + score, 8, 20);

        // 플레이어 이동
        if (rightPressed && player.x < canvas.width - player.width) player.x += player.speed;
        if (leftPressed && player.x > 0) player.x -= player.speed;

        requestAnimationFrame(draw);
    }
    
    draw();
</script>
"""

# f-string을 활용해 HTML 뼈대 안에 변수와 위에서 정의한 게임 스크립트를 삽입합니다.
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CI/CD Test & Galaga</title>
</head>
<body>
    <div class="report-section">
        <h1 style="margin-top: 0;">🛠️ CI/CD Test Report</h1>
        <p style="font-size: 20px;">Status: <strong style="color: #4CAF50;">{status}</strong></p>
        <p>{message}</p>
        <p style="font-size: 14px; color: #aaa;">last updated: {date_info}</p>
    </div>
    
    <hr>
    
    <div>
        <h2>🚀 대기 시간 갤러그 한 판!</h2>
        <p style="font-size: 14px; color: #ccc;">조작: [ ⬅️ / ➡️ ] 방향키로 이동 &nbsp;|&nbsp; [ Spacebar ] 미사일 발사</p>
        <canvas id="gameCanvas" width="400" height="450"></canvas>
    </div>

    <!-- 파이썬 변수에 저장해둔 CSS와 JS 코드 삽입 -->
    {game_style_and_script}
</body>
</html>"""

# 파일 쓰기
os.makedirs("public", exist_ok=True)
with open("public/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("성공적으로 public/index.html 파일이 생성되었습니다!")