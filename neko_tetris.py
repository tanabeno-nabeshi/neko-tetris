import pygame as pg
from pygame.locals import *
import sys
import random

#画面
SCREEN_W, SCREEN_H = 360, 640
#フォント(任意)
title_font = "font/Kranky-Regular.ttf"
crayon_font = "font/crayon_1-1.ttf"

levels = [("1:EASY", 400), ("2:NORMAL", 200), ("3:HARD", 100)]
level_btn = [pg.Rect(60, 280 + i*70, SCREEN_W-120, 50) for i in range(len(levels))]
#ネッコ
cats = [pg.image.load(f"image/cat{i}.png") for i in range(7)]
hata = pg.image.load(f"image/hata.png")
hata_s = pg.transform.rotozoom(hata, 0, 0.31)

#ゲーム画面
BLOCK_SIZE = 30
#盤面/グリッド線
BOARD_W,BOARD_H = 10, 20 #マス目の数
OFFSET_X = (SCREEN_W - (BLOCK_SIZE*BOARD_W)) // 2#中央揃え
OFFSET_Y = 20#開始位置
#壁蹴り技
# 順番： 0.そのまま 1.左 2.右 3.上(床蹴り) 4.左に2 5.右に2
WALL_KICK_DATA = [(0, 0), (-1, 0), (1, 0), (0, -1), (-2, 0), (2, 0)]

#色指定
BG_COLOR = (240, 230, 255)
BOARD_BG = (255,255,255,150)#盤面半透明
GRID_COLOR = (212, 197, 249)
TEXT_COLOR = (100,80,140)
BLOCK_OUTLINE = (255,255,255)
DOT_COLOR = (255,255,255)
DOT_INTERVAL = 30
GO_COLOR = (255, 100, 150)

MINOS_DATA = {#相対座標
    'I': {'shape': [[-1, 0], [0, 0], [1, 0], [2, 0]],
          "cat":0,
          'color': (140, 220, 230)}, # パステルターコイズ
    'O': {'shape': [[0, 0], [1, 0], [0, 1], [1, 1]],
          "cat":1,
          'color': (255, 230, 150)}, # パステルイエロー
    'T': {'shape': [[-1, 0], [0, 0], [0, 1], [1, 0]],
          "cat":2,
          'color': (200, 160, 240)}, # パステルパープル
    'S': {'shape': [[-1, 1], [0, 1], [0, 0], [1, 0]],
          "cat":3,
          'color': (160, 230, 160)}, # パステルミント
    'Z': {'shape': [[-1, 0], [0, 0], [0, 1], [1, 1]],
          "cat":4,
          'color': (255, 160, 180)}, # パステルコーラル
    'J': {'shape': [[-1, 0], [0, 0], [1, 0], [1, 1]],
          "cat":5,
          'color': (150, 180, 250)}, # パステルブルー
    'L': {'shape': [[-1, 1], [-1, 0], [0, 0], [1, 0]],
          "cat":6,
          'color': (255, 190, 150)}  # パステルピーチ
}
MINOS_KEYS = list(MINOS_DATA.keys())

class Tetris:
    def __init__(self):#盤面の初期化
        self.board = [[None for _ in range(BOARD_W)] for _ in range(BOARD_H)]
        self.score = 0
        self.game_over = False
        self.particles = []
        self.new_mino()

    def new_mino(self):#新規ミノ生成
        self.key = random.choice(MINOS_KEYS)
        self.shape = MINOS_DATA[self.key]["shape"]
        self.color = MINOS_DATA[self.key]["color"]
        self.cat = MINOS_DATA[self.key]["cat"]
        self.x = BOARD_W//2
        self.y = 0
        if self.check_collision(self.x, self.y, self.shape):
            self.game_over = True

    def check_collision(self, x, y, shape):#衝突判定
        for pos in shape:
            mx = x + pos[0]
            my = y + pos[1]
            if my < 0 or my >= BOARD_H or mx < 0 or mx >= BOARD_W:
                return True #壁と床
            if my >= 0 and self.board[my][mx]:
                return True #固定されたブロックとの
        return False

    def move(self, x, y):#移動
        if not self.check_collision(self.x + x, self.y + y, self.shape):
            self.x += x
            self.y += y
            return True
        return False

    def rotate(self):#回転
        if self.key == "O": return

        rotate_shape = [[-ay, ax] for ax, ay in self.shape]
        #壁蹴り
        for dx, dy in WALL_KICK_DATA:
            kick_x = self.x + dx
            kick_y = self.y + dy
            if not self.check_collision(kick_x, kick_y, rotate_shape):
                self.shape = rotate_shape
                self.x = kick_x
                self.y = kick_y
                return

    def fix_mino(self):#ミノの固定
        for pos in self.shape:
            fx = self.x + pos[0]
            fy = self.y + pos[1]
            if 0 <= fx < BOARD_W and 0 <= fy < BOARD_H:
                self.board[fy][fx] = [self.color, self.cat]
        self.clear_lines()
        self.new_mino()

    def clear_lines(self):#一列並んだら消す
        check_lines = [i for i, row in enumerate(self.board)
                       if all(mino is not None for mino in row)]
        for row_idx in check_lines:
            for p in range(BOARD_W):
                px = OFFSET_X + p * BLOCK_SIZE
                py = OFFSET_Y + row_idx * BLOCK_SIZE
                for _ in range(5):
                    particle = Particle(px, py, self.board[row_idx][p][0])
                    self.particles.append(particle)

            del self.board[row_idx]
            self.board.insert(0, [None for _ in range(BOARD_W)])
            self.score += 100

