# MomentoAI

Pipeline para criar cortes automáticos de vídeos usando inteligência artificial. O sistema transcreve o áudio, identifica os melhores momentos e gera clips prontos para redes sociais.

## Como Funciona

1. **Transcrição** - Usa Whisper (OpenAI) para converter áudio em texto com timestamps
2. **Análise** - Usa Ollama (LLM local) para identificar os momentos mais interessantes
3. **Corte** - Usa FFmpeg para extrair os clips do vídeo original

## Requisitos

- Python 3.10+
- FFmpeg instalado no sistema
- Ollama instalado e rodando

## Instalação

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Baixar modelo de IA
ollama pull llama3
```

## Uso

### Vídeo local

```bash
python main.py video.mp4
```

### Vídeo do YouTube

```bash
python main.py "https://www.youtube.com/watch?v=XXXXX"
```

### Opções

| Opção | Descrição | Padrão |
|-------|-----------|--------|
| `-n` | Número de clips a extrair | 5 |
| `-o` | Pasta de saída | clips |
| `--whisper-model` | Modelo de transcrição (tiny, base, small, medium, large) | base |
| `--llm-model` | Modelo Ollama para análise | llama3 |
| `--language` | Idioma do vídeo (pt, en, es, etc.) | pt |
| `--save-transcript` | Salvar transcrição em JSON | false |

### Exemplos

```bash
# Vídeo em inglês, 10 clips
python main.py video.mp4 --language en -n 10

# Usar modelo mais preciso
python main.py video.mp4 --whisper-model small --llm-model phi3

# Salvar transcrição
python main.py video.mp4 --save-transcript
```

## Estrutura do Projeto

```
editordevideo/
├── main.py          # Script principal
├── transcriber.py   # Transcrição com Whisper
├── analyzer.py      # Análise com Ollama
├── clipper.py       # Corte com FFmpeg
├── downloader.py    # Download do YouTube
├── requirements.txt # Dependências
└── clips/           # Pasta de saída
```

## Modelos Recomendados

### Whisper (transcrição)

| Modelo | RAM | Velocidade | Precisão |
|--------|-----|------------|----------|
| tiny | 1GB | Muito rápido | Básica |
| base | 1GB | Rápido | Boa |
| small | 2GB | Médio | Muito boa |
| medium | 5GB | Lento | Excelente |
| large | 10GB | Muito lento | Máxima |

### Ollama (análise)

| Modelo | RAM | Qualidade |
|--------|-----|-----------|
| phi3 | 2GB | Boa |
| llama3 | 4GB | Muito boa |
| mistral | 4GB | Muito boa |

## Tecnologias

- **Whisper** - Transcrição de áudio (OpenAI, open source)
- **Ollama** - Execução de LLMs localmente
- **FFmpeg** - Processamento de vídeo
- **yt-dlp** - Download de vídeos do YouTube
