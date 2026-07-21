from pathlib import Path
import sys

from dotenv import load_dotenv
from openai import OpenAI


ROOT = Path(__file__).resolve().parents[2]
VIDEO_DIR = ROOT / "submission" / "video"
SEGMENTS_DIR = VIDEO_DIR / "segments"
OUTPUT_DIR = VIDEO_DIR / "audio_natural"

VOICE_DIRECTION = """
Speak in natural, warm, confident conversational English, like a thoughtful
product founder giving a live demo to judges. Keep the energy attentive and
human, with varied rhythm, light emphasis on the learning benefit, and brief
pauses between ideas. Sound clear and engaged, not salesy. Avoid an announcer
cadence, a synthetic monotone, exaggerated emotion, or rushed delivery.
Pronounce GPT-5.6 as "G P T five point six" and Codex as "code-ex".
""".strip()


def main() -> None:
    load_dotenv(ROOT / ".env")
    client = OpenAI()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timeline_ids = {
        line.split("\t", 1)[0]
        for line in (VIDEO_DIR / "timeline.tsv").read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    }
    requested_ids = set(sys.argv[1:]) or timeline_ids

    for source in sorted(SEGMENTS_DIR.glob("*.txt")):
        if source.stem not in requested_ids:
            continue
        target = OUTPUT_DIR / f"{source.stem}.wav"
        text = source.read_text(encoding="utf-8").strip()
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="marin",
            input=text,
            instructions=VOICE_DIRECTION,
            response_format="wav",
            speed=1.03,
        ) as response:
            response.stream_to_file(target)
        print(f"Generated {target.name}")


if __name__ == "__main__":
    main()
