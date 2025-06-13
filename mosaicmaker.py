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

_WINDOW = None

def main():
    global _WINDOW

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest="in_filename", help="Input video file (any file format that ffmpeg can handle)")
    parser.add_argument('-tw', '--width', dest="thumb_w", default=320, help="Width of each mosaic piece")
    parser.add_argument('-th', '--height', dest="thumb_h", default=180, help="Height of each mosaic piece")
    parser.add_argument('-r', '--rows', dest="rows", default=6, help="Number of rows in the mosaic")
    parser.add_argument('-c', '--cols', dest="columns", default=6, help="Number of columns in the mosaic")
    parser.add_argument('-o', '--output', dest="out_filename", default=os.path.join(os.getcwd(), "mosaic.jpg"), help="Output filename (extension sets encoder, if in doubt use .jpg)")
    parser.add_argument('-s', '--sensitivity', dest="sensitivity", default=0.6, help="Set scene detection sensitivity, 0 means scene detection is off.")
    parser.add_argument('-k', '--keep', dest="keep", default=False, help="Keep the 'mosaic pieces' as seperate full res files as well")
    parser.add_argument('-q', '--quality', dest="quality", default=4, help="Image encoder quality, from 2-31 for Jpeg. 2-5 recommended.")
    parser.add_argument('--show', dest="show", default=True, help="Open resulting mosaic in default viewer")
    parser.add_argument('--meta', dest="meta", default=False, help="Output metadata of video file")
    args = parser.parse_args()

    if len(sys.argv) > 1:
        if args.in_filename is None:
            print("Missing input filename (-i)")
            print("Example: python scenedetect.py -i myvideo.mp4 -o result.jpg -s 0.6 -tw 160 -th 120")
            exit()
        args.sensitivity    = str(args.sensitivity)
        args.rows           = str(args.rows)
        args.columns        = str(args.columns)
        args.thumb_w        = str(args.thumb_w)
        args.thumb_h        = str(args.thumb_h)
        args.quality        = str(args.quality)
        processVideo(args)

    else:
        pprint(args)
        layout = [
                    [sg.Text('Input', size=(15,1)), sg.In(size=(50,1), default_text="", enable_events=True, key="inputFileName"), sg.FileBrowse()],
                    [sg.Text('Sensitivity (0=Auto)', size=(15,1)), sg.Slider(key="sensitivity",range=(0,100),default_value=(args.sensitivity*100),size=(32,15),orientation='horizontal',font=('Helvetica', 10))],
                    [sg.Text('Rows', size=(15,1)), sg.Slider(key="rows",range=(1,30),default_value=args.rows,size=(32,15),orientation='horizontal',font=('Helvetica', 10))],
                    [sg.Text('Columns', size=(15,1)), sg.Slider(key="columns",range=(1,30),default_value=args.columns,size=(32,15),orientation='horizontal',font=('Helvetica', 10))],
                    [sg.Text('Thumb Dimensions', size=(15,1)),  sg.Text('Width',size=(5,1)), sg.In(key="thumbw",size=(5,1), default_text=args.thumb_w), sg.Text('Height',size=(5,1)), sg.In(key="thumbh",size=(5,1), default_text=args.thumb_h)],
                    [sg.Text('Output Folder', size=(15,1)), sg.In(size=(50,1), default_text=os.path.join(os.getcwd(), 'output'), key="outputFolder"), sg.FolderBrowse()],
                    [sg.Text('Output File', size=(15,1)), sg.In(size=(50,1), default_text="mosaic.jpg", key="outputFileName")],
                    [sg.Text('Quality (2=Max)', size=(15,1)), sg.Slider(key="quality",range=(2,31),default_value=args.quality,size=(32,15),orientation='horizontal',font=('Helvetica', 10))],
                    [sg.Checkbox('Also Save Single Images', default=args.keep, key="keep")],
                    [sg.Checkbox('Show Result', default=args.show, key="show")],
                    [sg.Text('Progress', size=(15,1)), sg.ProgressBar(100, orientation='h', size=(10, 20), key='progress_detect'), sg.ProgressBar(100, orientation='h', size=(10, 20), key='progress_mosaic'), sg.ProgressBar(100, orientation='h', size=(10, 20), key='progress_single')],
                    [sg.Text('', size=(15,1)), sg.Text('Detect', size=(18,1), font=('Helvetica', 8)), sg.Text('Mosaic', size=(18,1), font=('Helvetica', 8)), sg.Text('Single', size=(18,1), font=('Helvetica', 8))],
                    [sg.Button('Ok', key="Ok"), sg.Button('Close')] ]

        # Create the Window
        _WINDOW = sg.Window('ffmpeg mosaic maker || 908', layout)
        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            if _WINDOW is None:
                break
            result = _WINDOW.read()
            if result is None:
                break
            event, values = result

            if event == sg.WINDOW_CLOSED or event == 'Quit' or event == 'Close':
                break

            elif event == "Ok":
                args.in_filename    = values["inputFileName"]
                args.sensitivity    = str(float(values["sensitivity"]) / 100.0) if values["sensitivity"] > 0 else None
                args.rows           = str(int(values["rows"]))
                args.columns        = str(int(values["columns"]))
                args.thumb_w        = str(int(values["thumbw"]))
                args.thumb_h        = str(int(values["thumbh"]))
                args.quality        = int(values["quality"])
                args.keep           = values["keep"]
                args.show           = values["show"]
                if values["outputFileName"] == "":
                    values["outputFileName"] = os.getcwd()
                if not os.path.exists(values["outputFolder"]):
                    print(f"Creating missing output folder: {values["outputFolder"]}")
                    os.makedirs(values["outputFolder"], exist_ok=True)
                args.out_filename   = os.path.join(values["outputFolder"],values["outputFileName"])
                
                if args.in_filename is None or args.in_filename=="":
                    sg.Popup("Missing input filename")
                elif args.out_filename is None or args.out_filename=="" or values["outputFileName"]=="":
                    sg.Popup("Missing output filename")
                else:
                    processVideo(args)

            elif event == "inputFileName":
                _WINDOW["outputFileName"].update(buildOutputFilename(values["inputFileName"], values["outputFileName"]))

        _WINDOW.close()

