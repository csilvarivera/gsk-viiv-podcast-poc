from google.cloud import texttospeech_v1beta1 as texttospeech
from utils import utils_gcs

def create_podcast_chapters(podcast_script):
    """ parses the podcast script in preparation and creates the multi_speaker markup
        conversation
    """
    # get a list of the 
    # print (podcast_script)
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
        # due to the 5000 bytes limitation of the Studio Voices, we need to crea a small clip
        # every 3 sentences. The reason behind this number is anecdotal and based on experience
        # sending requests to the api
        if i > 2:
            multi_speaker_markup = texttospeech.MultiSpeakerMarkup(turns = turns)
            # create small clip with the 4 turns we have 
            synthesise_audio(multi_speaker_markup,p)
            i =0
            p +=1
            turns = []
        i +=1
    # check that we didn't miss one last clip
    if  len(turns) > 0:
        multi_speaker_markup = texttospeech.MultiSpeakerMarkup(turns = turns)
        # create small clip with the remaining turns
        synthesise_audio(multi_speaker_markup,p)
    return multi_speaker_markup


def synthesise_audio(multi_speaker_markup, p):
    """ Generates the MP3 file by calling AudioLM"""
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
   
    # The response's audio_content is binary.
    with open(f"tmp/{p} - output.wav", "wb") as out:
        # Write the response to the output file in the local file system
        out.write(response.audio_content)
    

