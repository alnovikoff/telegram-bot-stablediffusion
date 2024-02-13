import telebot
from telebot import types
from auth_data import token
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Message
import requests
from PIL import Image, PngImagePlugin
import io
import os
import base64
from fastapi import FastAPI
import json
import aiogram

#stable diffusion url
url = ""


bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start', 'upload'])
def handle_start(message: Message):
    bot.send_message(message.chat.id, "Пожалуйста, напишите текст.")


# Changing photo with replacer
@bot.message_handler(content_types=['photo'])
def handle_photo(message: Message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path

    file_content = bot.download_file(file_path)
    photo_folder = "photos"
    file_name = "photo.png"
    photo_path = os.path.join (photo_folder, file_name)
    with open (photo_path, "wb") as f:
        f.write (file_content)

    bot.send_message(message.chat.id, "Photo accepted.")
    bot.send_message(message.chat.id, "Wait for the result.")

    photo_path = "photos/photo.png"
    
    with open(photo_path, 'rb') as image_file:
        base64_bytes = base64.b64encode(image_file.read())
        base64_bytes = base64_bytes.decode('utf-8')

    payload = {
        "input_image": base64_bytes,
        "detection_prompt": "face",
        "positive_prompt": "old face",
        "negative_prompt": "overlapping, stretching, cropping, bad promt, cartoon, painting",
        "width" : 512,
        "height" : 512,
        "sam_model_name": "sam_vit_h_4b8939.pth",
        "dino_model_name": "GroundingDINO_SwinT_OGC (694MB)",
        "seed": 362644423,
        "sampler": "DPM++ 2M SDE Karras",
        "steps": 35,
        "box_threshold": 0.3,
        "mask_expand": 35,
        "mask_blur":  4,
        "max_resolution_on_detection ": 1280,
        "cfg_scale": 6.5,
        "denoise":  1,
        "inpaint_padding":  40,
        "inpainting_mask_invert":  False,
        "upscaler_for_img2img" : "",
        "fix_steps" : False,
        "inpainting_fill" : 0,
        "sd_model_checkpoint": "realisticVisionV60B1_v60B1VAE",
    }

    response = requests.post(url=f'{url}replacer/replace', data=json.dumps(payload))

    
    r = response.json()
    print(response.json())        

    image = Image.open(io.BytesIO(base64.b64decode(r['image'])))

    image.save('output/output.png')

    bot.send_photo(message.chat.id, photo=open('output/output.png', 'rb'))
        
# Generate image by promt
@bot.message_handler(content_types=['text'])
def handle_text(message: Message):
    prompt = message.text

    bot.send_message(message.chat.id, "Text accepted.")
    bot.send_message(message.chat.id, "Wait for the result.")

    payload = {
        "prompt": prompt,
        "negative-prompt": "overlapping, stretching, cropping, bad promt, cartoon, painting",
        "styles": [
            "realisticVisionV60B1_v60B1VAE"
        ],
        "steps": 35,
        "height" : 1024,
        "width" : 768,
        "sampler" : "DPM++ 2M Karras",
        "cfg_scale": 7,
        "seed" : 343656465
    }

    response = requests.post(url=f'{url}sdapi/v1/txt2img', json=payload)
    
    r = response.json()
    print(response.json())        

    image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))

    image.save('output/output.png')

    bot.send_photo(message.chat.id, photo=open('output/output.png', 'rb'))




if __name__ == '__main__':
    bot.polling(none_stop=True)
