---
name: yt-ingest
description: Ingest a YouTube video — transcribe, AI-summarize, save clean note to vault
version: 2.0.0
tags: [youtube, transcription, summarize, ingest]
---

# YouTube Ingest

## What it does
One command: download audio → transcribe with Whisper → AI extracts key points → saves only the cleaned summary to vault → deletes everything else.

## Pipeline
```
/yt url:... 
  → yt-dlp (audio to /tmp)
  → faster-whisper (transcript)
  → DeepSeek (key points + summary)
  → vault/input/yt/*-cleaned.md
  → temp files deleted
```

## Usage
**Discord:** `/yt url:https://youtube.com/watch?v=xxx model:base`

The model parameter controls Whisper size. `base` is good for most videos. Use `tiny` for long videos or slow CPUs.

## What gets saved
A clean markdown note with:
- Frontmatter: source URL, title, date, duration
- TL;DR
- Key points
- Notable quotes (with timestamps)
- Action items (if any)

No raw transcript, no audio, no video — just the important information.

## Model sizes (faster-whisper)
| Size | RAM | Speed | Quality |
|------|-----|-------|---------|
| tiny | ~1GB | fastest | baseline |
| base | ~1.5GB | fast | decent |
| small | ~2.5GB | moderate | good |
| medium | ~5GB | slow | better |

## Script
`discord-control-plane/scripts/yt-ingest.sh` handles download + transcription.
The AI summarization runs inside the Discord bot via the OpenCode API.
