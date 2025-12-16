"""Tests to simulate Librosa FFmpeg checks and related fallback logic.

These tests mock `librosa.load` and `soundfile.read` to exercise
`check_ffmpeg_for_librosa()` scenarios:
- transient Windows file-lock (WinError 32) with retry success
- FFmpeg-missing error that triggers `ensure_ffmpeg()` and then succeeds
- fallback to `soundfile.read` when `librosa.load` fails for unrelated reasons

Run with: pytest -q
"""
import numpy as np
import pytest

from core.asr.phowhisper_service import check_ffmpeg_for_librosa
import core.asr.phowhisper_service as phow


def test_winerror_retry_success(monkeypatch):
    calls = {"n": 0}

    def fake_load(path, sr):
        calls["n"] += 1
        # Fail with WinError 32 for the first two attempts, then succeed
        if calls["n"] < 3:
            raise OSError(32, "The process cannot access the file because it is being used by another process")
        return np.zeros(16000, dtype=np.float32), 16000

    monkeypatch.setattr(phow.librosa, "load", fake_load)

    ok, msg = check_ffmpeg_for_librosa()

    assert ok is True
    assert "Librosa có thể load audio" in msg or "FFmpeg OK" in msg


def test_ffmpeg_missing_triggers_ensure_ffmpeg_then_success(monkeypatch):
    calls = {"n": 0}

    def fake_load(path, sr):
        calls["n"] += 1
        # First call: raise ffmpeg-not-found error, second call: succeed
        if calls["n"] == 1:
            raise Exception("ffmpeg was not found but is required to load audio files from filename")
        return np.zeros(16000, dtype=np.float32), 16000

    monkeypatch.setattr(phow.librosa, "load", fake_load)

    ensured = {"called": False}

    def fake_ensure(silent=True, verbose=False):
        ensured["called"] = True
        return True, {"ffmpeg_path": "fake", "verified": True}

    monkeypatch.setattr(phow, "ensure_ffmpeg", fake_ensure)

    ok, msg = check_ffmpeg_for_librosa()

    assert ensured["called"] is True
    assert ok is True


def test_soundfile_fallback(monkeypatch):
    def fake_load(path, sr):
        raise Exception("some unrelated librosa error")

    monkeypatch.setattr(phow.librosa, "load", fake_load)

    def fake_sf_read(path):
        # Return mono audio and 16kHz sample rate
        return np.zeros(16000, dtype=np.float32), 16000

    monkeypatch.setattr(phow.sf, "read", fake_sf_read)

    ok, msg = check_ffmpeg_for_librosa()

    assert ok is True
    assert "fallback" in msg.lower() or "soundfile" in msg.lower()
