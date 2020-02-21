# MosaicMaker
Simple Python script to automate video preview mosaics

Can be run from the command line or using a [PySimpleGUI](https://pysimplegui.readthedocs.io/en/latest/) UI.
Sensitivity > 0 will run the video through a scene detect filter first, then interpolate frames if not enough scene changes were found to fill up the mosaic.
Sensitivity == 0 just takes frames distributed evenly over the duration of the video

To install:

    pip install ffmpeg-python
    pip install PySimpleGUI

Make sure ffmpeg.exe and ffprobe.exe are either somewhere in the path or in the same directory as the mosaicmaker.py file

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

Here's what the GUI looks like:
![GUI](https://github.com/flipswitchingmonkey/MosaicMaker/screenshots/Mosaic_GUI.png "MosaicMaker GUI")

And this is what you get out of it:
![GUI](https://github.com/flipswitchingmonkey/MosaicMaker/screenshots/Mosaic_Result.jpg "MosaicMaker Result")

Also Save Single Images gives you every image seperately as well:
![GUI](https://github.com/flipswitchingmonkey/MosaicMaker/screenshots/Mosaic_SaveImages.jpg "MosaicMaker Save Images")
