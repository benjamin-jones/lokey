#!/usr/bin/python3.5

import logging
import matplotlib.pyplot as plt
import numpy as numpy
import scipy.misc

from queue import Queue
from optparse import OptionParser
from PIL import Image
from random import randint

_NAME_ = "LoKey"
_VERSION_ = "0.1"

EXIT_OK = 0
EXIT_IO_ERROR = -1

messages = Queue()


def lokey_cleanup(return_val=0):
    logging.info("Exiting...")
    exit(return_val)


def get_dimensions(png_object):
    width, height, planes = png_object.size[0], png_object.size[1], 4

    return width, height, planes


def transform_red(pixel):
    return pixel


def transform_green(pixel):
    global messages
    item = messages.get()

    # Don't allow clipping or overflow
    if item + pixel > 255:
        return pixel

    return item + pixel


def transform_blue(pixel):
    return pixel


def generate_mask(width, height):
    global messages
    for i in range(0, width*height):
        noise = randint(0, 128)
        messages.put(noise)


def transform_image(png_object, width, height, planes):

    arr = numpy.array(png_object)
    image_4d = numpy.reshape(arr, (height, width, planes))

    image_3d = image_4d[:, :, :-1]

    generate_mask(width, height)

    for i in range(0, height):
        row = []
        for pixel in image_3d[i]:
            pixel[0] = transform_red(pixel[0])
            pixel[1] = transform_green(pixel[1])
            pixel[2] = transform_blue(pixel[2])
            row.append(pixel)
        image_3d[i] = row

    plt.imshow(image_3d)
    plt.show()
    return image_3d


def print_metadata(png_object):
    logging.info("IMG WIDTH: %d HEIGHT: %d", png_object.size[0], png_object.size[1])


def lokey(cleanup_fcn=exit):
    return_value = EXIT_OK
    logging.basicConfig(filename='lokey.log',
                        format='%(asctime)s %(message)s',
                        level=logging.INFO)
    logging.info("%s - v%s", _NAME_, _VERSION_)

    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="Use PNG file", metavar="FILE")
    parser.add_option("-o", "--output", dest="output",
                      help="Output PNG file", metavar="OFILE")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")

    (options, args) = parser.parse_args()

    filename = options.filename
    output = options.output

    if filename is None:
        print("Usage: ./lokey.py -f <filename> -o <output filename>")
        cleanup_fcn(return_value)
    if output is None:
        print("Usage: ./lokey.py -f <filename> -o <output filename>")
        cleanup_fcn(return_value)

    try:
        r = Image.open(filename)
    except FileNotFoundError:
        logging.error("%s - File not found!", filename)
        return_value = EXIT_IO_ERROR
        cleanup_fcn(return_value)

    png_object = r

    print_metadata(png_object)

    width, height, plane_count = get_dimensions(png_object)
    out_image = transform_image(r, width, height, plane_count)

    logging.info("Writing output file...")
    scipy.misc.imsave(output, out_image)

    cleanup_fcn(return_value)

if __name__ == "__main__":
    lokey(cleanup_fcn=lokey_cleanup)
