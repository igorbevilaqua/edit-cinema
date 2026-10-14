import json, sys, mlx_whisper, soundfile as sf
segs = json.load(open("transcript.json"))["segments"]
W = [w for s in segs for w in s.get("words", [])]
# extra pass for the final CTA take missed by the first transcription
a, sr = sf.read("audio16k.wav")
r = mlx_whisper.transcribe(a[994*sr:1002*sr].astype("float32"), path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="pt", word_timestamps=True)
W += [dict(word=w["word"], start=w["start"]+994, end=w["end"]+994) for s in r["segments"] for w in s["words"]]
json.dump(W, open("words.json","w"), ensure_ascii=False)
