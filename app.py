import argparse
import io
import logging

import ebooklib
from ebooklib import epub

from PIL import Image

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('in_epub_filepath')
    parser.add_argument('out_epub_filepath')
    parser.add_argument('-l', '--log-level')
    parser.add_argument('--jpeg-quality', type=int, default=75)
    parser.add_argument('--image-resize-percent', type=int)

    args = parser.parse_args()

    if args.log_level:
        log_level_num = getattr(logging, args.log_level.upper(), None)
        if not isinstance(log_level_num, int):
            raise ValueError('Invalid log level: {}'.format(args.log_level))

        logging.basicConfig(level=log_level_num)

    if args.image_resize_percent:
        args.image_resize_percent /= 100.0

    book = epub.read_epub(args.in_epub_filepath)

    for item in book.get_items_of_type(ebooklib.ITEM_COVER):
        _compress_image_item(item, args)

    for item in book.get_items_of_type(ebooklib.ITEM_IMAGE):
        _compress_image_item(item, args)

    epub.write_epub(args.out_epub_filepath, book)


def _compress_image_item(item, args):
    if item.media_type not in {'image/jpeg', 'image/png'}:
        return

    old_content = item.get_content()
    if old_content:
        in_buffer = io.BytesIO(old_content)
        img = Image.open(in_buffer)

        if args.image_resize_percent:
            original_size = img.size
            new_size = (int(original_size[0] * args.image_resize_percent), int(original_size[1] * args.image_resize_percent))
            logging.info('old size: %s', original_size)
            logging.info('new size: %s', new_size)

            img = img.resize(new_size)

        format_ = None
        params = {}
        if item.media_type == 'image/jpeg':
            format_ = 'JPEG'
            params['quality'] = args.jpeg_quality
            params['optimize'] = True
        elif item.media_type == 'image/png':
            format_ = 'PNG'
            params['optimize'] = True

        out_buffer = io.BytesIO()
        img.save(out_buffer, format_, **params)

        item.content = out_buffer.getvalue()

        logging.info('old content length: %s', len(old_content))
        logging.info('new content length: %s', len(item.content))

if __name__ == '__main__':
    main()