def buildOutputFilename(s, previous):
    base, filename = os.path.split(s)
    basefile, _ = os.path.splitext(filename)
    _, ext = os.path.splitext(previous)
    if ext == "":
        ext = ".jpg"
    newFilename = f"{basefile}_mosaic{ext}"
    return newFilename

def frameListToString(frameList):
    frameListString = ""
    for i in range(len(frameList)):
        frameListString += f"eq(n,{frameList[i]})"
        if i < len(frameList)-1:
            frameListString += "+"
    return frameListString

def getBasicFrameList(every, imgcount):
    return [(every*i) for i in range(imgcount)]


def processSceneDetectOutput(p, framerate):
    frameList = []
    sceneDetectFrameTimePattern = re.compile(r'(?<=pts_time:)\d*.\d*')

    while True:
        in_bytes = p.stderr.read(256)
        if not in_bytes:
            break
        line = in_bytes.decode("utf-8")
        reResult = re.search(sceneDetectFrameTimePattern, line)
        if reResult is not None:
            frameTime = float(reResult.group(0))
            frameList.append(int(frameTime * framerate))
            print(f"Detected scene change at {frameTime}s")
            if _WINDOW:
                _WINDOW["progress_detect"].UpdateBar(int(frameTime * framerate))
                _WINDOW.refresh()
    
    return frameList

def processEncodingOutput(pMosaic, pSingle=None, framerate=25):
    framePattern = re.compile(r'(frame=\s*)(\d*)')
    ptsTimePattern = re.compile(r'(?<=pts_time:)\d*.\d*')
    
    someCounter = 0
    
    while True:
        in_bytes_single = None
        in_bytes_mosaic = None

        if pMosaic is not None:
            in_bytes_mosaic = pMosaic.stderr.read(256)
        if pSingle is not None:
            in_bytes_single = pSingle.stderr.read(256)

        if not in_bytes_mosaic and not in_bytes_single:
            break

        if in_bytes_mosaic is not None:
            line_mosaic = in_bytes_mosaic.decode("utf-8")
            reResult = re.search(framePattern, line_mosaic)
            # pprint(reResult)
            if reResult is not None:
                try:
                    frame = int(reResult.group(2))
                    if frame == 0:
                        print(f"Mosaic: Processing...")
                        if _WINDOW:
                            someCounter += 5  # we are not getting a truely usable update from ffmpeg here, so let's just move the progress along somewhat...
                            _WINDOW["progress_mosaic"].UpdateBar(someCounter)
                            _WINDOW.refresh()
                    else:
                        print(f"Mosaic: Processing Finished")
                        if _WINDOW:
                            _WINDOW["progress_mosaic"].UpdateBar(100)
                            _WINDOW.refresh()
                except:
                    pass
        
        if in_bytes_single is not None:
            line_single = in_bytes_single.decode("utf-8")
            reResult = re.search(ptsTimePattern, line_single)
            if reResult is not None:
                try:
                    frame = float(reResult.group(0))
                    print(f"Writing single image at {frame}s")
                    if _WINDOW:
                        _WINDOW["progress_single"].UpdateBar(int(frameTime * framerate))
                        _WINDOW.refresh()
                except:
                    pass


