"""Tests to ensure file-not-found (WinError 2) errors are handled gracefully.
"""
import pytest
import os

from core.asr.transcription_service import transcribe_audio
from core.asr.phowhisper_service import transcribe_phowhisper

class DummyModelRaising:
    def __call__(self, *args, **kwargs):
        raise OSError(2, "No such file or directory")

class DummyWhisperModel:
    def transcribe(self, *args, **kwargs):
        raise OSError(2, "No such file or directory")


def test_transcribe_audio_handles_oserror_file_not_found(tmp_path, caplog):
    # Create a small temp wav file
    wav = tmp_path / "test.wav"
    wav.write_bytes(b"RIFF\x00\x00\x00\x00WAVE")  # tiny invalid WAV header but exists on disk

    model = DummyWhisperModel()
    res = transcribe_audio(model, str(wav), sr=16000, language="vi")
    assert res is None


def test_transcribe_phowhisper_handles_oserror_file_not_found(tmp_path, caplog):
    wav = tmp_path / "test.wav"
    wav.write_bytes(b"RIFF\x00\x00\x00\x00WAVE")

    dummy = DummyModelRaising()
    res = transcribe_phowhisper(dummy, str(wav), sr=16000, language="vi")
    assert res is None
