import ollama
import json
import re
from typing import List, Dict


def format_transcript(segments: List[Dict], max_segments: int = 100) -> str:
    total = len(segments)
    
    if total > max_segments:
        indices = []
        for i in range(max_segments):
            idx = int(i * total / max_segments)
            indices.append(idx)
        
        selected = [segments[i] for i in indices]
        print(f"Transcrição reduzida: {total} → {len(selected)} segmentos (distribuídos)")
    else:
        selected = segments
    
    lines = []
    for s in selected:
        lines.append(f"{s['start']:.0f}-{s['end']:.0f}s: {s['text']}")
    
    return "\n".join(lines)


def find_highlights(segments: List[Dict], num_clips: int = 5, model: str = "llama3") -> List[Dict]:
    total_duration = segments[-1]['end'] if segments else 0
    transcript = format_transcript(segments, max_segments=100)
    
    prompt = f"""Video duration: {total_duration:.0f} seconds

Find {num_clips} best moments for viral clips.

IMPORTANT RULES:
1. Spread clips across the ENTIRE video (beginning, middle, and end)
2. Clips should be 20-60 seconds each
3. Return ONLY JSON array, no other text

Format: [{{"start":100,"end":130,"title":"title here"}}]

Transcript:
{transcript}

JSON:"""

    print(f"Analisando com {model}...")
    print(f"Duração do vídeo: {total_duration:.0f}s ({total_duration/60:.1f} min)")
    
    for attempt in range(3):
        try:
            response = ollama.chat(
                model=model, 
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.1, 'num_predict': 1000}
            )
            
            content = response['message']['content'].strip()
            highlights = try_parse_json(content, total_duration)
            
            if highlights and len(highlights) >= num_clips // 2:
                if len(highlights) < num_clips:
                    highlights = fill_gaps(highlights, total_duration, num_clips)
                print(f"Encontrados {len(highlights)} highlights")
                return highlights
            
            print(f"Tentativa {attempt + 1}/3 falhou...")
            
        except Exception as e:
            print(f"Erro na tentativa {attempt + 1}: {e}")
    
    print("Usando fallback: clips distribuídos automaticamente")
    return create_distributed_clips(total_duration, num_clips)


def try_parse_json(content: str, max_duration: float) -> List[Dict] | None:
    content = re.sub(r'^```json?\s*', '', content.strip())
    content = re.sub(r'\s*```$', '', content)
    
    match = re.search(r'\[[\s\S]*?\]', content)
    if match:
        try:
            data = json.loads(match.group())
            return validate_highlights(data, max_duration)
        except:
            pass
    return None


def validate_highlights(data: List, max_duration: float) -> List[Dict] | None:
    valid = []
    for item in data:
        if isinstance(item, dict) and 'start' in item and 'end' in item:
            start = float(item['start'])
            end = float(item['end'])
            if 0 <= start < end <= max_duration + 10:
                valid.append({
                    'start': start,
                    'end': min(end, max_duration),
                    'title': str(item.get('title', f'Clip {len(valid)+1}')),
                })
    valid.sort(key=lambda x: x['start'])
    return valid if valid else None


def fill_gaps(highlights: List[Dict], duration: float, target: int) -> List[Dict]:
    if len(highlights) >= target:
        return highlights
    
    covered = [(h['start'], h['end']) for h in highlights]
    covered.sort()
    
    gaps = []
    prev_end = 0
    for start, end in covered:
        if start - prev_end > 60:
            gaps.append((prev_end + 10, start - 10))
        prev_end = end
    
    if duration - prev_end > 60:
        gaps.append((prev_end + 10, duration - 10))
    
    needed = target - len(highlights)
    for i, (gap_start, gap_end) in enumerate(gaps[:needed]):
        mid = (gap_start + gap_end) / 2
        highlights.append({
            'start': mid - 15,
            'end': mid + 15,
            'title': f'Momento {len(highlights) + 1}'
        })
    
    highlights.sort(key=lambda x: x['start'])
    return highlights


def create_distributed_clips(duration: float, num_clips: int) -> List[Dict]:
    clips = []
    clip_duration = 30
    section_size = duration / num_clips
    
    for i in range(num_clips):
        section_start = section_size * i
        center = section_start + section_size / 2
        
        start = max(0, center - clip_duration / 2)
        end = min(start + clip_duration, duration)
        
        clips.append({
            'start': start,
            'end': end,
            'title': f'Clip {i + 1}'
        })
    
    return clips
