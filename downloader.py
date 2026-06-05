import yt_dlp
import os
import re


def sanitize_filename(title: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '', title)[:100]


def download_from_youtube(url: str, output_dir: str = "downloads") -> str:
    os.makedirs(output_dir, exist_ok=True)
    
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        title = sanitize_filename(info['title'])
    
    output_path = os.path.join(output_dir, f"{title}.mp4")
    
    ydl_opts = {
        'format': 'best[ext=mp4][height<=1080]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'quiet': False,
        'no_warnings': True,
    }
    
    print(f"Baixando: {info['title']}")
    print(f"Duração: {info.get('duration', 0) // 60}min {info.get('duration', 0) % 60}s")
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    print(f"Salvo em: {output_path}")
    return output_path
