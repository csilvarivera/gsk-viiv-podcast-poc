# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from utils.parse_config import TEMP_FOLDER
import os
import wave

def get_audio_file_paths():
    """" Returns a sorted local array with the path of all the created podcast chapters """
    file_paths = []
    # get all files 
    sorted_files = sorted(os.listdir(f"{TEMP_FOLDER}/"), key=lambda x: int(x.split('.')[0].split('-')[0]))
    for file in sorted_files:
        if file.endswith(".wav"):
            file_paths.append(os.path.join(f"{TEMP_FOLDER}/", file))
    print(file_paths)
    return file_paths


def concatenate_audio_files(file_paths):
    """ Combines a list of local wav files into one single final podcast file"""
    data = []
    for clip in file_paths:
        w = wave.open(clip, "rb")
        data.append([w.getparams(), w.readframes(w.getnframes())])
        w.close()
    output = wave.open(f"{TEMP_FOLDER}/output.wav", "wb")
    output.setparams(data[0][0])
    for i in range(len(data)):
        output.writeframes(data[i][1])
    output.close()
    # add output to the file_path
    file_paths.append(os.path.join(f"{TEMP_FOLDER}/","output.wav"))
    return output

def delete_audio_files():
    """  Deletes all tmp files created for the podcast"""
    files = os.listdir(f"{TEMP_FOLDER}/")
    for file in files:
        if file.endswith(".wav"):
            os.remove(os.path.join(f"{TEMP_FOLDER}/", file))