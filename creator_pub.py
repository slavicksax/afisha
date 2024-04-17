from PIL import Image, ImageDraw, ImageFont
import re
import textwrap
import os
import json

def get_parametrs():
    if not os.path.exists('hist_param_pub.txt'):
        data = {
            "TITLE_SIZE": 100,
            "TITLE_POS": (350, 100),
            "TITLE": "Прямые трансляции",
            "TITLE_COLOR": (255, 0, 0),
            "title_size": 72,
            "name_size": 4,
            "vs_size": 70,
            "start_height": 450,
            "nominal_length": 1200,
            "left_indent": 80,
            "image_width": 300,
            "title_color":(255,0,0),
            "vs_color":(0,0,0)
        }
        with open("hist_param_pub.txt", "w") as file:
            json.dump(data, file)

    with open("hist_param_pub.txt", "r") as file:
            data = json.load(file)
    return data

first_column = 300
second_column = 900


def create(path_bg,text,folder_path):
    image = Image.open(path_bg).convert("RGBA")
    draw = ImageDraw.Draw(image)
    data = get_parametrs()

    TIT_SIZE = data['TITLE_SIZE']
    TIT_POS = data['TITLE_POS']
    TIT = data['TITLE']
    TIT_COLOR = tuple(data['TITLE_COLOR'])
    title_color = tuple(data['title_color'])

    title_size = data['title_size']
    name_size = data['name_size']
    vs_size = data['vs_size']
    vs_color = tuple(data['vs_color'])
    start_height = data['start_height']
    nominal_length = data['nominal_length']
    left_indent = data['left_indent']
    image_width = data['image_width']

    lines = text.splitlines()
    print(lines)
    date = lines[0]
    temp_height = start_height
    font_pub = ImageFont.truetype("MADE Evolve Sans Regular (PERSONAL USE).ttf", title_size)
    FONT = ImageFont.truetype("MADE Evolve Sans Regular (PERSONAL USE).ttf", TIT_SIZE)
    draw.text(TIT_POS, TIT, font=FONT, fill=TIT_COLOR)

    for line in lines[1:]:
        time = re.search(r'\d\d:\d\d', line)
        tit_fir_sec = line.replace(time.group(), "").split('#')
        print(tit_fir_sec)
        print()
        draw.text((left_indent,temp_height), time.group(), font=font_pub, fill=title_color)
        draw.text((left_indent + 170, temp_height), tit_fir_sec[0], font=font_pub, fill=title_color)
        for root, dirs, files in os.walk(folder_path):
            print(root, dirs, files)
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if file_name.replace(".png","").lower() in tit_fir_sec[1].lower():
                    overlay_image = Image.open(file_path)
                    image_loc = first_column
                elif file_name.replace(".png","").lower() in tit_fir_sec[2].lower():
                    overlay_image = Image.open(file_path)
                    image_loc = second_column
                else: break

                overlay_image = overlay_image.convert("RGBA")
                k = overlay_image.height / image_width
                w = int(overlay_image.width / k)
                h = image_width
                overlay_image = overlay_image.resize((w, h))
                image.alpha_composite(overlay_image,(image_loc - int(w/2),temp_height + 100))
                draw.text((550, temp_height + 250),'VS', font=font_pub, fill=vs_color)

                text_width = font_pub.getlength(tit_fir_sec[1])

                x = first_column - int(text_width / 2)
                y = temp_height + 400
                draw.text((x,y), tit_fir_sec[1], font=font_pub, fill=title_color)

                text_width = font_pub.getlength(tit_fir_sec[2])
                x = second_column - int(text_width / 2)
                y = temp_height + 400
                draw.text((x, y), tit_fir_sec[2], font=font_pub, fill=title_color)


        temp_height +=500
    return image



# date
# time title # first # second
# time title # first # second







