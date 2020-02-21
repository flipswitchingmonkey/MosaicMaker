# ffmpeg mosaic maker || 908
# Michael Auerswald @ 908video

import sys
import os
import re
import subprocess
import ffmpeg
import argparse
import PySimpleGUI as sg
from pprint import pprint

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest="in_filename")
    parser.add_argument('-tw', '--width', dest="thumb_w", default="160")
    parser.add_argument('-th', '--height', dest="thumb_h", default="120")
    parser.add_argument('-r', '--rows', dest="rows", default="10")
    parser.add_argument('-c', '--cols', dest="columns", default="6")
    parser.add_argument('-o', '--output', dest="out_filename", default="preview.jpg")
    parser.add_argument('-s', '--sensitivity', dest="sensitivity", default="0.4")
    parser.add_argument('-k', '--keep', dest="keep", default="False")
    parser.add_argument('-q', '--quality', dest="quality", default=4)
    parser.add_argument('--show', dest="show", default="False")
    args = parser.parse_args()

    if len(sys.argv) > 1:
        if args.in_filename is None:
            print("Missing input filename (-i)")
            print("Example: python scenedetect.py -i myvideo.mp4 -o result.jpg -s 0.6 -tw 160 -th 120")
            exit
        processVideo(args)

    else:
        layout = [
                    [sg.Text('Input', size=(15,1)), sg.In(size=(50,1), default_text="D:/video/908_ShowReel_2018_edit_14_MASTER.mp4"), sg.FileBrowse()],
                    [sg.Text('Sensitivity (0=Auto)', size=(15,1)), sg.Slider(range=(0,100),default_value=60,size=(32,15),orientation='horizontal',font=('Helvetica', 10))],
                    [sg.Text('Rows', size=(15,1)), sg.Slider(range=(1,30),default_value=6,size=(32,15),orientation='horizontal',font=('Helvetica', 10))],
                    [sg.Text('Columns', size=(15,1)), sg.Slider(range=(1,30),default_value=6,size=(32,15),orientation='horizontal',font=('Helvetica', 10))],
                    [sg.Text('Thumb Width', size=(15,1)), sg.In(size=(5,1), default_text=320)],
                    [sg.Text('Thumb Height', size=(15,1)), sg.In(size=(5,1), default_text=180)],
                    [sg.Text('Output Folder', size=(15,1)), sg.In(size=(50,1), default_text=os.getcwd()), sg.FolderBrowse()],
                    [sg.Text('Output File', size=(15,1)), sg.In(size=(50,1), default_text="mosaic.jpg")],
                    [sg.Text('Quality (2=Max)', size=(15,1)), sg.Slider(range=(2,31),default_value=4,size=(32,15),orientation='horizontal',font=('Helvetica', 10))],
                    [sg.Checkbox('Also Save Single Images', default=False)],
                    [sg.Checkbox('Show Result', default=True)],
                    [sg.Button('Ok'), sg.Button('Cancel')] ]

        # Create the Window
        window = sg.Window('ffmpeg mosaic maker || 908', layout)
        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            event, values = window.read()
            if event in (None, 'Cancel'):	# if user closes window or clicks cancel
                window.close()
                return
            #print('You entered ', values)
            args.in_filename    = values[0]
            args.sensitivity    = str(float(values[1]) / 100.0) if values[1] > 0 else None
            args.rows           = str(int(values[2]))
            args.columns        = str(int(values[3]))
            args.thumb_w        = str(int(values[4]))
            args.thumb_h        = str(int(values[5]))
            args.quality        = int(values[8])
            args.keep           = values[9]
            args.show           = values[10]
            if values[6] == "":
                values[6] = os.getcwd()
            args.out_filename   = os.path.join(values[6],values[7])
            
            if args.in_filename is None or args.in_filename=="":
                sg.Popup("Missing input filename")
            elif args.out_filename is None or args.out_filename=="" or values[7]=="":
                sg.Popup("Missing output filename")
            else:
                processVideo(args)

        window.close()

def frameListToString(frameList):
    frameListString = ""
    for i in range(len(frameList)):
        frameListString += f"eq(n,{frameList[i]})"
        if i < len(frameList)-1:
            frameListString += "+"
    return frameListString

def processVideo(args):
    imgcount = int(args.rows) * int(args.columns)
    metadata=ffmpeg.probe(os.path.abspath(args.in_filename))
    pprint(metadata)
    framecount = metadata["streams"][0]["nb_frames"]
    framerate = eval(metadata["streams"][0]["avg_frame_rate"])
    every = int(int(framecount) / imgcount)

    frameList = []
    frameListString = ""
    #
    # POPULATE FRAMELIST
    #

    # Simple time interval framelist
    if args.sensitivity is None or args.sensitivity == 0:
        frameList = [(every*i) for i in range(imgcount)]
    
    # Run scene detect filter over video once to find scene changes,
    # then fill up with intermediate frames if not enough to fill mosaic
    else:
        try:
            out, err = (
                ffmpeg
                .input(args.in_filename)
                .video
                .filter('select', 'gt(scene,' + args.sensitivity + ')')
                .filter('showinfo')
                .filter('null')
                .output('-', format="null")
                .run(capture_stdout=True, capture_stderr=True)
            )
            pattern = re.compile(r'(?<=pts_time:)\d*.\d*')

            for line in err.decode("utf-8").split('\n'):
                if line.startswith("[Parsed_showinfo"):
                    reResult = re.search(pattern, line)
                    if reResult is not None:
                        frameTime = float(reResult.group(0))
                        frameList.append(int(frameTime * framerate))

            if len(frameList) < imgcount:
                counter = 0 
                while len(frameList) < imgcount:
                    valA = frameList[counter]
                    counter = (counter + 1) % len(frameList)
                    valB = frameList[counter]
                    if valA >= valB:
                        valB = valA + 2
                    frameList.insert(counter, int((valA+valB)/2.0))
                    counter = (counter + 1) % len(frameList)

        except ffmpeg.Error as e:
                print('stdout:', e.stdout.decode('utf8'))
                print('stderr:', e.stderr.decode('utf8'))
                raise e


    frameListString = frameListToString(frameList)
    print(frameListString)
    print(frameList)
    # ENCODE MOSAIC (based on list of frames)

    out, _ = (
        ffmpeg
        .input(args.in_filename)
        .video
        # .filter('select', 'not(mod(n,' + str(every) + '))')
        .filter('select', frameListString)
        .filter('scale', args.thumb_w, args.thumb_h)
        .filter('tile', args.columns + 'x' + args.rows)
        .output(args.out_filename, vsync=0, vframes=1, **{'qscale:v': args.quality})
        .overwrite_output()
        .run(capture_stdout=True)
    )

    # WRITE SINGLE IMAGES (based on list of frames)
    if args.keep:
        base, filename = os.path.split(args.out_filename)
        basefile, ext = os.path.splitext(filename)
        newFilename = f"{basefile}_%05d{ext}"
        outImageName = os.path.join(base, newFilename)

        out, _ = (
            ffmpeg
            .input(args.in_filename)
            .video
            .filter('select', frameListString)
            .output(outImageName, vsync=0, **{'qscale:v': args.quality})
            .overwrite_output()
            .run(capture_stdout=False)
        )

    if args.show:
        os.startfile(args.out_filename)

main()