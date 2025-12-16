"""Integration test for the user's MP3 file to diagnose Librosa/FFmpeg issues.

This test attempts to:
- Verify the file exists at the expected path (skips if not present).
- Ensure FFmpeg is configured and log `get_ffmpeg_info()`.
- Run the project's Librosa FFmpeg check (`check_ffmpeg_for_librosa()`) and log the message.
- Try to normalize the MP3 to WAV using `normalize_audio_to_wav()` (file-path based load).
- Try to load the MP3 by content (bytes) via `load_audio()`.

The test prints detailed diagnostic logs to stdout so you can paste them here if there are failures.

Run with: pytest -q tests/test_popcast_mp3.py
"""
import sys
import os
# Allow running this test file directly (python tests/test_popcast_mp3.py) by adding project root to sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import logging
import numpy as np
import pytest

from core.audio.ffmpeg_setup import ensure_ffmpeg, get_ffmpeg_info
from core.asr.phowhisper_service import check_ffmpeg_for_librosa
from core.audio.audio_processor import normalize_audio_to_wav, load_audio

# Path provided by user (note: includes a space before extension as provided)
# Use environment variable or default to None (test will skip if not found)
MP3_PATH = os.environ.get("TEST_MP3_PATH", None)

logger = logging.getLogger(__name__)


def _log_ffmpeg_state():
    ok, info = ensure_ffmpeg(silent=True, verbose=True)
    logger.info("ensure_ffmpeg returned: %s", ok)
    logger.info("get_ffmpeg_info: %s", get_ffmpeg_info())


def test_popcast_mp3_loads_and_normalizes(caplog):
    caplog.set_level(logging.INFO)

    if MP3_PATH is None or not os.path.exists(MP3_PATH):
        pytest.skip(f"Test file not found. Set TEST_MP3_PATH environment variable to run this test.")

    logger.info("Starting diagnostics for: %s", MP3_PATH)

    # 1) FFmpeg basics
    _log_ffmpeg_state()

    # 2) Run project-level librosa ffmpeg check
    librosa_ok, librosa_msg = check_ffmpeg_for_librosa()
    logger.info("check_ffmpeg_for_librosa -> ok=%s, msg=%s", librosa_ok, librosa_msg)

    # 3) Try normalize_audio_to_wav (path-based). This function uses librosa.load internally.
    norm_path = None
    try:
        norm_path, sr, y = normalize_audio_to_wav(MP3_PATH)
        logger.info("normalize_audio_to_wav succeeded: out=%s sr=%s samples=%s", norm_path, sr, y.shape if y is not None else None)
        assert os.path.exists(norm_path), "Normalized WAV not created"
        # Clean up
        try:
            os.unlink(norm_path)
        except Exception as e:
            logger.warning("Failed to remove normalized file: %s", e)
    except Exception as e:
        logger.exception("normalize_audio_to_wav failed: %s", e)
        norm_path = None

    # 4) Try load_audio with bytes (this uses a temp file in the project code)
    try:
        with open(MP3_PATH, "rb") as f:
            data = f.read()
        y2, sr2 = load_audio(data, sr=16000)
        logger.info("load_audio(bytes) -> ok, sr=%s, shape=%s", sr2, y2.shape if y2 is not None else None)
    except Exception as e:
        logger.exception("load_audio(bytes) failed: %s", e)
        y2 = None

    # 5) Final assertions: at least one method should have produced audio
    if (norm_path is None) and (y2 is None):
        # Print helpful logs for debugging
        logger.error("Both normalize_audio_to_wav and load_audio(bytes) failed. Check ffmpeg and file validity.")
        # Re-log ffmpeg info for easy copy-paste
        logger.error("FFmpeg info: %s", get_ffmpeg_info())
        pytest.fail("Failed to load/normalize the MP3 file. See logs for details.")

    logger.info("MP3 diagnostic test completed successfully.")


def test_transcribe_with_whisper_and_phowhisper(caplog):
    """Run both Whisper and PhoWhisper on the normalized WAV produced from the MP3 and save transcripts.

    This helps reproduce runtime errors seen in Streamlit (WinError 2, FFmpeg errors, missing files).
    The test writes transcript artifacts to `tests/artifacts/` for easy inspection.
    """
    caplog.set_level(logging.INFO)

    if MP3_PATH is None or not os.path.exists(MP3_PATH):
        pytest.skip(f"Test file not found. Set TEST_MP3_PATH environment variable to run this test.")

    logger.info("Starting transcription diagnostics for: %s", MP3_PATH)

    # Ensure FFmpeg state is logged
    _log_ffmpeg_state()

    # Normalize source to WAV (creates a temp WAV file)
    wav_path = None
    try:
        wav_path, sr, y = normalize_audio_to_wav(MP3_PATH)
        logger.info("Normalized MP3 to WAV: %s (sr=%s, samples=%s)", wav_path, sr, y.shape if y is not None else None)
    except Exception as e:
        logger.exception("Failed to normalize MP3 to WAV: %s", e)
        pytest.fail(f"normalize_audio_to_wav failed: {e}")

    # Prepare artifact folder
    artifacts_dir = os.path.join(ROOT, "tests", "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)

    # Try Whisper
    whisper_text = None
    try:
        # Import here to avoid heavy imports if test gets skipped earlier
        from core.asr.evaluate_models import evaluate_model_whisper
        whisper_model = os.environ.get("TEST_WHISPER_MODEL", "base")
        logger.info("Running Whisper model: %s", whisper_model)
        whisper_text = evaluate_model_whisper(wav_path, model_size=whisper_model)
        logger.info("Whisper output (first 200 chars): %s", (whisper_text or "").strip()[:200])
        with open(os.path.join(artifacts_dir, f"whisper_{whisper_model}_transcript.txt"), "w", encoding="utf-8") as f:
            f.write(whisper_text or "")
    except Exception as e:
        logger.exception("Whisper transcription failed: %s", e)

    # Try PhoWhisper
    phow_text = None
    try:
        from core.asr.evaluate_models import evaluate_model_phowhisper
        phow_model = os.environ.get("TEST_PHOWHISPER_MODEL", "small")
        logger.info("Running PhoWhisper model: %s", phow_model)
        phow_text = evaluate_model_phowhisper(wav_path, model_size=phow_model)
        logger.info("PhoWhisper output (first 200 chars): %s", (phow_text or "").strip()[:200])
        with open(os.path.join(artifacts_dir, f"phowhisper_{phow_model}_transcript.txt"), "w", encoding="utf-8") as f:
            f.write(phow_text or "")
    except Exception as e:
        logger.exception("PhoWhisper transcription failed: %s", e)

    # Clean up normalized WAV
    try:
        if wav_path and os.path.exists(wav_path):
            os.unlink(wav_path)
    except Exception as e:
        logger.warning("Failed to remove temporary WAV: %s", e)

    # Final assertion: at least one model should produce non-empty text
    if not (whisper_text or phow_text):
        logger.error("Both models failed to produce transcripts. See logs and artifacts folder: %s", artifacts_dir)
        logger.error("FFmpeg info: %s", get_ffmpeg_info())
        pytest.fail("Whisper and PhoWhisper both failed to transcribe the MP3. Check logs/artifacts for details.")

    logger.info("Transcription diagnostics completed. Artifacts: %s", artifacts_dir)