class Particle: #散ってく演出
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
        self.size = random.randint(3, 7)
        self.life = 1.0
        self.vx, self.vy = random.uniform(-2, 2), random.uniform(-5, -1)#上向きの速度
        self.ang = random.uniform(0, 360)

    def animation(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.12 #重力
        self.life -= 0.035#消えゆくキラキラ
        self.ang += 8 #くるくる

    def draw(self, screen):
        if self.life > 0 and self.color is not None:
            s = pg.Surface((self.size, self.size), pg.SRCALPHA)
            alpha = int(self.life * 255)
            pg.draw.rect(s, (*self.color, alpha), (0, 0, self.size, self.size))
            rotate_particle = pg.transform.rotate(s, self.ang)
            screen.blit(rotate_particle, (self.x, self.y))

def draw_cats(screen, cat, x, y):
    rect = [x-2, y-2]
    screen.blit(cat, rect)

class Text:
    def __init__(self, size, text, color, font="arial"):
        try:self.font = pg.font.Font(font, size)
        except Exception as e:self.font = pg.font.SysFont(font, size)
        self.text = self.font.render(text, True, color)
        self.text_w, self.text_h = self.text.get_width(), self.text.get_height()
        
    def draw_text(self, screen, x, y):
        screen.blit(self.text, (x, y))
    
def draw_dot(screen):
    dx = 0
    half_step = DOT_INTERVAL 
    full_step = int(DOT_INTERVAL * 2)
    line_color = (250, 240, 255)
    for x in range(dx, SCREEN_W+half_step, full_step):
        for y in range(dx, SCREEN_H, DOT_INTERVAL):
            if (y-dx)%full_step == 0:
                curr_x, curr_y = x, y
            else:
                curr_x, curr_y = x + half_step, y
            
            next_y = curr_y + half_step

            # 右下方向への線
            pg.draw.aaline(screen, line_color, (curr_x, curr_y),
                         (curr_x + half_step, next_y), 1)
            # 左下方向への線
            pg.draw.aaline(screen, line_color, (curr_x, curr_y),
                         (curr_x - half_step, next_y), 1)
            
            pg.draw.circle(screen, DOT_COLOR, (curr_x, curr_y), 3)

#ネッコ
# --- 定数 ---
MAX_BALLS = 90  # 画面内に存在できる最大数
GRAVITY = 0.005

# --- 画像の準備 ---
all_rotated_caches = []

for file in cats:

    cache = [pg.transform.rotate(file, a) for a in range(360)]
    all_rotated_caches.append(cache)

class Ball:
    def __init__(self, x, y, auto_drop=False):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(0, 1.5) if auto_drop else random.uniform(-1.5, 0)
        self.bounce = random.uniform(-0.5, -0.7)
        self.angle = random.randint(0, 359)
        self.rot_speed = random.uniform(-1, 1)
        self.img_id = random.randint(0, len(all_rotated_caches) - 1)
        self.is_sleeping = False

    def update(self):
        if self.is_sleeping:
            return

        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy

        
        if self.y + 18 > SCREEN_H:
            self.y = SCREEN_H - 18
            if abs(self.vy) < 1.5: 
                self.vy = 0
                self.vx = 0
                self.rot_speed = 0
                self.is_sleeping = True
            else:
                self.vy *= self.bounce
                self.vx *= 0.9

        if self.x - 16 < 0 or self.x + 16 > SCREEN_W:
            self.vx *= -0.8
            self.x = max(16, min(self.x, SCREEN_W - 16))

        self.angle = (self.angle + self.rot_speed) % 360

    def draw(self, surface):
        img = all_rotated_caches[self.img_id][int(self.angle)]
        rect = img.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(img, rect)

def reset_scene():
    #画面をクリアして初期状態に戻す
    new_balls = []
    for _ in range(50):
        spawn_x = random.randint(0, SCREEN_W)
        spawn_y = random.uniform(-500, 0)
        new_balls.append(Ball(spawn_x, spawn_y, auto_drop=True))
    return new_balls
   
#難易度選択
def select_difficulty(screen):
    title1 = Text(45, "Meow Meow", TEXT_COLOR, title_font)
    title_shadow1 = Text(45, "Meow Meow", DOT_COLOR, title_font)
    title2 = Text(45, "TETRIS", TEXT_COLOR, title_font)
    title_shadow2 = Text(45, "TETRIS", DOT_COLOR, title_font)
    # 初回の生成
    balls = reset_scene()
    while True:
        mx, my = pg.mouse.get_pos()#マウスのポジション
        screen.fill(BG_COLOR)
        draw_dot(screen)

        # 更新
        for ball in balls: ball.update()       
        # 制限数を超えたら止まっているものから消去
        if len(balls) > MAX_BALLS:
            for i, b in enumerate(balls):
                if b.is_sleeping:
                    balls.pop(i)
                    break # 1フレームに1つずつ消すと自然
            else:
                # もし止まっているものが一つもなければ、一番古いものを消す
                balls.pop(0)
        # 描画
        for ball in balls: ball.draw(screen)
            
        pg.draw.rect(screen, BLOCK_OUTLINE, (0,0,SCREEN_W,SCREEN_H), width=15)
        pg.draw.rect(screen, BG_COLOR, (0,0,SCREEN_W,SCREEN_H), width=5)
        title_shadow1.draw_text(screen,SCREEN_W//2 - title1.text_w//2+2, 122)
        title_shadow2.draw_text(screen,SCREEN_W//2 - title2.text_w//2+2,
                  120+title2.text_h+2)
        title1.draw_text(screen,SCREEN_W//2 - title1.text_w//2, 120)
        title2.draw_text(screen,SCREEN_W//2 - title2.text_w//2,
                  120+title2.text_h)
        
        for i, (name, _) in enumerate(levels):
            if level_btn[i].collidepoint((mx, my)):
                pg.draw.rect(screen,TEXT_COLOR, level_btn[i], border_radius=10) # ボタン
                lbl = Text(28, name, BG_COLOR , crayon_font)
                lbl.draw_text(screen,SCREEN_W//2 - lbl.text_w//2, 290 + i * 70)
            else:
                pg.draw.rect(screen, DOT_COLOR, level_btn[i], border_radius=10) # ボタン
                lbl = Text(28, name, TEXT_COLOR, crayon_font)
                lbl.draw_text(screen,SCREEN_W//2 - lbl.text_w//2, 290 + i * 70)
                
        pg.display.flip()
        
        for e in pg.event.get():
            if e.type == QUIT:
                    pg.quit()
                    sys.exit()
                    return
            if e.type == KEYDOWN:
                if e.key == K_1: return levels[0][1]
                if e.key == K_2: return levels[1][1]
                if e.key == K_3: return levels[2][1]
                # スペースキーでリセット
                if e.key == K_SPACE:balls = reset_scene()
                
            elif e.type == MOUSEBUTTONDOWN  and e.button == 1:
                meow = random.randint(0, 1)
                for _ in range(5):
                    balls.append(Ball(mx, my))
                for i in range(len(levels)):
                    if level_btn[i].collidepoint(e.pos):
                        return levels[i][1]
def main():
    pg.init()
    screen = pg.display.set_mode((SCREEN_W,SCREEN_H))
    pg.display.set_caption("Meow Meow Tetris")

    #長押しの操作を最適化
    key_timers = {K_LEFT: 0, K_RIGHT: 0, K_DOWN: 0,}
    while True:
        fall_speed = select_difficulty(screen)
        #難易度が押されなかった場合
        if fall_speed is None: break
        fall_time = 0 
        screen.fill(BG_COLOR)
        clock = pg.time.Clock()
        game = Tetris()
        board_surface = pg.Surface((SCREEN_W, SCREEN_H), pg.SRCALPHA)

        while not game.game_over:
            screen.fill(BG_COLOR)
            draw_dot(screen)
            screen.blit(hata_s,(2, 0))
            dt = clock.tick(60)#デルタタイム
            fall_time += dt

            #入力処理 長押し
            keys = pg.key.get_pressed()
            for k in [K_LEFT, K_RIGHT, K_DOWN]:
                if keys[k]:
                    if key_timers[k] == 0:
                        if k == K_LEFT: game.move(-1, 0)
                        if k == K_RIGHT: game.move(1, 0)
                        if k == K_DOWN: game.move(0, 1)
                    key_timers[k] += dt
                    limit = 150 if k != K_DOWN else 40#横移動は150ms/落下は40ms
                    if key_timers[k] > limit:
                        if key_timers[k] > limit + 40:#40msごとに移動
                            if k == K_LEFT: game.move(-1, 0)
                            if k == K_RIGHT: game.move(1, 0)
                            if k == K_DOWN: game.move(0, 1)
                            key_timers[k] = limit
                else: key_timers[k] = 0
                
            for e in pg.event.get():
                if e.type == QUIT:
                    pg.quit()
                    sys.exit()
                    return
                elif e.type == KEYDOWN:
                    if e.key == K_UP:
                        game.rotate()

            if fall_time > fall_speed:#一定の時間が経過したら一マス落下
                if not game.move(0, 1): game.fix_mino()#落下しない時間は固定
                fall_time = 0

            #盤面・グリッド線の描画
            pg.draw.rect(board_surface, BOARD_BG,
                             (OFFSET_X, OFFSET_Y,
                              BLOCK_SIZE*BOARD_W, BLOCK_SIZE*BOARD_H))
            screen.blit(board_surface, (0, 0))
            for x in range(OFFSET_X, BLOCK_SIZE*(BOARD_W+2),BLOCK_SIZE):
                    pg.draw.line(screen,GRID_COLOR,(x,OFFSET_Y),
                                 (x,BLOCK_SIZE*BOARD_H+OFFSET_Y))
            for y in range(OFFSET_Y, BLOCK_SIZE*(BOARD_H+1),BLOCK_SIZE):
                    pg.draw.line(screen,GRID_COLOR,(OFFSET_X,y),
                                 (BLOCK_SIZE*BOARD_W+OFFSET_X,y))

            #パーティクルを散らす
            for p in game.particles[:]:
                p.animation()
                p.draw(screen)
                if p.life <= 0:game.particles.remove(p)
                
            active_mino_cats = {(game.x + pos[0], game.y + pos[1]):
                                game.cat for pos in game.shape}
            for x in range(BOARD_W):#左から右へ
                for y in range(BOARD_H):
                    fixed_val = game.board[y][x]#固定済みのブロックを確認
                    active_cat_idx = active_mino_cats.get((x,y))#操作中のミノを確認
                    #猫を描画　固定優先
                    if fixed_val:
                        draw_cats(screen, cats[fixed_val[1]],
                            OFFSET_X + x*BLOCK_SIZE,
                            OFFSET_Y + y*BLOCK_SIZE)
                    elif active_cat_idx is not None:
                        draw_cats(screen, cats[active_cat_idx],
                            OFFSET_X + x*BLOCK_SIZE,
                            OFFSET_Y + y*BLOCK_SIZE)
                        
            # スコア表示
            score_txt = Text(30, f"SCORE: {game.score}", TEXT_COLOR, title_font)
            score_txt.draw_text(screen, 10, 10)
            pg.display.update()
            #clock.tick(60)

        # 結果画面
        board_surface.fill((255, 255, 255, 180)) 
        screen.blit(board_surface, (0,0))
        
        res_txt = Text(40, "GAME OVER",GO_COLOR, title_font)
        res_txt.draw_text(screen,SCREEN_W//2 - res_txt.text_w//2,
                              SCREEN_H/2-50)
        
        score_txt = Text(30, f"SCORE: {game.score}", TEXT_COLOR, title_font)
        score_txt.draw_text(screen, SCREEN_W//2 - score_txt.text_w//2,
                              SCREEN_H/2-150)
        pg.display.flip()
        pg.time.wait(2000)

if __name__ == "__main__":
    main()