def processVideo(args):
    if _WINDOW:
        _WINDOW["Ok"].Update(disabled=True)
        _WINDOW["Close"].Update(disabled=True)
        _WINDOW.refresh()

    imgcount = int(args.rows) * int(args.columns)
    metadata=ffmpeg.probe(os.path.abspath(args.in_filename))
    if args.meta: pprint(metadata)
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
        frameList = getBasicFrameList(every, imgcount)
    
    # Run scene detect filter over video once to find scene changes,
    # then fill up with intermediate frames if not enough to fill mosaic
    else:
        process_ffmpeg = (
            ffmpeg
            .input(args.in_filename)
            .video
            .filter('select', 'gt(scene,' + args.sensitivity + ')')
            .filter('showinfo')
            .filter('null')
            .output('-', format="null")
            .run_async(pipe_stderr=True)
        )
        if _WINDOW:
            _WINDOW["progress_detect"].UpdateBar(0,framecount)
            _WINDOW.refresh()
        frameList = processSceneDetectOutput(process_ffmpeg, framerate)
        if _WINDOW:
            _WINDOW["progress_detect"].UpdateBar(framecount)
            _WINDOW.refresh()

        if len(frameList) < imgcount/2:
            frameList = frameList + (getBasicFrameList(every, imgcount))
            frameList.sort()
        elif len(frameList) < imgcount:
            counter = 0 
            while len(frameList) < imgcount:
                valA = frameList[counter]
                counter = (counter + 1) % len(frameList)
                valB = frameList[counter]
                if valA >= valB:
                    valB = valA + 2
                frameList.insert(counter, int((valA+valB)/2.0))
                counter = (counter + 1) % len(frameList)

    frameListString = frameListToString(frameList)
    
    # ENCODE MOSAIC (based on list of frames)

    process_mosaic = (
        ffmpeg
        .input(args.in_filename)
        .video
        .filter('select', frameListString)
        .filter('showinfo')
        .filter('scale', args.thumb_w, args.thumb_h)
        .filter('tile', args.columns + 'x' + args.rows)
        .output(args.out_filename, vsync=0, vframes=1, **{'qscale:v': args.quality})
        .overwrite_output()
        .run_async(pipe_stderr=True)
    )

    # WRITE SINGLE IMAGES (based on list of frames)
    process_single = None
    if args.keep:
        base, filename = os.path.split(args.out_filename)
        basefile, ext = os.path.splitext(filename)
        newFilename = f"{basefile}_%05d{ext}"
        outImageName = os.path.join(base, newFilename)

        process_single = (
            ffmpeg
            .input(args.in_filename)
            .video
            .filter('select', frameListString)
            .filter('showinfo')
            .output(outImageName, vsync=0, **{'qscale:v': args.quality})
            .overwrite_output()
            .run_async(pipe_stderr=True)
        )

    if _WINDOW:
            _WINDOW["progress_single"].UpdateBar(0,framecount)
            _WINDOW.refresh()
    processEncodingOutput(process_mosaic, process_single, framerate)
    if _WINDOW:
            _WINDOW["progress_single"].UpdateBar(framecount)
            _WINDOW.refresh()

    if _WINDOW:
        _WINDOW["Ok"].Update(disabled=False)
        _WINDOW["Close"].Update(disabled=False)
        _WINDOW.refresh()

    if args.show:
        if sys.platform.startswith('win'):
            os.startfile(args.out_filename)
        elif sys.platform.startswith('darwin'):
            subprocess.call(['open', args.out_filename])
        else:
            subprocess.call(['xdg-open', args.out_filename])

main()
