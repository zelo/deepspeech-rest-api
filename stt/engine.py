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

    def run(self, audio):
        audio = self.normalize_audio(audio)
        audio = BytesIO(audio)
        with wave.Wave_read(audio) as wav:
            audio = np.frombuffer(wav.readframes(wav.getnframes()), np.int16)
        result = self.model.stt(audio_buffer=audio)
        return result
