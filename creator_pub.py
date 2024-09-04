from PIL import Image, ImageDraw, ImageFont
import re
import textwrap
import os
import json

def get_parametrs():
    if not os.path.exists('hist_param_pub.txt'):
        data = {
            "TITLE_SIZE": 100,
            "TITLE_POS": (120, 100),
            "TITLE": "Прямые трансляции",
            "TITLE_COLOR": (255, 255, 255),
            "title_size": 72,
            "name_size": 50,
            "vs_size": 70,
            "start_height": 340,
            "nominal_length": 1200,
            "left_indent": 80,
            "image_width": 450,
            "title_color":(255,255,255),
            "vs_color":(255,255,255)
        }
        with open("hist_param_pub.txt", "w") as file:
            json.dump(data, file)

    with open("hist_param_pub.txt", "r") as file:
            data = json.load(file)
    return data

first_column = 300
second_column = 800


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

    font_date = ImageFont.truetype("htc-hand3.ttf", 80)
    font_pub = ImageFont.truetype("MADE Evolve Sans Regular (PERSONAL USE).ttf", title_size)
    font_name = ImageFont.truetype("MADE Evolve Sans Regular (PERSONAL USE).ttf", name_size)
    FONT = ImageFont.truetype("MADE Evolve Sans Regular (PERSONAL USE).ttf", TIT_SIZE)
    draw.text(TIT_POS, TIT, font=FONT, fill=TIT_COLOR)
    image_ = Image.open('Frame.png')
    image.alpha_composite(image_, (800,200))
    draw.text((840,200), date, font=font_date, fill=(0,0,0))

    count_tr = len(lines) - 1
    if count_tr < 3:
        siz = int((1750 - start_height)/count_tr)
    else:
        siz = int((1920 - start_height) / count_tr)

    if siz < 650:
        image_width = siz - 185
    korect = 0
    if siz > 650:
        korect = int((siz - 500)/2)

    if count_tr == 1:
        temp_height -= 160
    
    for line in lines[1:]:
        time = re.search(r'\d\d:\d\d', line)
        tit_fir_sec = line.replace(time.group(), "").split('#')
        if ' Ф ' in tit_fir_sec[0]:
            tit_fir_sec[0] = tit_fir_sec[0].replace(' Ф ','')
            image__ = Image.open('bol.png')
            image.alpha_composite(image__, (left_indent + 210, temp_height + korect))
        elif ' Х ' in tit_fir_sec[0]:
            tit_fir_sec[0] = tit_fir_sec[0].replace(' Х ','')
            image__ = Image.open('kl.png')
            image.alpha_composite(image__, (left_indent + 210, temp_height+ korect))

        image.alpha_composite(image_, (left_indent-40,temp_height+ korect))
        draw.text((left_indent,temp_height + korect), time.group(), font=font_date, fill=(0,0,0))

        tits = tit_fir_sec[0].split("$")
        tit_kor = 0
        for t in tits:
            draw.text((left_indent + 300, temp_height + korect + tit_kor), t, font=font_pub, fill=title_color)
            tit_kor+=70
        tit_kor-=70
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if tit_fir_sec[1].lower().strip() == file_name.replace(".png","").lower():
                    overlay_image = Image.open(file_path)
                    image_loc = first_column
                elif tit_fir_sec[2].lower().strip() == file_name.replace(".png","").lower():
                    overlay_image = Image.open(file_path)
                    image_loc = second_column
                else:
                    continue

                overlay_image = overlay_image.convert("RGBA")
                k = overlay_image.height / (image_width - 40)
                w = int(overlay_image.width / k)
                h = image_width - 40
                overlay_image = overlay_image.resize((w, h))
                image.alpha_composite(overlay_image,(image_loc - int(w/2),  temp_height + 140 + korect))

                s = font_pub.getlength("VS")/2

                draw.text((first_column + (second_column - first_column)/2 - s,temp_height + 120 + korect + h/2),'VS', font=font_pub, fill=vs_color)
                text_width = font_name.getlength(tit_fir_sec[1])
                x = first_column - int(text_width / 2)
                y = temp_height + 140 + h + korect
                draw.text((x,y), tit_fir_sec[1], font=font_name, fill=title_color)
                text_width = font_name.getlength(tit_fir_sec[2])
                x = second_column - int(text_width / 2)
                y = temp_height + 140 + h  + korect
                draw.text((x, y), tit_fir_sec[2], font=font_name, fill=title_color)


        temp_height +=siz
    return image



# date
# time title # first # second
# time title # first # second







