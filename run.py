import datetime as dt
import glob
import json
import os

import PySimpleGUI as sg
import numpy as np
from time import sleep
import cv2

import src.start_video as sv
import src.Blockchain.api as blockchain_api
from src.FrameHash import FrameHash
from src.verify import verify
from src.add_metadata import add_metadata
from src.assets.recording_gif_base64 import recording_gif


def send_tx(last_t):
    send_freq = 5
    return last_t + dt.timedelta(0, send_freq) <= dt.datetime.now()


def _clear_directory():
    files = glob.glob('out/*.mp4')
    for f in files:
        os.remove(f)


def main():
    global end_t, fh, verify_t
    bc_api = blockchain_api.API()

    sg.theme('Material1')
    # define the window layout
    layout = [[sg.Image(filename='src/assets/Demo_welcome.png', key='image')],
              [sg.Text('', key="_RECITE_TEXT_BOX_", font='Ubuntu 14', size=(50, 2))],
              [sg.Submit('Record', size=(10, 1), font='Ubuntu 14'),
               sg.Button('Exit', size=(10, 1), font='Ubuntu 14'),
               sg.Image(data=recording_gif, visible=False, key='_IMAGE_'), ],
              [sg.Text('Select video file', size=(14, 1), font='Ubuntu 12'),
               sg.FileBrowse(key="-IN-", file_types=(("mp4 video files", "*.mp4"),), size=(10, 1), font='Ubuntu 14'),
               sg.Submit('Verify', size=(10, 1), font='Ubuntu 14')], ]

    # create the window and show it without the plot
    window = sg.Window('Quitelive Demo', layout, location=(800, 400))

    # --- Event LOOP Read and display frames, operate the GUI --- #
    cap = cv2.VideoCapture(0)
    recording = False
    last_t = 0
    record_duration = 60
    recite_time = 15
    reciting = False
    while True:
        event, values = window.read(timeout=5)
        bc_api.random_mine()  # has a random node mine every 10 seconds, enabling a 10 second approx block time

        if event == 'Exit' or event == sg.WIN_CLOSED:
            window.close()
            return

        elif event == 'Record':
            _clear_directory()
            sv.start(record_duration)
            last_t = dt.datetime.now()
            end_t = last_t + dt.timedelta(0, record_duration)
            verify_t = end_t - dt.timedelta(0, recite_time)
            fh = FrameHash("out/out.md5")
            recording = True
            window.Element('_IMAGE_').update(visible=True)
            window['Record'].update(disabled=True)
            window['Verify'].update(disabled=True)

        elif event == 'Verify':
            window['Record'].update(disabled=True)
            window['Verify'].update(disabled=True)
            print("video merkle root")
            video_file = verify(values["-IN-"])

            with open('out/metadata.json') as json_file:
                metadata = json.load(json_file)
                matches = 0
                for i, merkle_root in enumerate(metadata["merkle_roots"]):
                    if merkle_root['merkle_root'] == video_file[i]['merkle_root']:
                        print("Hash {} matches".format(merkle_root['merkle_root']))
                        matches += 1
                    else:
                        print("hash does not match: {} != {}".format(merkle_root['merkle_root'],
                                                                     video_file[i]['merkle_root']))
            result = "{} out of {} hashes correct".format(matches, len(metadata["merkle_roots"]))
            window.Element("_RECITE_TEXT_BOX_").update(result)

        if recording:
            ret, frame = cap.read()
            img_bytes = cv2.imencode('.png', frame)[1].tobytes()
            window['image'].update(data=img_bytes)
            if send_tx(last_t) and not reciting:
                last_t = dt.datetime.now()
                fh.compute_root()
                bc_api.transact("quitelive", "quitelive", .0000001, fh.get_roots()[-1])  # thread this?

            if dt.datetime.now() > verify_t and not reciting:
                reciting = True
                wordlist = bc_api.get_recite_words()
                window.Element("_RECITE_TEXT_BOX_").update(wordlist)

            if dt.datetime.now() >= end_t:
                print("done")
                recording = False
                img = np.full((480, 640), 255)
                # this is faster, shorter and needs less includes
                img_bytes = cv2.imencode('.png', img)[1].tobytes()
                window['image'].update(data=img_bytes)
                sleep(1)  # error with writing metadata before file is saved
                add_metadata(fh.get_roots(), bc_api.tx_ids)
                return
            window.Element('_IMAGE_').UpdateAnimation(recording_gif, time_between_frames=500)


main()
