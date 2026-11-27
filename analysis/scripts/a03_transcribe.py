"""Whisper (medium.en) transcription of the Demucs vocal stem with word timestamps -> frames (N = round(t*30))."""
import sys, json, torch, whisper
torch.set_num_threads(int(sys.argv[2]) if len(sys.argv) > 2 else 2)
model = whisper.load_model(sys.argv[1] if len(sys.argv) > 1 else 'medium.en')
prompt = ("Arthur Morgan, Dutch van der Linde, Hosea Matthews, John Marston, Micah Bell, Sadie Adler, Charles, Lenny, "
          "Abigail, Sister Calderón, Agent Milton, Pinkertons, Blackwater, Saint Denis, Guarma, Valentine, Mary Linton, "
          "Eliza, Isaac, Strauss, Thomas Downes, Edith, Rains Fall, Pearson, Uncle, Tahiti, tuberculosis, Lyle.")
res = model.transcribe('work/stems/vocals_16k.wav', language='en', word_timestamps=True, initial_prompt=prompt,
                       condition_on_previous_text=True, temperature=0.0, verbose=False)
json.dump(res, open('analysis/data/whisper_raw.json', 'w'), indent=1)
words = []
for s in res['segments']:
    for w in s.get('words', []):
        words.append(dict(word=w['word'].strip(), start_s=round(w['start'], 3), end_s=round(w['end'], 3),
                          start_f=int(round(w['start']*30)), end_f=int(round(w['end']*30)), prob=round(w.get('probability', 0), 3), seg=s['id']))
json.dump(words, open('analysis/data/words_whisper.json', 'w'), indent=1)
print('DONE', len(words), 'words')
