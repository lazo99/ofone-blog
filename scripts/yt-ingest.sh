#!/usr/bin/env bash
# yt-ingest — Download + transcribe a YouTube video into the vault
set -euo pipefail

URL="${1:-}"
VAULT_DIR="${2:-$HOME/obsidian-vault}"
MODEL="${3:-base}"

if [ -z "$URL" ]; then
  echo "Usage: $0 <youtube-url> [vault-dir] [whisper-model]"
  exit 1
fi

# Sanitize title for filename
RAW_TITLE=$(yt-dlp --print title "$URL" 2>/dev/null)
TITLE=$(echo "$RAW_TITLE" | sed 's/[^a-zA-Z0-9 ]//g' | cut -c1-60)
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
DATE=$(date +%Y-%m-%d)
OUT_DIR="$VAULT_DIR/input/yt"
mkdir -p "$OUT_DIR"

echo "📥 Downloading audio: $TITLE"
yt-dlp -x --audio-format wav -o "/tmp/yt-${SLUG}.%(ext)s" "$URL" 2>&1

echo "🔊 Converting to 16kHz mono"
ffmpeg -y -i "/tmp/yt-${SLUG}.wav" -ar 16000 -ac 1 "/tmp/yt-${SLUG}-16k.wav" 2>/dev/null

DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "/tmp/yt-${SLUG}-16k.wav" 2>/dev/null)
DURATION_INT=$(printf "%.0f" "$DURATION" 2>/dev/null || echo "0")
MIN=$((DURATION_INT / 60))
SEC=$((DURATION_INT % 60))

echo "🎤 Transcribing (model: $MODEL, duration: ${MIN}m${SEC}s)..."
TRANSCRIPT=$(python3 << EOF
from faster_whisper import WhisperModel
import sys

model = WhisperModel("$MODEL", device="cpu", compute_type="int8")
segments, info = model.transcribe("/tmp/yt-${SLUG}-16k.wav")

print(f"Detected language: {info.language} (p={info.language_probability:.2f})", file=sys.stderr)
for seg in segments:
    print(f"[{seg.start:.1f}s -> {seg.end:.1f}s] {seg.text}")
EOF
)

# Save to vault
NOTE_FILE="$OUT_DIR/${DATE}-${SLUG}.md"
{
  echo "---"
  echo "source: $URL"
  echo "title: \"$TITLE\""
  echo "date: $DATE"
  echo "duration: ${MIN}m${SEC}s"
  echo "model: $MODEL"
  echo "tags: [youtube, transcript]"
  echo "---"
  echo ""
  echo "# $TITLE"
  echo ""
  echo "$TRANSCRIPT"
} > "$NOTE_FILE"

# Cleanup
rm -f "/tmp/yt-${SLUG}.wav" "/tmp/yt-${SLUG}-16k.wav"

echo ""
echo "✅ Saved to: $NOTE_FILE"
echo "📝 $(echo "$TRANSCRIPT" | wc -l) lines, $(echo "$TRANSCRIPT" | wc -c) chars"
