import argparse
import io

import ebooklib
from ebooklib import epub

from PIL import Image

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('in_epub_filepath')
    parser.add_argument('out_epub_filepath')
    parser.add_argument('--jpeg-quality', type=int, default=75)

    args = parser.parse_args()

    book = epub.read_epub(args.in_epub_filepath)

    for item in book.get_items_of_type(ebooklib.ITEM_COVER):
        _compress_image_item(item, args)

    for item in book.get_items_of_type(ebooklib.ITEM_IMAGE):
        _compress_image_item(item, args)

    epub.write_epub(args.out_epub_filepath, book)


def _compress_image_item(item, args):
    if item.media_type not in {'image/jpeg', 'image/png'}:
        return

    content = item.get_content()
    if content:
        in_buffer = io.BytesIO(content)
        img = Image.open(in_buffer)

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

if __name__ == '__main__':
    main()
