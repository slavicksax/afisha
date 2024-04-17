from PIL import Image, ImageDraw, ImageFont
import re
import textwrap
import os
import json


def get_parametrs():
    if not os.path.exists('hist_param.txt'):
        data = {
            "lanch_font_size": 46,
            "time_font_size": 72,
            "data_font_size": 100,
            "title_font_size": 70,
            "coord_time": (660, 150),
            "coord_data": (580, 30),
            "start_height": 450,
            "price_location": 650,
            "nominal_length": 1200,
            "left_indent": 80,
            "after_title": 100,
            "between_one": 50,
            "between_two": 80,
            "image_width": 300,
            "image_loc": 750,
            "TITLE_SIZE":100,
            "TITLE_POS":(350,100),
            "TITLE":"Бизнес-ланч",
            "TITLE_COLOR":(255,0,0),
            "title_color":(255,0,0),
            "lanch_color":(0,0,0),
            "time_data_color": (0, 0, 0)
        }
        with open("hist_param.txt", "w") as file:
            json.dump(data, file)

    with open("hist_param.txt", "r") as file:
            data = json.load(file)
    return data


def create(path,date,time,menu,folder_path):
    image = Image.open(path).convert("RGBA")
    draw = ImageDraw.Draw(image)
    data = get_parametrs()
    print(1)
    lanch_font_size = data['lanch_font_size']
    time_font_size = data['time_font_size']
    data_font_size = data['data_font_size']
    title_font_size = data['title_font_size']
    coord_time = data['coord_time']
    coord_data = data['coord_data']
    start_height = data['start_height']
    price_location = data['price_location']
    nominal_length = data['nominal_length']
    left_indent = data['left_indent']
    after_title = data['after_title']
    between_one = data['between_one']
    between_two = data['between_two']
    image_width = data['image_width']
    image_loc = data['image_loc']
    TIT_SIZE = data['TITLE_SIZE']
    TIT_POS = data['TITLE_POS']
    TIT = data['TITLE']
    TIT_COLOR = tuple(data['TITLE_COLOR'])
    title_color = tuple(data['title_color'])
    lanc_color = tuple(data['lanch_color'])
    time_data_color = tuple(data['time_data_color'])
    font_color = (0, 0, 0)
    print(1)
    FONT = ImageFont.truetype("ComforterBrush-Regular.ttf", TIT_SIZE)
    font = ImageFont.truetype("MADE Evolve Sans Regular (PERSONAL USE).ttf", lanch_font_size)
    font_time = ImageFont.truetype("ComforterBrush-Regular.ttf", time_font_size)
    font_date = ImageFont.truetype("ComforterBrush-Regular.ttf", data_font_size)
    font_title = ImageFont.truetype("TanaUncialSP.ttf", title_font_size)
    draw.text(coord_time, time, font=font_time, fill=time_data_color)
    draw.text(coord_data, date, font=font_date, fill=time_data_color)
    draw.text(TIT_POS,TIT,font=FONT,fill=TIT_COLOR)
    temp_h = start_height
    coord = []
    ass = []
    print(1)
    lines = menu.splitlines()

    sl =''
    for line in lines:
        print(line)
        if any(char.isdigit() for char in line):
            price = re.search(r'\d+([.,]\d+)', line)
            text = line.replace(price.group(),"")
            result = re.sub(r'(?<![)])\b(\d+)\b(?![\(])', r'(\1)', text)
            result = re.sub(r'\(+', '(', result)
            text = re.sub(r'\)+', ')', result)
            sl += text
            lines = textwrap.wrap(text, width=nominal_length // lanch_font_size)
            draw.text((price_location, temp_h), price.group().replace('.', ','), font=font, fill=lanc_color)
            for l in lines:
                draw.text((left_indent, temp_h),l , font=font, fill=lanc_color)
                temp_h += between_one
            temp_h += between_two - between_one
        else:
            coord.append(temp_h)
            if len(sl) > 0:
                ass.append(sl)
            sl = ''
            draw.text((left_indent, temp_h), line, font=font_title, fill=title_color)
            temp_h += after_title
    print(1)
    coord.append(temp_h)
    ass.append(sl)

    for root, dirs, files in os.walk(folder_path):
        for i in range(len(ass)):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                #print(file_name.replace(".png","").lower())
                if file_name.replace(".png","").lower() in ass[i].lower():
                    overlay_image = Image.open(file_path)

                    overlay_image = overlay_image.convert("RGBA")
                    k = overlay_image.width / image_width
                    h = int(overlay_image.height / k)
                    w = image_width
                    overlay_image = overlay_image.resize((w,h))
                    image.alpha_composite(overlay_image, (image_loc,coord[i] + int((coord[i+1]-coord[i])/2) - int(h/2)))
                    break
    return image
    #image.save(out + 'history.png')

