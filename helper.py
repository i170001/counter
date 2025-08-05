import matplotlib.pyplot as plt
from PIL import Image
import json

gif_path = "assets/boingdragon.gif"
output_json = "assets/digit_positions.json"
digit_positions_per_frame = []
digit_count = 6

with Image.open(gif_path) as gif:
    for frame_index in range(gif.n_frames):
        gif.seek(frame_index)
        frame = gif.copy().convert("RGB")

        fig, ax = plt.subplots()
        ax.imshow(frame)
        ax.set_title(f"Frame {frame_index} - Click {digit_count} digit positions")
        coords = []

        def onclick(event):
            if event.xdata is not None and event.ydata is not None:
                x, y = int(event.xdata), int(event.ydata)
                coords.append((x, y))
                print(f"Clicked: ({x}, {y})")
                if len(coords) == digit_count:
                    plt.close()

        cid = fig.canvas.mpl_connect('button_press_event', onclick)
        plt.show()

        digit_positions_per_frame.append(coords)

# save result
with open(output_json, "w") as f:
    json.dump(digit_positions_per_frame, f)

print("All digit positions saved.")