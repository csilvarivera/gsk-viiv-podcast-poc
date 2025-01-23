import os
import wave

def get_audio_file_paths():
    """" Returns a sorted local array with the path of all the created podcast chapters """
    file_paths = []
    # get all files 
    sorted_files = sorted(os.listdir("tmp/"), key=lambda x: int(x.split('.')[0].split('-')[0]))
    for file in sorted_files:
        if file.endswith(".wav"):
            file_paths.append(os.path.join("tmp/", file))
            print(os.path.join("tmp/", file))
    return file_paths


def concatenate_audio_files(file_paths):
    """ Combines a list of local wav files into one single final podcast file"""
    data = []
    for clip in file_paths:
        w = wave.open(clip, "rb")
        data.append([w.getparams(), w.readframes(w.getnframes())])
        w.close()
    output = wave.open("tmp/output.wav", "wb")
    output.setparams(data[0][0])
    for i in range(len(data)):
        output.writeframes(data[i][1])
    output.close()
    # add output to the file_path
    file_paths.append(os.path.join("tmp/","output.wav"))
    return output

def delete_audio_files(file_paths):
    """  Deletes all tmp files created for the podcast"""
    for file in file_paths:
        os.remove(file)
