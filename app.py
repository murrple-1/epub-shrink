import argparse
import os
import io
import logging
import zipfile
import mimetypes

from PIL import Image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('in_epub_filepath')
    parser.add_argument('out_epub_filepath')
    parser.add_argument('-l', '--log-level')
    parser.add_argument('--jpeg-quality', type=int, default=75)
    parser.add_argument('--image-resize-percent', type=int)
    parser.add_argument('--image-resize-resample')

    args = parser.parse_args()

    if args.log_level:
        log_level_num = getattr(logging, args.log_level.upper(), None)
        if type(log_level_num) is not int:
            raise ValueError('Invalid log level: {}'.format(args.log_level))

        logging.basicConfig(level=log_level_num)

    if not os.path.isfile(args.in_epub_filepath):
        raise FileNotFoundError(args.in_epub_filepath)

    if os.path.isdir(args.out_epub_filepath):
        args.out_epub_filepath = os.path.join(
            args.out_epub_filepath, os.path.basename(args.in_epub_filepath))

    if args.out_epub_filepath == args.in_epub_filepath:
        raise FileExistsError(args.out_epub_filepath)

    if args.image_resize_percent:
        args.image_resize_percent /= 100.0

    with zipfile.ZipFile(args.in_epub_filepath, 'r') as in_book:
        with zipfile.ZipFile(args.out_epub_filepath, 'w') as out_book:
            for name in in_book.namelist():
                with in_book.open(name, 'r') as in_file:
                    content = in_file.read()

                    type_, encoding = mimetypes.guess_type(name)

                    if type_:
                        type_, subtype = type_.split('/')

                        if type_ == 'image':
                            content = _compress_image(subtype, content, args)

                    out_book.writestr(name, content)


def _compress_image(subtype, old_content, args):
    if subtype not in {'jpeg', 'jpg', 'png'}:
        return old_content

    in_buffer = io.BytesIO(old_content)
    img = Image.open(in_buffer)

    if args.image_resize_percent:
        original_size = img.size
        new_size = (int(original_size[0] * args.image_resize_percent),
                    int(original_size[1] * args.image_resize_percent))
        logging.info('old size: %s', original_size)
        logging.info('new size: %s', new_size)

        resample = None
        if args.image_resize_resample:
            resample_attr = args.image_resize_resample.upper()
            if not hasattr(Image, resample_attr):
                raise ValueError('unknown resample mode: {}'.format(
                    args.image_resize_resample))

            resample = getattr(Image, resample_attr)

        img = img.resize(new_size, resample)

    format_ = None
    params = {}
    if subtype == 'jpeg' or subtype == 'jpg':
        format_ = 'JPEG'
        params['quality'] = args.jpeg_quality
        params['optimize'] = True
    elif subtype == 'png':
        format_ = 'PNG'
        params['optimize'] = True

    out_buffer = io.BytesIO()
    img.save(out_buffer, format_, **params)

    new_content = out_buffer.getvalue()

    logging.info('old content length: %s', len(old_content))
    logging.info('new content length: %s', len(new_content))

    return new_content


if __name__ == '__main__':
    main()
