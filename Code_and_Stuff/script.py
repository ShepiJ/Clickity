#!/usr/bin/env python

import os
import logging
import random
import sys
import time

import cv2 as cv
import numpy as np
import pyautogui
from PIL import Image, ImageOps
import click

@click.command()
@click.option('--sleep_max', default=5.)
@click.option('--sleep_min', default=0.)
def run(sleep_max: float, sleep_min: float) -> None:
    logging.basicConfig(
        datefmt='%m/%d/%Y %I:%M:%S %p',
        format='%(asctime)s [%(levelname)s] %(message)s',
        level=logging.INFO,
    )
    
    templates_dir = _get_templates_dir()
    if not templates_dir:
        logging.error('Templates folder not found. Exiting.')
        _exit_with_delay(5)
        return
    
    templates = _get_templates(templates_dir)
    if not templates:
        logging.error('No PNG templates found in the templates folder. Exiting.')
        _exit_with_delay(5)
        return
    
    while True:
        sleep_seconds = random.uniform(sleep_min, sleep_max)
        logging.info('Sleeping for %f seconds', sleep_seconds)
        time.sleep(sleep_seconds)
        try:
            _find_and_click(templates)
        except Exception as e:
            logging.error('An error occurred: %s', e)

def _exit_with_delay(seconds: float) -> None:
    time.sleep(seconds)
    sys.exit(1)

class _Template:
    def __init__(self, array, name):
        self.array = array
        self.name = name

def _find_and_click(templates: list) -> None:
    screenshot_image = pyautogui.screenshot()
    screenshot = _image_to_grayscale_array(screenshot_image)

    all_points = []
    
    for template in templates:
        result = cv.matchTemplate(screenshot, template.array, cv.TM_CCOEFF_NORMED)
        threshold = 0.8  # Adjust this threshold as needed
        loc = np.where(result >= threshold)

        if loc[0].size > 0:
            # Collect all points for this template
            points = list(zip(loc[1], loc[0]))  # (x, y) coordinates
            all_points.extend(points)

    if all_points:
        # Randomly select a point from all matches
        pt = random.choice(all_points)
        current_mouse_pos = pyautogui.position()
        logging.info('Saving current mouse position at x=%f y=%f', *current_mouse_pos)
        pyautogui.click(pt[0] + templates[0].array.shape[1] // 2, pt[1] + templates[0].array.shape[0] // 2)
        logging.info('Clicking on a matched template at coordinates x=%f y=%f', pt[0], pt[1])
        pyautogui.moveTo(*current_mouse_pos)
        return

    logging.info('No matches found')

def _get_templates_dir() -> str:
    # Get the directory of the executable
    exe_path = os.path.abspath(sys.argv[0])
    root_dir = os.path.dirname(exe_path)
    templates_dir = os.path.join(root_dir, 'templates')
    
    if os.path.exists(templates_dir) and os.path.isdir(templates_dir):
        return templates_dir
    else:
        return ''

def _get_templates(templates_dir: str) -> list:
    templates = []
    
    for filename in os.listdir(templates_dir):
        if filename.endswith('.png'):
            path = os.path.join(templates_dir, filename)
            image = Image.open(path)
            array = _image_to_grayscale_array(image)
            templates.append(_Template(array=array, name=filename))

    return templates

def _image_to_grayscale_array(image: Image.Image) -> np.ndarray:
    image = ImageOps.grayscale(image)
    return np.array(image)

if __name__ == '__main__':
    run()
