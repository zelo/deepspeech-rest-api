from os import getenv
from pathlib import Path
from subprocess import run
from tempfile import NamedTemporaryFile
import wave

from deepspeech import Model
from deepspeech.client import N_FEATURES, N_CONTEXT, BEAM_WIDTH, LM_ALPHA, LM_BETA
import numpy as np


MODEL_DIR = Path(getenv('MODEL_DIR', Path(__file__).parents[1].joinpath('model').absolute()))
FFMPEG_PATH = getenv('FFMPEG_PATH', 'ffmpeg')


class SpeechToTextEngine:
    def __init__(self):
        model_path = MODEL_DIR.joinpath('output_graph.pbmm').as_posix()
        alphabet_path = MODEL_DIR.joinpath('alphabet.txt').as_posix()
        lm_path = MODEL_DIR.joinpath('lm.binary').as_posix()
        trie_path = MODEL_DIR.joinpath('trie').as_posix()
        self.model = Model(
            aModelPath=model_path,
            aNCep=N_FEATURES,
            aNContext=N_CONTEXT,
            aAlphabetConfigPath=alphabet_path,
            aBeamWidth=BEAM_WIDTH
        )
        self.model.enableDecoderWithLM(
            aAlphabetConfigPath=alphabet_path,
            aLMPath=lm_path,
            aTriePath=trie_path,
            aLMWeight=LM_ALPHA,
            aValidWordCountWeight=LM_BETA
        )

    def run(self, audio):
        sample_rate = 16000
        with NamedTemporaryFile() as in_file, NamedTemporaryFile() as out_file:
            in_file.write(audio)
            # TODO: consider piping data, but in some cases ffmpeg whines about missing headers
            cmd = (f"{FFMPEG_PATH} -loglevel error -hide_banner -i {in_file.name}"
                   f" -y -f WAV -ar {sample_rate} -ac 1 {out_file.name}")
            run(cmd.split(), check=True)
            with wave.open(out_file.name, 'rb') as wav:
                audio = np.frombuffer(wav.readframes(wav.getnframes()), np.int16)
            result = self.model.stt(aBuffer=audio, aSampleRate=sample_rate)
            return result
