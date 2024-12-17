import pygame
import random
import mediapipe as mp
import cv2

# Khởi tạo Pygame
pygame.init()

# Cài đặt màn hình
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fishy Shipper")
bg = pygame.image.load("bg.png")
bg = pygame.transform.scale(bg, (800, 600))

#Lớp mờ màn hình
overlay = pygame.Surface((800, 600))  # Tạo một surface có cùng kích thước với màn hình
overlay.set_alpha(180)  # Đặt độ trong suốt (0: trong suốt hoàn toàn, 255: không trong suốt)
overlay.fill((0, 0, 0))  # Màu đen để tạo hiệu ứng làm mờ

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND_COLOR = (173, 216, 230)

# Phông chữ
font = pygame.font.SysFont("Arial", 24)

# Hình ảnh
shipper_image = pygame.image.load("Shipper.png")
food_images = [pygame.image.load(f"food{i}.png") for i in range(1, 4)]
car_images = [pygame.image.load(f"car{i}.png") for i in range(1, 5)]

# Thiết lập nhân vật người chơi
INITIAL_PLAYER_SIZE = 30  # Kích thước cố định của nhân vật người chơi
player_size = INITIAL_PLAYER_SIZE  # Thiết lập kích thước ban đầu
player_pos = [WIDTH // 2, HEIGHT // 2]

# Thiết lập kẻ thù
food_size_range = (10, 40)
car_size_range = (40, 80)
enemies = []

# Hàm vẽ văn bản
def draw_text(text, pos, size=24, color=BLACK):
    label = pygame.font.SysFont("Arial", size).render(text, True, color)
    screen.blit(label, pos)

# Hàm sinh kẻ thù
def spawn_enemy(is_car=False):
    if is_car:
        size = INITIAL_PLAYER_SIZE  # Đặt kích thước của cá mập bằng với kích thước của người chơi
        y = random.choice([155,235,312, 385])
        #y=y*100
        x = random.choice([0, WIDTH - size])
        speed = (random.randint(2, 4)) * (1 if x == 0 else -1)
        image = pygame.transform.scale(random.choice(car_images), (size * 3, size * 2.25))
        enemies.append({"pos": [x, y+10], "size": size, "speed": speed, "image": image, "is_car": True})
    else:
        size = INITIAL_PLAYER_SIZE  # Đặt kích thước của thức ăn bằng với kích thước của người chơi
        y = random.choice([95, 460])
        x = random.choice([100,250,400,550,700])
        speed = 0
        image = pygame.transform.scale(random.choice(food_images), (size * 2.5, size * 2.5))
        enemies.append({"pos": [x+50, y], "size": size, "speed": speed, "image": image, "is_car": False})


# Webcam
cap = cv2.VideoCapture(0)

# Đồng hồ trò chơi
clock = pygame.time.Clock()
running = True

# Vòng lặp trò chơi chính
def game_loop(player_pos):
    global shipper_image
    global splus
    enemies.clear()
    score = 0
    splus=0

    # Sinh các kẻ thù ban đầu
    for _ in range(7):  
        spawn_enemy(is_car=True)
    for _ in range(5):  
        spawn_enemy(is_car=False)

    prev_pos = player_pos[0]
    running = True
    paused = False

    while running:
        #bắt đầu vòng lặp của camera
        ret, frame = cap.read()
        if not ret:
            break

        # Xử lý khung hình từ webcam
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # Lấy vị trí ngón trỏ
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Lấy tọa độ ngón trỏ
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                player_pos[0] = int(index_finger_tip.x * WIDTH*2-200)
                player_pos[1] = int(index_finger_tip.y * HEIGHT*2-150)
                if player_pos[1]>420: player_pos[1]=420
                elif player_pos[1]<120: player_pos[1]=120

        # Hiển thị khung hình webcam
        cv2.imshow("Webcam", frame)

        #Hiển thị màn hình
        screen.fill(BACKGROUND_COLOR)
        pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, 100))  # Viền trên màu trắng
        pygame.draw.rect(screen, WHITE, (0, HEIGHT - 100, WIDTH, 100))
        screen.blit(bg, (0, 0))
        
        # Kiểm tra lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = True

        # Kiểm tra trạng thái tạm dừng
        if paused:
            screen.blit(overlay, (0, 0))
            pygame.mixer.music.pause()
            pause_sound = pygame.mixer.Sound("pause.mp3")
            pause_sound.set_volume(0.2)
            pause_sound.play()
            bg3 = pygame.image.load("pause.png")
            bg3 = pygame.transform.scale(bg3, (186*2,186*2))
            screen.blit(bg3, (400-186, 300-186))
            pygame.display.flip()
            while paused:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        paused = False
                        pause_sound.stop()
                        pygame.mixer.music.unpause()



        # Đổi hướng hình ảnh cá dựa trên chuyển động chuột
        if player_pos[0] > prev_pos + 5:
            shipper_image = pygame.image.load("Shipper.png")  # Hình ảnh cá hướng phải
        elif player_pos[0] < prev_pos - 5:
            shipper_image = pygame.transform.flip(pygame.image.load("Shipper.png"), True, False)  # Hình ảnh cá hướng trái
        
        prev_pos = player_pos[0]

        # Vẽ nhân vật người chơi (kích thước cố định)
        scaled_player_image = pygame.transform.scale(shipper_image, (INITIAL_PLAYER_SIZE * 2, INITIAL_PLAYER_SIZE * 2))
        screen.blit(scaled_player_image, (player_pos[0] - INITIAL_PLAYER_SIZE, player_pos[1] - INITIAL_PLAYER_SIZE))

        # Di chuyển kẻ thù và kiểm tra va chạm
        for enemy in enemies[:]:
            enemy["pos"][0] += enemy["speed"]
            flipped_image = pygame.transform.flip(enemy["image"], True, False) if enemy["speed"] < 0 else enemy["image"]

            # Đặt lại vị trí kẻ thù nếu nó vượt ra ngoài màn hình
            if enemy["pos"][0] < 0 or enemy["pos"][0] > WIDTH:
                enemy["pos"][1] = random.choice([155,235,312, 385])
                enemy["pos"][0] = 0 if enemy["speed"] > 0 else WIDTH
                enemy["speed"] = (random.randint(2, 4)+splus) * (1 if enemy["pos"][0] == 0 else -1)

            # Vẽ kẻ thù
            screen.blit(flipped_image, (enemy["pos"][0] - enemy["size"], enemy["pos"][1] - enemy["size"]))

            # Kiểm tra va chạm với cá thức ăn (Người chơi có thể ăn tất cả cá thức ăn)
            if not enemy["is_car"]:
                distance = ((player_pos[0] - enemy["pos"][0]) ** 2 + (player_pos[1] - enemy["pos"][1]) ** 2) ** 0.5
                if distance < INITIAL_PLAYER_SIZE + enemy["size"]:
                    #pygame.mixer.music.stop()
                    eat_sound = pygame.mixer.Sound("an.mp3")
                    eat_sound.set_volume(0.1)
                    eat_sound.play()
                    score += enemy["size"]
                    enemies.remove(enemy)
                    splus = splus + 0.1
                    spawn_enemy(is_car=False)  # Sinh thêm một cá thức ăn
                    for e in enemies:
                        if e["is_car"]:
                            if e["speed"]<0: e["speed"]-=0.2
                            else:  e["speed"]+=0.2

            # Kiểm tra va chạm với ô tô (Trò chơi kết thúc nếu bị chạm)
            if enemy["is_car"]:
                distance = ((player_pos[0] - enemy["pos"][0]) ** 2 + (player_pos[1] - enemy["pos"][1]) ** 2) ** 0.5
                if distance < INITIAL_PLAYER_SIZE + enemy["size"]-5:
                    #âm thanh tông xe
                    pygame.mixer.music.stop()
                    game_over_sound = pygame.mixer.Sound("tongxe.mp3")
                    game_over_sound.play()

                    #màn hình tông xe
                    screen.blit(overlay, (0, 0))
                    bg2 = pygame.image.load("End2.png")
                    bg2 = pygame.transform.scale(bg2, (186*2,70*2))
                    screen.blit(bg2, (400-186, 300-70))
                    pygame.display.flip()
                    pygame.time.wait(2000)

                    #nhạc lúc thua
                    pygame.mixer.init()  # Khởi tạo module âm thanh
                    pygame.mixer.music.load("op0.mp3")  # Đường dẫn file nhạc
                    pygame.mixer.music.set_volume(0.2)  # Điều chỉnh âm lượng (0.0 - 1.0)
                    pygame.mixer.music.play(-1)

                    #màn hình lúc thua
                    bg2 = pygame.image.load("End.png")
                    bg2 = pygame.transform.scale(bg2, (800, 600))
                    screen.blit(bg2, (0, 0))
                    pygame.display.flip()

                    waiting = True
                    while waiting:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                exit()
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_SPACE:  # Chơi lại
                                    waiting = False  # Thoát vòng chờ, bắt đầu lại game loop
                                if event.key == pygame.K_ESCAPE:  # Thoát trò chơi
                                    pygame.quit()
                                    exit()
                    return  # Kết thúc vòng lặp hiện tại, quay lại màn hình bắt đầu

        # Hiển thị điểm số
        draw_text(f"Score: {score}", (10, 10))

        # Cập nhật màn hình
        pygame.display.flip()
        clock.tick(30)

# Hàm hiển thị màn hình bắt đầu
def show_start_screen():

    screen.fill(BACKGROUND_COLOR)
    bg1 = pygame.image.load("start.png")
    screen.blit(bg1, (0, 0))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                #giải phóng tài nguyên
                cap.release()
                cv2.destroyAllWindows()
                exit()
                
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

# MediaPipe khởi tạo
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Chương trình chính
pygame.mixer.init()  # Khởi tạo module âm thanh
pygame.mixer.music.load("op1.mp3")  # Đường dẫn file nhạc
pygame.mixer.music.set_volume(0.2)  # Điều chỉnh âm lượng (0.0 - 1.0)
pygame.mixer.music.play(-1)
show_start_screen()
while True:
    #bắt đàu vòng lặp của game
    game_loop(player_pos=player_pos)
    pygame.mixer.init()  # Khởi tạo module âm thanh
    pygame.mixer.music.load("op1.mp3")  # Đường dẫn file nhạc
    pygame.mixer.music.set_volume(0.2)  # Điều chỉnh âm lượng (0.0 - 1.0)
    pygame.mixer.music.play(-1)
    show_start_screen()