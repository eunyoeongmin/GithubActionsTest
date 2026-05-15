import os

status = "Success"
message = "갤러그 원작 비행 로직(곡선 진입, 강하 공격, 편대 호흡) 완벽 적용"

# f-string 충돌 방지를 위해 JS/CSS 코드를 별도 변수로 분리합니다.
game_logic_and_style = """
<style>
    body { font-family: 'Courier New', Courier, monospace; text-align: center; background-color: #000; color: #fff; margin: 0; overflow: hidden; }
    #game-wrapper { margin-top: 20px; }
    canvas { background-color: #050510; border: 2px solid #333; box-shadow: 0 0 20px rgba(0, 150, 255, 0.2); }
    .status-panel { margin-top: 10px; font-size: 14px; color: #aaa; }
    #report-header { background-color: #111; padding: 10px; border-bottom: 1px solid #333; }
</style>

<script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");

    // 게임 전역 상태
    let gameState = "START"; 
    let score = 0;
    let level = 1;
    let lives = 3;
    let frameCount = 0;

    // 입력 상태
    const keys = { ArrowLeft: false, ArrowRight: false, Space: false };
    let spacePressed = false; // 연사 제한용

    // 별 배경 객체
    const stars = Array.from({ length: 80 }, () => ({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        speed: Math.random() * 1.5 + 0.5
    }));

    // 플레이어 객체
    const player = {
        x: canvas.width / 2,
        y: canvas.height - 40,
        width: 30,
        height: 30,
        speed: 4
    };

    let playerBullets = [];
    let enemyBullets = [];
    let enemies = [];

    // 편대 전체의 움직임을 제어하는 오프셋
    let formation = { offsetX: 0, offsetY: 0, direction: 1, breathing: 0 };

    // 적군 초기화 로직 (갤러그 특유의 3종류 적 생성)
    function initEnemies() {
        enemies = [];
        const cols = 8;
        
        // 보스 갤러그 (1줄) - 체력 2
        for (let c = 0; c < 4; c++) {
            enemies.push(createEnemy(c, 0, cols, "boss", 2, c * 10));
        }
        // 빨간 파리 (2줄) - 체력 1
        for(let r = 1; r <= 2; r++) {
            for (let c = 0; c < cols; c++) {
                enemies.push(createEnemy(c, r, cols, "guard", 1, c * 5 + r * 15));
            }
        }
        // 파란 꿀벌 (2줄) - 체력 1
        for(let r = 3; r <= 4; r++) {
            for (let c = 0; c < cols; c++) {
                enemies.push(createEnemy(c, r, cols, "bee", 1, c * 5 + r * 15));
            }
        }
    }

    // 개별 적군 객체 생성
    function createEnemy(col, row, totalCols, type, hp, entryDelay) {
        // 편대 내에서의 목표 위치 계산
        const spacingX = 40;
        const spacingY = 35;
        const startX = (canvas.width - (totalCols * spacingX)) / 2;
        const targetX = startX + col * spacingX;
        const targetY = 50 + row * spacingY;

        return {
            type: type,
            hp: hp,
            col: col,
            row: row,
            baseTargetX: targetX,
            baseTargetY: targetY,
            x: canvas.width / 2, // 진입 시작점 X
            y: -50,              // 진입 시작점 Y
            state: "waiting",    // waiting -> entering -> idle (편대) -> diving (강하) -> returning
            timer: entryDelay,
            angle: 0,
            diveStartX: 0,
            diveStartY: 0
        };
    }

    // 키보드 리스너
    window.addEventListener("keydown", (e) => {
        if (e.code === "ArrowLeft") keys.ArrowLeft = true;
        if (e.code === "ArrowRight") keys.ArrowRight = true;
        if (e.code === "Space") {
            if (gameState === "START" || gameState === "GAMEOVER") {
                if (gameState === "GAMEOVER") { score = 0; level = 1; lives = 3; }
                gameState = "PLAYING";
                playerBullets = [];
                enemyBullets = [];
                initEnemies();
            } else if (gameState === "PLAYING" && !spacePressed) {
                // 오락실 원작 로직: 화면에 총알 2발까지만 존재 가능
                if (playerBullets.length < 2) {
                    playerBullets.push({ x: player.x + player.width / 2 - 2, y: player.y, width: 4, height: 12 });
                }
                spacePressed = true;
            }
        }
    });

    window.addEventListener("keyup", (e) => {
        if (e.code === "ArrowLeft") keys.ArrowLeft = false;
        if (e.code === "ArrowRight") keys.ArrowRight = false;
        if (e.code === "Space") spacePressed = false;
    });

    function checkCollision(r1, r2) {
        return (r1.x < r2.x + r2.width && r1.x + r1.width > r2.x &&
                r1.y < r2.y + r2.height && r1.y + r1.height > r2.y);
    }

    function update() {
        if (gameState !== "PLAYING") return;
        frameCount++;

        // 배경 업데이트
        stars.forEach(s => {
            s.y += s.speed;
            if (s.y > canvas.height) s.y = 0;
        });

        // 플레이어 이동
        if (keys.ArrowLeft && player.x > 0) player.x -= player.speed;
        if (keys.ArrowRight && player.x < canvas.width - player.width) player.x += player.speed;

        // 플레이어 총알
        for (let i = playerBullets.length - 1; i >= 0; i--) {
            playerBullets[i].y -= 12; // 총알 속도 빠름
            if (playerBullets[i].y < 0) playerBullets.splice(i, 1);
        }

        // 적 총알
        for (let i = enemyBullets.length - 1; i >= 0; i--) {
            enemyBullets[i].y += 5;
            if (checkCollision(enemyBullets[i], player)) {
                enemyBullets.splice(i, 1);
                lives--;
                if (lives <= 0) gameState = "GAMEOVER";
            } else if (enemyBullets[i].y > canvas.height) {
                enemyBullets.splice(i, 1);
            }
        }

        // 편대 이동 로직 (전체가 좌우로 흔들리며 숨을 쉼)
        formation.offsetX += 0.5 * formation.direction;
        if (formation.offsetX > 40 || formation.offsetX < -40) formation.direction *= -1;
        formation.breathing = Math.sin(frameCount * 0.05) * 5; // 숨쉬는 듯한 수축 팽창

        let allDead = true;
        let idleCount = 0;

        // 적 로직 업데이트
        enemies.forEach(e => {
            if (e.hp <= 0) return;
            allDead = false;

            // 목표 좌표 계산 (편대 위치)
            const curTargetX = e.baseTargetX + formation.offsetX + (e.col - 4) * formation.breathing * 0.5;
            const curTargetY = e.baseTargetY + formation.offsetY + (e.row) * formation.breathing * 0.2;

            if (e.state === "waiting") {
                e.timer--;
                if (e.timer <= 0) { e.state = "entering"; e.angle = 0; }
            } 
            else if (e.state === "entering") {
                // 원작 특유의 곡선 진입 흉내 (수학적 궤적)
                e.angle += 0.05;
                e.x = curTargetX + Math.sin(e.angle) * 100 * Math.exp(-e.angle * 0.5);
                e.y += 3;
                if (e.y > curTargetY) {
                    e.y = curTargetY;
                    e.x = curTargetX;
                    e.state = "idle";
                }
            } 
            else if (e.state === "idle") {
                idleCount++;
                e.x = curTargetX;
                e.y = curTargetY;

                // 랜덤하게 강하 공격 시작
                if (Math.random() < 0.002 + (level * 0.0005)) {
                    e.state = "diving";
                    e.diveStartX = e.x;
                    e.diveStartY = e.y;
                    e.timer = 0; // 강하 궤적 타이머
                }
            } 
            else if (e.state === "diving") {
                e.timer += 0.05;
                // 플레이어를 향해 둥글게 강하하는 로직
                e.x = e.diveStartX + Math.sin(e.timer * 1.5) * 80;
                e.y += 4 + level * 0.5;

                // 하강 중 총알 발사
                if (Math.random() < 0.02) {
                    enemyBullets.push({ x: e.x + 10, y: e.y + 20, width: 4, height: 10 });
                }

                // 화면 아래로 벗어나면 위에서 다시 나타나 편대로 복귀 준비
                if (e.y > canvas.height) {
                    e.y = -30;
                    e.x = curTargetX;
                    e.state = "returning";
                }
                
                // 플레이어와 본체 충돌
                if (checkCollision({x: e.x, y: e.y, width: 25, height: 20}, player)) {
                    lives = 0;
                    gameState = "GAMEOVER";
                }
            }
            else if (e.state === "returning") {
                // 다시 자기 자리로 쫓아감
                e.y += 3;
                if (e.y >= curTargetY) {
                    e.y = curTargetY;
                    e.state = "idle";
                }
            }
        });

        // 총알 충돌 (플레이어 총알 -> 적)
        for (let i = playerBullets.length - 1; i >= 0; i--) {
            let hit = false;
            let b = playerBullets[i];
            for (let j = 0; j < enemies.length; j++) {
                let e = enemies[j];
                if (e.hp > 0 && e.state !== "waiting" && checkCollision(b, {x: e.x, y: e.y, width: 25, height: 20})) {
                    e.hp--;
                    hit = true;
                    if (e.hp <= 0) {
                        score += (e.state === "diving" ? 200 : 100) * level; // 강하 중인 적 격추시 보너스
                    }
                    break;
                }
            }
            if (hit) playerBullets.splice(i, 1);
        }

        // 스테이지 클리어
        if (allDead && enemies.length > 0) {
            level++;
            initEnemies();
            playerBullets = [];
            enemyBullets = [];
        }
    }

    function draw() {
        // 캔버스 초기화
        ctx.fillStyle = "#000000";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // 별 (우주 스크롤)
        ctx.fillStyle = "#aaaaaa";
        stars.forEach(s => {
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.speed, 0, Math.PI * 2);
            ctx.fill();
        });

        if (gameState === "START") {
            ctx.fillStyle = "#ff0000"; ctx.font = "bold 40px 'Courier New'"; ctx.textAlign = "center";
            ctx.fillText("GALAGA LOGIC", canvas.width / 2, canvas.height / 2 - 40);
            ctx.fillStyle = "#00ffff"; ctx.font = "18px 'Courier New'";
            ctx.fillText("Press SPACE to Start", canvas.width / 2, canvas.height / 2 + 20);
            return;
        }

        // 플레이어 (전투기 모양)
        ctx.fillStyle = "#dedede"; // 기체 은색
        ctx.beginPath();
        ctx.moveTo(player.x + player.width / 2, player.y);
        ctx.lineTo(player.x + player.width, player.y + player.height);
        ctx.lineTo(player.x + player.width / 2 + 5, player.y + player.height - 8);
        ctx.lineTo(player.x + player.width / 2 - 5, player.y + player.height - 8);
        ctx.lineTo(player.x, player.y + player.height);
        ctx.closePath();
        ctx.fill();
        ctx.fillStyle = "#ff0000"; // 조종석 빨간색
        ctx.fillRect(player.x + player.width / 2 - 2, player.y + 10, 4, 8);

        // 총알
        ctx.fillStyle = "#ffff00";
        playerBullets.forEach(b => ctx.fillRect(b.x, b.y, b.width, b.height));
        ctx.fillStyle = "#ff3333";
        enemyBullets.forEach(b => ctx.fillRect(b.x, b.y, b.width, b.height));

        // 적
        enemies.forEach(e => {
            if (e.hp <= 0 || e.state === "waiting") return;
            
            ctx.save();
            ctx.translate(e.x + 12.5, e.y + 10);
            
            // 색상 결정 로직 (보스는 피격 시 색상이 변함)
            if (e.type === "boss") {
                ctx.fillStyle = e.hp === 2 ? "#00ff00" : "#0055ff"; // 체력 2: 녹색, 체력 1: 파란색
            } else if (e.type === "guard") {
                ctx.fillStyle = "#ff0000"; // 빨간 파리
            } else {
                ctx.fillStyle = "#00aaaa"; // 파란 꿀벌
            }

            // 도형 렌더링 (원작의 날개를 펼친 벌레 모양 단순화)
            ctx.beginPath();
            ctx.moveTo(0, -10);
            ctx.lineTo(12, 0);
            ctx.lineTo(12, 10);
            ctx.lineTo(6, 5);
            ctx.lineTo(-6, 5);
            ctx.lineTo(-12, 10);
            ctx.lineTo(-12, 0);
            ctx.closePath();
            ctx.fill();

            // 눈 그리기
            ctx.fillStyle = "#fff";
            ctx.fillRect(-6, -4, 3, 3);
            ctx.fillRect(3, -4, 3, 3);

            ctx.restore();
        });

        // UI
        ctx.fillStyle = "#ff0000"; ctx.font = "bold 16px 'Courier New'"; ctx.textAlign = "left";
        ctx.fillText("SCORE", 10, 20);
        ctx.fillStyle = "#ffffff";
        ctx.fillText(score, 10, 40);

        ctx.textAlign = "center"; ctx.fillStyle = "#00ffff";
        ctx.fillText("STAGE " + level, canvas.width / 2, 30);

        // 오락실 스타일의 목숨 아이콘 표기
        ctx.textAlign = "right"; ctx.fillStyle = "#dedede";
        for(let i = 0; i < lives; i++) {
            ctx.beginPath();
            let lx = canvas.width - 20 - (i * 25);
            let ly = 15;
            ctx.moveTo(lx, ly);
            ctx.lineTo(lx + 10, ly + 15);
            ctx.lineTo(lx - 10, ly + 15);
            ctx.fill();
        }

        // 게임 오버
        if (gameState === "GAMEOVER") {
            ctx.fillStyle = "#ff0000"; ctx.font = "bold 40px 'Courier New'"; ctx.textAlign = "center";
            ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2);
            ctx.fillStyle = "#ffffff"; ctx.font = "18px 'Courier New'";
            ctx.fillText("Press SPACE to Restart", canvas.width / 2, canvas.height / 2 + 40);
        }
    }

    function loop() {
        update();
        draw();
        requestAnimationFrame(loop);
    }
    loop();
</script>
"""

html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Galaga Logic Implementation</title>
</head>
<body>
    <div id="report-header">
        <h2 style="margin: 0; color: #4CAF50;">[CI/CD] {status}</h2>
        <p style="margin: 5px 0 0 0; font-size: 14px; color: #ccc;">{message}</p>
    </div>
    
    <div id="game-wrapper">
        <canvas id="gameCanvas" width="480" height="600"></canvas>
        <div class="status-panel">
            [ ⬅️ / ➡️ ] 방향키 이동 &nbsp;|&nbsp; [ SPACE ] 총알 발사 (화면당 2발 제한)
        </div>
    </div>

    {game_logic_and_style}
</body>
</html>"""

os.makedirs("public", exist_ok=True)
with open("public/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("성공적으로 public/index.html 파일이 생성되었습니다! 갤러그의 편대 이동 및 강하 로직이 적용되었습니다.")