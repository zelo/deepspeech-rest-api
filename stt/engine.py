from argparse import PARSER
import argparse
import json
import sys
import wave
from io import BytesIO
from pathlib import Path

import ffmpeg
import numpy as np
from deepspeech import Model


class SpeechToTextEngine:
    def __init__(self):
        self.model = Model(model_path=Path(__file__).parents[1].joinpath('model.pbmm').absolute().as_posix())

    def normalize_audio(self, audio):
        out, err = ffmpeg.input('pipe:0') \
            .output('pipe:1', f='WAV', acodec='pcm_s16le', ac=1, ar='16k', loglevel='error', hide_banner=None) \
            .run(input=audio, capture_stdout=True, capture_stderr=True)
        if err:
            raise Exception(err)
        return out

    def words_from_candidate_transcript(self,metadata):
        word = ""
        word_list = []
        word_start_time = 0
        # Loop through each character
        for i, token in enumerate(metadata.tokens):
            # Append character to word if it's not a space
            if token.text != " ":
                if len(word) == 0:
                    # Log the start time of the new word
                    word_start_time = token.start_time

                word = word + token.text
            # Word boundary is either a space or the last character in the array
            if token.text == " " or i == len(metadata.tokens) - 1:
                word_duration = token.start_time - word_start_time

                if word_duration < 0:
                    word_duration = 0

                each_word = dict()
                each_word["word"] = word
                each_word["start_time"] = round(word_start_time, 4)
                each_word["duration"] = round(word_duration, 4)

                word_list.append(each_word)
                # Reset
                word = ""
                word_start_time = 0

        return word_list
    
    def metadata_json_output(self,metadata):
        json_result = dict()
        json_result["transcripts"] = [{
            "confidence": transcript.confidence,
            "words": self.words_from_candidate_transcript(transcript),
        } for transcript in metadata.transcripts]
        return json.dumps(json_result, indent=2)

    def run(self, audio):
        audio = self.normalize_audio(audio)
        audio = BytesIO(audio)
        with wave.Wave_read(audio) as wav:
            audio = np.frombuffer(wav.readframes(wav.getnframes()), np.int16)

        parser = argparse.ArgumentParser(description='Running DeepSpeech inference.')
        parser.add_argument('--model', required=False,
                            help='Path to the model (protocol buffer binary file)',)
        parser.add_argument('--scorer', required=False,
                            help='Path to the external scorer file')
        parser.add_argument('--audio', required=False,
                            help='Path to the audio file to run (WAV format)')
        parser.add_argument('--beam_width', type=int,
                            help='Beam width for the CTC decoder')
        parser.add_argument('--lm_alpha', type=float,
                            help='Language model weight (lm_alpha). If not specified, use default from the scorer package.')
        parser.add_argument('--lm_beta', type=float,
                            help='Word insertion bonus (lm_beta). If not specified, use default from the scorer package.')
        parser.add_argument('--extended', required=False, action='store_true',
                            help='Output string from extended metadata')
        parser.add_argument('--json', required=False, action='store_true',
                            help='Output json from metadata with timestamp of each word')
        parser.add_argument('--candidate_transcripts', type=int, default=3,
                            help='Number of candidate transcripts to include in JSON output')
        parser.add_argument('--hot_words', type=str,
                            help='Hot-words and their boosts.')
        args = parser.parse_args()
        
        # sphinx-doc: python_ref_model_start
        #ds = Model(args.model)
        #result_plain = self.model.stt(audio_buffer=audio)
        result_stamp = self.metadata_json_output(self.model.sttWithMetadata(audio, args.candidate_transcripts))
        result = result_stamp
        return result
