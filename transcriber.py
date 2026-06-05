import whisper
from typing import List, Dict


def transcribe_video(video_path: str, model_size: str = "base", language: str = "pt") -> List[Dict]:
    print(f"Carregando modelo Whisper ({model_size})...")
    model = whisper.load_model(model_size)
    
    print(f"Transcrevendo: {video_path}")
    print(f"Idioma: {language}")
    result = model.transcribe(video_path, language=language)
    
    segments = []
    for seg in result['segments']:
        segments.append({
            'start': seg['start'],
            'end': seg['end'],
            'text': seg['text'].strip()
        })
    
    print(f"Transcrição completa: {len(segments)} segmentos")
    return segments
