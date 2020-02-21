# MosaicMaker
Simple Python script to automate video preview mosaics

Can be run from the command line or using a [PySimpleGUI](https://pysimplegui.readthedocs.io/en/latest/) UI.
Sensitivity > 0 will run the video through a scene detect filter first, then interpolate frames if not enough scene changes were found to fill up the mosaic.
Sensitivity == 0 just takes frames distributed evenly over the duration of the video

Requires ffmpeg.exe and ffprobe.exe either somewhere in the path or in the same directory as the mosaicmaker.py file

    usage: mosaicmaker.py [-h] [-i IN_FILENAME] [-tw THUMB_W] [-th THUMB_H]
                          [-r ROWS] [-c COLUMNS] [-o OUT_FILENAME]
                          [-s SENSITIVITY] [-k KEEP] [-q QUALITY] [--show SHOW]

    optional arguments:
      -h, --help            show this help message and exit
      -i IN_FILENAME, --input IN_FILENAME
      -tw THUMB_W, --width THUMB_W
      -th THUMB_H, --height THUMB_H
      -r ROWS, --rows ROWS
      -c COLUMNS, --cols COLUMNS
      -o OUT_FILENAME, --output OUT_FILENAME
      -s SENSITIVITY, --sensitivity SENSITIVITY
      -k KEEP, --keep KEEP
      -q QUALITY, --quality QUALITY
      --show SHOW
