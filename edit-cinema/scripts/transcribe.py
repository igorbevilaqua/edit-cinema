import json, mlx_whisper
r = mlx_whisper.transcribe("work/audio16k.wav", path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
                           language="pt", word_timestamps=True, condition_on_previous_text=False)
json.dump(r, open("work/transcript.json", "w"), ensure_ascii=False)
for s in r["segments"]:
    print(f'{s["start"]:7.2f}-{s["end"]:7.2f} {s["text"].strip()}')
