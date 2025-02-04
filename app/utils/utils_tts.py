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

from google.cloud import texttospeech_v1beta1 as texttospeech
from utils.parse_config import TEMP_FOLDER
import os

def create_podcast_chapters(podcast_script):
    """ parses the podcast script in preparation and creates the multi_speaker markup
        conversation
    """
    podcast_list = podcast_script.split ("|")
    turns = []
    i = 0
    p =0
    for turn in podcast_list:
        if (turn.lstrip().startswith("[-]")):
            # remove the speaker indicator
            clean_turn = turn.split("[-]")[1]
            # create the turn
            print (clean_turn)
            tts_turn = texttospeech.MultiSpeakerMarkup.Turn(
                text= clean_turn,
                speaker="R",
            )
            turns.append(tts_turn)
        elif (turn.lstrip().startswith("[+]")):
            # remove the speaker indicator
            clean_turn = turn.split("[+]")[1]
            # create the turn
            print (clean_turn)
            tts_turn = texttospeech.MultiSpeakerMarkup.Turn(
                text= clean_turn,
                speaker="S",
            )
            turns.append(tts_turn)
        # due to the 5000 bytes limitation of the Studio Voices, we need to create a small clip
        # every 3 sentences. The reason behind this number is anecdotal and based on experience
        # sending requests to the api
        if i > 2:
            multi_speaker_markup = texttospeech.MultiSpeakerMarkup(turns = turns)
            # create small clip with the 4 turns we have 
            synthesize_audio(multi_speaker_markup,p)
            i =0
            p +=1
            turns = []
        i +=1
    # check that we didn't miss one last clip
    if  len(turns) > 0:
        multi_speaker_markup = texttospeech.MultiSpeakerMarkup(turns = turns)
        # create small clip with the remaining turns
        synthesize_audio(multi_speaker_markup,p)
    return multi_speaker_markup

def synthesize_audio(_multi_speaker_markup, p):
    multi_speaker_markup = _multi_speaker_markup
    """ Generates the WAV file by calling AudioLM"""
    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

        # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(
        multi_speaker_markup=multi_speaker_markup
    )

    # Build the voice request, select the language code ('en-US') and the voice
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", name="en-US-Studio-MultiSpeaker"
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    
    # If the temporary directory does not exist, let's create it
    os.makedirs(TEMP_FOLDER, exist_ok=True)

    # The response's audio_content is binary.
    with open(f"{TEMP_FOLDER}/{p} - output.wav", "wb") as out:
        # Write the response to the output file in the local file system
        out.write(response.audio_content)
    

