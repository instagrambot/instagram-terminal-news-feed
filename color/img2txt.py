#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Modified from https://github.com/hit9/img2txt/blob/gh-pages/img2txt.py

import sys
import color.ansi
from PIL import Image
from color.graphics_util import alpha_blend

def load_and_resize_image(imgname, antialias, maxLen, aspectRatio):

    if aspectRatio is None:
        aspectRatio = 1.0

    img = Image.open(imgname)

    # force image to RGBA - deals with palettized images (e.g. gif) etc.
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # need to change the size of the image?
    if maxLen is not None or aspectRatio != 1.0:

        native_width, native_height = img.size

        new_width = native_width
        new_height = native_height

        # First apply aspect ratio change (if any) - just need to adjust one axis
        # so we'll do the height.
        if aspectRatio != 1.0:
            new_height = int(float(aspectRatio) * new_height)

        # Now isotropically resize up or down (preserving aspect ratio) such that
        # longer side of image is maxLen
        if maxLen is not None:
            rate = float(maxLen) / max(new_width, new_height)
            new_width = int(rate * new_width)
            new_height = int(rate * new_height)

        if native_width != new_width or native_height != new_height:
            img = img.resize((new_width, new_height), Image.ANTIALIAS if antialias else Image.NEAREST)

    return img


def draw_with_color(img_path, post_info):
    maxLen, fontSize, target_aspect_ratio = 100.0, 7, 0.3
    img = load_and_resize_image(img_path, None, maxLen, target_aspect_ratio)
    # get pixels
    pixel = img.load()
    print('username: ' + post_info['username'])
    print('\033[4m' + post_info['site_url'] + '\033[0m \n')
    width, height = img.size
    sys.stdout.write(
        color.ansi.generate_ANSI_from_pixels(pixel, width, height, None)[0])
    sys.stdout.write("\x1b[0m\n")
    sys.stdout.flush()
    print('Likes: ' + post_info['likes'])
    print(post_info['caption'])
    print('-------------------\n')
