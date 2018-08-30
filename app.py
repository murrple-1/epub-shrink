import argparse

import ebooklib
from ebooklib import epub


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('epub_filepath')

    args = parser.parse_args()

    book = epub.read_epub(args.epub_filepath)

    for item in book.get_items_of_type(ebooklib.ITEM_COVER):
        print(item)
        print(len(item.get_content()))
        print(item.media_type)

    for item in book.get_items_of_type(ebooklib.ITEM_IMAGE):
        print(item)
        print(len(item.get_content()))
        print(item.media_type)


if __name__ == '__main__':
    main()
