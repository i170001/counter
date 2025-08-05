from flask import Flask, jsonify, send_file
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from PIL import Image, ImageDraw, ImageFont
import io
import math
import json

# load .env file
load_dotenv()

app = Flask(__name__)

# connect to mongodb
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["counter"]
collection = db["visits"]

# paths
BASE_GIF_PATH = "assets/boingdragon.gif"
FONT_PATH = "assets/ComicRelief-Regular.ttf"
FONT_SIZE = 8

@app.route("/")
def home():
    result = collection.find_one_and_update(
        {"_id": "global"},
        {"$inc": {"count": 1}},
        upsert=True,
        return_document=True
    )
    count = result["count"]
    return jsonify({"message": "visit counter updated", "visits": count})

@app.route("/counter.gif")
def serve_counter_gif():
    # increment the counter and get updated value
    result = collection.find_one_and_update(
        {"_id": "global"},
        {"$inc": {"count": 1}},
        upsert=True,
        return_document=True
    )
    count = result["count"]

    # format count as fixed 6-digit string
    digits = list(f"{count:06d}")

    # load base gif and font
    base_gif = Image.open(BASE_GIF_PATH)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    # load digit coordinates
    with open("assets/digit_positions.json", "r") as f:
        digit_positions_per_frame = json.load(f)

    frames = []

    for frame_index in range(base_gif.n_frames):
        base_gif.seek(frame_index)
        frame = base_gif.copy().convert("RGBA")
        draw = ImageDraw.Draw(frame)

        # get coordinates for this frame
        positions = digit_positions_per_frame[frame_index]

        # draw digits directly at their positions
        for digit, (x, y) in zip(digits, positions):
            draw.text(
                (x, y),
                digit,
                font=font,
                fill=(255, 255, 255),  # white fill
                stroke_width=1,
                stroke_fill=(0, 0, 0)  # black border
            )

        frames.append(frame)

    # save all frames into a bytesio buffer
    gif_buffer = io.BytesIO()
    frames[0].save(
        gif_buffer,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=base_gif.info.get('duration', 100),
        loop=0,
        disposal=2
    )
    gif_buffer.seek(0)

    return send_file(gif_buffer, mimetype='image/gif')