# StartOne competition video

This folder contains the English narration, timed scene plan, screenshots, subtitle file and reproducible rendering tools for the StartOne Devpost submission.

- Final duration: under 3 minutes
- Audio: natural English narration generated with `gpt-4o-mini-tts` and the `marin` voice; no music
- Captions: burned into the MP4 and provided as `StartOne_demo_en.srt`
- Privacy: no API key, account details or private learner material
- Product scenes: captured from the running StartOne web app

With `OPENAI_API_KEY` configured in the ignored root `.env`, run `python generate_natural_narration.py` and then `./build_video.sh`. The generated audio, build products and final MP4 stay local and are ignored by Git.
