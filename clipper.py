import subprocess
import os
from typing import List, Dict


def extract_clip(input_path: str, start: float, end: float, output_path: str) -> bool:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    duration = end - start
    
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-i", input_path,
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def extract_all_clips(video_path: str, highlights: List[Dict], output_dir: str = "clips") -> List[str]:
    created = []
    
    for i, clip in enumerate(highlights, 1):
        title = clip.get('title', f'clip_{i}')
        safe_title = "".join(c if c.isalnum() or c in ' -_' else '' for c in title)
        safe_title = safe_title.strip()[:50] or f"clip_{i}"
        
        output_path = os.path.join(output_dir, f"{i:02d}_{safe_title}.mp4")
        
        duration = clip['end'] - clip['start']
        print(f"Cortando clip {i}: {clip['start']:.1f}s → {clip['end']:.1f}s ({duration:.1f}s)")
        print(f"  Título: {title}")
        print(f"  Motivo: {clip.get('reason', 'N/A')}")
        
        if extract_clip(video_path, clip['start'], clip['end'], output_path):
            created.append(output_path)
            print(f"  ✓ Salvo: {output_path}")
        else:
            print(f"  ✗ Erro ao criar clip")
    
    return created
