#!/usr/bin/python3.5

import logging
import png
import numpy as numpy

from optparse import OptionParser

_NAME_ = "LoKey"
_VERSION_ = "0.1"

EXIT_OK = 0
EXIT_IO_ERROR = -1


def lokey_cleanup(return_val=0):
    logging.info("Exiting...")
    exit(return_val)


def get_dimensions(png_object):
    width, height, planes = png_object[0], png_object[1], png_object[3]['planes']

    return width, height, planes


def transform_image(png_object, width, height, planes):
    pngdata = png_object.asDirect()

    pngdata8bit = [i for i in map(numpy.uint16, pngdata[2])]
    image_2d = numpy.vstack(pngdata8bit)
    image_3d = numpy.reshape(image_2d, (height, width, planes))

    return image_3d


def print_metadata(png_object):
    logging.info("IMG WIDTH: %d HEIGHT: %d", png_object[0], png_object[1])


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
        r = png.Reader(filename=filename)
    except FileNotFoundError:
        logging.error("%s - File not found!", filename)
        return_value = EXIT_IO_ERROR
        cleanup_fcn(return_value)

    try:
        png_object = r.read()
    except png.FormatError:
        logging.error("%s - Invalid PNG!", filename)
        return_value = EXIT_IO_ERROR
        cleanup_fcn(return_value)

    print_metadata(png_object)

    width, height, plane_count = get_dimensions(png_object)
    out_image = transform_image(r, width, height, plane_count)

    f = open(output, 'wb')
    w = png.Writer(width, height)
    w.write(f, numpy.reshape(out_image, (-1, width*plane_count)))
    f.close()

    cleanup_fcn(return_value)

if __name__ == "__main__":
    lokey(cleanup_fcn=lokey_cleanup)
