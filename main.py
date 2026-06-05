#!/usr/bin/env python3

import argparse
import os
import json

from transcriber import transcribe_video
from analyzer import find_highlights
from clipper import extract_all_clips


def is_youtube_url(text: str) -> bool:
    youtube_patterns = ['youtube.com', 'youtu.be', 'youtube.com/shorts']
    return any(pattern in text.lower() for pattern in youtube_patterns)


def get_video_path(video_input: str, output_dir: str) -> str:
    if is_youtube_url(video_input):
        from downloader import download_from_youtube
        print("\n[0/4] DOWNLOAD DO YOUTUBE")
        print("-" * 40)
        return download_from_youtube(video_input, os.path.join(output_dir, "downloads"))
    else:
        if not os.path.exists(video_input):
            raise FileNotFoundError(f"Vídeo não encontrado: {video_input}")
        return video_input


def main():
    parser = argparse.ArgumentParser(
        description="Cortes automáticos de vídeo com IA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python main.py video.mp4
  python main.py video.mp4 -n 3 --whisper-model small
  python main.py "https://www.youtube.com/watch?v=XXXXX"
  python main.py "https://youtu.be/XXXXX" --llm-model phi3
        """
    )
    parser.add_argument("video", help="Caminho do vídeo ou URL do YouTube")
    parser.add_argument("-n", "--num-clips", type=int, default=5, 
                        help="Número de clips a extrair (padrão: 5)")
    parser.add_argument("-o", "--output-dir", default="clips",
                        help="Pasta de saída (padrão: clips)")
    parser.add_argument("--whisper-model", default="base",
                        choices=["tiny", "base", "small", "medium", "large"],
                        help="Modelo Whisper (padrão: base)")
    parser.add_argument("--llm-model", default="llama3",
                        help="Modelo Ollama (padrão: llama3)")
    parser.add_argument("--save-transcript", action="store_true",
                        help="Salvar transcrição em arquivo JSON")
    parser.add_argument("--language", default="pt",
                        help="Idioma do vídeo para transcrição (padrão: pt)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("PIPELINE DE CORTES AUTOMÁTICOS")
    print("=" * 60)
    print(f"Entrada: {args.video}")
    print(f"Clips a extrair: {args.num_clips}")
    print(f"Modelo Whisper: {args.whisper_model}")
    print(f"Modelo LLM: {args.llm_model}")
    print(f"Idioma: {args.language}")
    print("=" * 60)
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    try:
        video_path = get_video_path(args.video, args.output_dir)
    except FileNotFoundError as e:
        print(f"Erro: {e}")
        return 1
    except Exception as e:
        print(f"Erro ao baixar vídeo: {e}")
        return 1
    
    print(f"\nVídeo: {video_path}")
    
    print("\n[1/3] TRANSCRIÇÃO")
    print("-" * 40)
    segments = transcribe_video(video_path, args.whisper_model, args.language)
    
    if not segments:
        print("Erro: Nenhum segmento transcrito. Verifique se o vídeo tem áudio.")
        return 1
    
    if args.save_transcript:
        transcript_path = os.path.join(args.output_dir, "transcript.json")
        with open(transcript_path, 'w', encoding='utf-8') as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)
        print(f"Transcrição salva: {transcript_path}")
    
    print("\n[2/3] ANÁLISE COM IA")
    print("-" * 40)
    try:
        highlights = find_highlights(segments, args.num_clips, args.llm_model)
    except Exception as e:
        print(f"Erro na análise: {e}")
        print("Dica: Verifique se o Ollama está rodando (ollama serve)")
        return 1
    
    if not highlights:
        print("Nenhum highlight encontrado.")
        return 1
    
    highlights_path = os.path.join(args.output_dir, "highlights.json")
    with open(highlights_path, 'w', encoding='utf-8') as f:
        json.dump(highlights, f, ensure_ascii=False, indent=2)
    print(f"Highlights salvos: {highlights_path}")
    
    print("\n[3/3] CORTE DOS CLIPS")
    print("-" * 40)
    created_clips = extract_all_clips(video_path, highlights, args.output_dir)
    
    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    print(f"Total de clips criados: {len(created_clips)}")
    for clip in created_clips:
        print(f"  → {clip}")
    print("=" * 60)
    print("Concluído!")
    
    return 0


if __name__ == "__main__":
    exit(main())
