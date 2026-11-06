
import math

from PIL import Image, ImageDraw, ImageFilter


WIDTH, HEIGHT = 480, 320
FRAME_COUNT = 36
FRAME_DURATION_MS = 65


def make_background():
    image = Image.new("RGB", (WIDTH, HEIGHT), "#20272b")
    draw = ImageDraw.Draw(image)

    # Oval track
    draw.ellipse((70, 20, 410, 300), outline="#555c60", width=82)
    draw.ellipse((70, 20, 410, 300), outline="#aab0ae", width=3)
    draw.ellipse((110, 60, 370, 260), outline="#aab0ae", width=3)

    # Dashed lane markings
    for i in range(24):
        angle = 2 * math.pi * i / 24
        x = WIDTH / 2 + 130 * math.cos(angle)
        y = HEIGHT / 2 + 100 * math.sin(angle)
        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill="#d1c9a5")

    # Small trackside lights
    for angle in range(0, 360, 30):
        a = math.radians(angle)
        x = WIDTH / 2 + 181 * math.cos(a)
        y = HEIGHT / 2 + 141 * math.sin(a)
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill="#f2c96d")

    return image


def make_car():
    car = Image.new("RGBA", (90, 54), (0, 0, 0, 0))
    draw = ImageDraw.Draw(car)

    # Tires
    for box in [(14, 9, 28, 23), (62, 9, 76, 23),
                (14, 33, 28, 47), (62, 33, 76, 47)]:
        draw.rounded_rectangle(box, radius=4, fill="#111518")

    # Body, facing up
    draw.rounded_rectangle((22, 3, 68, 51), radius=15, fill="#e94b3c")
    draw.polygon([(25, 16), (32, 6), (58, 6), (65, 16)], fill="#ff6654")
    draw.rounded_rectangle((29, 13, 61, 27), radius=6, fill="#9bd5df")
    draw.rounded_rectangle((30, 30, 60, 41), radius=4, fill="#293d47")

    # Headlights and rear lights
    draw.rounded_rectangle((25, 4, 34, 8), radius=2, fill="#fff2b2")
    draw.rounded_rectangle((56, 4, 65, 8), radius=2, fill="#fff2b2")
    draw.rounded_rectangle((26, 46, 36, 50), radius=2, fill="#ffcf63")
    draw.rounded_rectangle((54, 46, 64, 50), radius=2, fill="#ffcf63")

    return car


def car_position(theta):
    return (
        WIDTH / 2 + 130 * math.cos(theta),
        HEIGHT / 2 + 100 * math.sin(theta),
    )


def make_frame(frame_index, background, car):
    theta = 2 * math.pi * frame_index / FRAME_COUNT
    x, y = car_position(theta)

    # Face along the oval, with a small angle offset for the drift.
    dx = -130 * math.sin(theta)
    dy = 100 * math.cos(theta)
    heading = math.degrees(math.atan2(dx, -dy)) + 22

    frame = background.copy()

    # Soft smoke trail from recent positions
    smoke = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    smoke_draw = ImageDraw.Draw(smoke)

    for age in range(12, 0, -1):
        past_theta = theta - age * 0.075
        px, py = car_position(past_theta)

        # Place smoke behind the car
        past_dx = -130 * math.sin(past_theta)
        past_dy = 100 * math.cos(past_theta)
        past_heading = math.atan2(past_dx, -past_dy) + math.radians(22)
        sx = px - math.sin(past_heading) * 28
        sy = py + math.cos(past_heading) * 28

        radius = 5 + age * 1.05
        alpha = max(10, 115 - age * 8)
        smoke_draw.ellipse(
            (sx - radius, sy - radius, sx + radius, sy + radius),
            fill=(205, 215, 216, alpha),
        )

    smoke = smoke.filter(ImageFilter.GaussianBlur(5))
    frame = Image.alpha_composite(frame.convert("RGBA"), smoke)

    rotated_car = car.rotate(-heading, resample=Image.Resampling.BICUBIC, expand=True)
    frame.alpha_composite(
        rotated_car,
        (int(x - rotated_car.width / 2), int(y - rotated_car.height / 2)),
    )

    return frame.convert("RGB")


def main():
    background = make_background()
    car = make_car()

    frames = [
        make_frame(i, background, car).convert(
            "P", palette=Image.Palette.ADAPTIVE, colors=128
        )
        for i in range(FRAME_COUNT)
    ]

    frames[0].save(
        "car_drift.gif",
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        optimize=False,
    )
    print("Created car_drift.gif")


if __name__ == "__main__":
    main()
