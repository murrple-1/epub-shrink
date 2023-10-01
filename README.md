# epub shrink

# Setup

### Using pipenv shell
https://stackoverflow.com/a/49867443/2159808
```
$ pipenv install
$ pipenv shell
```

### By hand
```
$ pip install Pillow
```


# Usage

### Reduce image quality
    $ python epub-shrink/app.py input_file.epub output_file.epub --jpeg-quality=25

### Decrease image size percentwise and cap resulting image size
    $ python epub-shrink/app.py input_file.epub output_file.epub --image-resize-percent=60 --image-max-width=1024

### Cap image size
    $ python epub-shrink/app.py input_file.epub output_file.epub --image-max-width=1024
