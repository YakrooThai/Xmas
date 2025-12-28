import threading
import time
import os
from PIL import Image
from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip
from pinpong.board import Board
from pinpong.libs.dfrobot_ssd1306 import SSD1306_I2C

# ---------------- CONFIG ----------------
SCREEN_W, SCREEN_H = 240, 320
DISPLAY_TIME = 6

OLED_W, OLED_H = 128, 64
CHAR_W = 6
# ----------------------------------------

# Init board & OLED
Board().begin()
oled = SSD1306_I2C(width=OLED_W, height=OLED_H)

# ---------------- OLED UTILS ----------------
def draw_bmp(oled, bmp_path):
    bmp = Image.open(bmp_path).convert("1")
    for y in range(bmp.height):
        for x in range(bmp.width):
            oled.pixel(x, y, 1 if bmp.getpixel((x, y)) else 0)

def text_center(oled, text, y):
    x = max(0, (OLED_W - len(text) * CHAR_W) // 2)
    oled.text(text, x, y)

# ---------------- XMAS DATA ----------------
BMP_IMG = "xmas1.bmp"

xmas_list = [
    {
        "vid": "xmas1.mp4",
        "lines": ["Warm", "X'mas"]
    },
    {
        "vid": "xmas2.mp4",
        "lines": ["Joy&", "Happy"]
    },
    {
        "vid": "xmas3.mp4",
        "lines": ["Peace", "on Earth"]
    },
    {
        "vid": "xmas4.mp4",
        "lines": ["Celebrate", "Together"]
    },
    {
        "vid": "xmas5.mp4",
        "lines": ["Welcome", "NewYear", "2026"]
    },
]

# ---------------- OLED THREAD ----------------
def show_xmas_oled(data):
    oled.fill(0)
    draw_bmp(oled, BMP_IMG)

    start_y = 4
    line_gap = 14
    x_pos = 65        # <<< ปรับ X ตรงนี้อย่างเดียว

    for i, line in enumerate(data["lines"]):
        oled.text(line, x_pos, start_y + i * line_gap)

    oled.show()
    time.sleep(DISPLAY_TIME)

# ---------------- VIDEO THREAD ----------------
def play_video(video_path):
    try:
        clip = VideoFileClip(video_path)

        bg = ColorClip(
            size=(SCREEN_W, SCREEN_H),
            color=(0, 0, 0),
            duration=clip.duration
        )

        composite = CompositeVideoClip(
            [bg, clip.set_position("center")]
        )

        composite.preview(fullscreen=False)

        clip.close()
        composite.close()

    except Exception as e:
        print(f"⚠️ Video error {video_path}: {e}")

# ---------------- MAIN LOOP ----------------
while True:
    for x in xmas_list:
        if not os.path.exists(BMP_IMG) or not os.path.exists(x["vid"]):
            print(f"⚠️ Missing file {x}")
            continue

        oled_thread = threading.Thread(
            target=show_xmas_oled,
            args=(x,),
            daemon=True
        )

        video_thread = threading.Thread(
            target=play_video,
            args=(x["vid"],),
            daemon=True
        )

        oled_thread.start()
        video_thread.start()

        time.sleep(DISPLAY_TIME)
        print("🎄 Next X'Mas Scene...")
