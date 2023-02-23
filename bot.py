import openai
import pytesseract
from PIL import Image
import os
import subprocess
import time
from multiprocessing import Pool
import questionary

class Rect:
    def __init__(self, min_x, min_y, max_x, max_y):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

openai.api_key = "ENTER_KEY_HERE" # EDIT THIS

Q_RECT = Rect(200, 1000, 1200, 1400) # EDIT THIS
A1_RECT = Rect(200, 1450, 1200, 1575) # EDIT THIS
A2_RECT = Rect(200, 1660, 1200, 1790) # EDIT THIS
A3_RECT = Rect(200, 1875, 1200, 2025) # EDIT THIS

PROMPT = """Return the correct answer.

Q: Which fairy tale character's nose grew when he told a lie?
* Pinocchio
* Peter Pan
* Bambi
A: Pinocchio

Q: What is a slang term for relaxing at home?
* Freezing
* Jumping
* Chilling
A: Chilling

Q: The game "Pass the Pigs" was invented in this year?
* 1987
* 1977
* 1997
A: 1977

Q: "Ferrum" is the Latin term for which metal?
* Copper
* Iron
* Zinc
A: Iron

Q: Whose most famous work is "Girl With a Pearl Earring"?
* Vermeer
* Rembrandt
* Rubens
A: Vermeer

Q: {}
* {}
* {}
* {}
A: """


def crop_screenshot(screenshot, rect):
    return screenshot.crop((rect.min_x, rect.min_y, rect.max_x, rect.max_y))

def take_screenshot():
    output = subprocess.check_output([
        'osascript',
        '-e',
        'tell app "Quicktime Player" to id of window 1'
    ])
    window_id = int(output.strip())
    subprocess.call([
        'screencapture',
        '-t', 'jpg',
        '-x',
        '-r',
        '-o',
        '-l{}'.format(window_id),
        'tiktok.png'
    ])
    return Image.open('tiktok.png')

def crop_obj(obj):
    screenshot, rect = obj
    return crop_screenshot(screenshot, rect)

def ocr_img(img):
    ocr = pytesseract.image_to_string(img)
    return ocr.replace('\n', ' ').strip()

def process_img(obj):
    return ocr_img(crop_obj(obj))

def generate_process_list(ss):
    return [(ss, Q_RECT), (ss, A1_RECT), (ss, A2_RECT), (ss, A3_RECT)]

def generate_prompt(inputs):
    return PROMPT.format(inputs[0], inputs[1], inputs[2], inputs[3])

def test_screenshot_cropping():
    result = list(map(crop_obj, generate_process_list(take_screenshot())))
    for img in result:
        img.show()

def run_gpt_3(prompt):
    return openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.4).choices[0].text

def bold_print(s):
    print('\033[1m' + s + '\033[0m')

def main():
    with Pool(4) as p:
        while True:
            response = questionary.select(
            "What do you want to do?",
            choices=[
                'Get the answer',
                'Test prompt generation',
                'Test OCR',
                'Test screenshot cropping',
                'Quit'
            ]).ask()

            if response == 'Get the answer':
                bold_print(
                    run_gpt_3(
                        generate_prompt(
                            p.map(
                                process_img, 
                                generate_process_list(
                                    take_screenshot())))))
            elif response == 'Test prompt generation':
                print(
                    generate_prompt(  
                        p.map(
                            process_img, 
                            generate_process_list(
                                take_screenshot()))))
            elif response == 'Test OCR':
                print(p.map(process_img, generate_process_list(take_screenshot())))
            elif response == 'Test screenshot cropping':
                test_screenshot_cropping()
            elif response == 'Quit':
                break



if __name__ == "__main__":
    main()