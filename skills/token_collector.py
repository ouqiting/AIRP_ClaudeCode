"""Read real DeepSeek token usage from Claude Code session transcript, append to response.txt."""
import json, os, sys, glob as globmod
from pathlib import Path

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.abspath(ROOT)

def slugify(path):
    """Turn a filesystem path into the slug Claude uses for project dirs."""
    return "".join(c if c.isalnum() else "-" for c in path.replace("\\", "/"))

def find_transcript(projects_dir, slug):
    """Find the most recent .jsonl transcript for the given project slug.
    Claude appends variable numbers of dashes to the slug, so we glob-match."""
    pattern = os.path.join(projects_dir, slug + "*.jsonl") if os.path.isdir(os.path.join(projects_dir, slug)) else None
    # First try: exact slug dir
    slug_dir = os.path.join(projects_dir, slug)
    if os.path.isdir(slug_dir):
        files = globmod.glob(os.path.join(slug_dir, "*.jsonl"))
        if files:
            return max(files, key=os.path.getmtime)
    # Second try: glob for slug* dirs (Claude sometimes adds trailing dashes)
    for cand in sorted(globmod.glob(os.path.join(projects_dir, slug + "*")), reverse=True):
        if os.path.isdir(cand):
            files = globmod.glob(os.path.join(cand, "*.jsonl"))
            if files:
                return max(files, key=os.path.getmtime)
    return None

projects_dir = os.path.join(os.environ["USERPROFILE"], ".claude", "projects")
slug = slugify(ROOT)

# Try lock file first (cron mode), then fall back to glob (direct mode)
lock_path = os.path.join(ROOT, ".claude", "scheduled_tasks.lock")
transcript = None
if os.path.exists(lock_path):
    with open(lock_path, "r") as f:
        sid = json.load(f)["sessionId"]
    candidate = os.path.join(projects_dir, slug, f"{sid}.jsonl")
    if os.path.exists(candidate):
        transcript = candidate

if not transcript:
    transcript = find_transcript(projects_dir, slug)

if not transcript:
    print("WARNING: no transcript found")
    sys.exit(0)

# Scan backwards for last assistant message with usage data
with open(transcript, "r", encoding="utf-8") as f:
    lines = f.readlines()

usage = None
for line in reversed(lines):
    entry = json.loads(line.strip() or "{}")
    if entry.get("type") == "assistant":
        u = entry.get("message", {}).get("usage", {})
        if u.get("input_tokens") or u.get("output_tokens"):
            usage = u
            break

if usage:
    intok = usage.get("input_tokens", 0) + usage.get("cache_read_input_tokens", 0) + usage.get("cache_creation_input_tokens", 0)
    outtok = usage.get("output_tokens", 0)
    total = intok + outtok
    tokens_block = f"\n<tokens>\nin: {intok}\nout: {outtok}\ntotal: {total}\n</tokens>\n"

    resp = os.path.join(ROOT, "skills", "styles", "response.txt")
    with open(resp, "a", encoding="utf-8") as wf:
        wf.write(tokens_block)

    print(f"Token: in={intok} out={outtok} total={total}")
else:
    print("WARNING: no usage data in transcript")
