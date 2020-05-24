from os import getenv
from pathlib import Path
from subprocess import run
from tempfile import NamedTemporaryFile
import wave

from deepspeech import Model
import numpy as np


MODEL_PATH = Path(getenv('MODEL_PATH', Path(__file__).parents[1].joinpath('model.pbmm').absolute()))
FFMPEG_PATH = getenv('FFMPEG_PATH', 'ffmpeg')


class SpeechToTextEngine:
    def __init__(self):
        self.model = Model(model_path=MODEL_PATH.as_posix())

    def run(self, audio):
        with NamedTemporaryFile() as in_file, NamedTemporaryFile() as out_file:
            in_file.write(audio)
            # TODO: consider piping data, but in some cases ffmpeg whines about missing headers
            cmd = (f"{FFMPEG_PATH} -loglevel error -hide_banner -i {in_file.name}"
                   f" -y -f WAV -ar 16000 -ac 1 {out_file.name}")
            run(cmd.split(), check=True)
            with wave.open(out_file.name, 'rb') as wav:
                audio = np.frombuffer(wav.readframes(wav.getnframes()), np.int16)
            result = self.model.stt(audio_buffer=audio)
            return result
