"""Ban word checker — scan response.txt against rules in ban_word.md, report matches to stdout."""
import re, sys, os

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.abspath(ROOT)

BAN_WORD_PATH = os.path.join(ROOT, "skills", "ban_word.md")
RESPONSE_PATH = os.path.join(ROOT, "skills", "styles", "response.txt")

# ── Parse ban_word.md ──
plain_rules = []   # list of str
regex_rules = []   # list of (pattern_str, compiled_regex)

with open(BAN_WORD_PATH, "r", encoding="utf-8") as f:
    for raw in f:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("`") and line.endswith("`"):
            pattern = line[1:-1]
            try:
                rx = re.compile(pattern)
                regex_rules.append((pattern, rx))
            except re.error as e:
                print(f"WARNING: invalid regex skipped: {pattern} ({e})")
        else:
            plain_rules.append(line)

# ── Read response.txt ──
with open(RESPONSE_PATH, "r", encoding="utf-8") as f:
    text = f.read()

# ── Sentence splitter (Chinese + English punctuation boundaries) ──
SENT_SPLIT = re.compile(r'(?<=[。！？.!?\n])(?=[^。！？.!?\n])')

def extract_sentence(text, pos, match_text):
    """Extract the full sentence containing the match, trimming to reasonable length."""
    # Find sentence boundaries around the match
    start = pos
    end = pos + len(match_text)
    # Expand start backwards to last sentence boundary
    for i in range(pos - 1, -1, -1):
        if text[i] in '。！？.!?\n':
            start = i + 1
            break
    else:
        start = 0
    # Expand end forwards to next sentence boundary
    for i in range(end, len(text)):
        if text[i] in '。！？.!?\n':
            end = i + 1
            break
    else:
        end = len(text)
    # Also include the surrounding sentence if we have only the match itself
    sentence = text[start:end].strip()
    if len(sentence) > 120:
        sentence = sentence[:117] + "..."
    return sentence

# ── Search ──
hits = []  # list of (rule, sentence)

# Plain text matching
for rule in plain_rules:
    idx = text.find(rule)
    while idx != -1:
        sent = extract_sentence(text, idx, rule)
        hits.append((rule, sent))
        idx = text.find(rule, idx + 1)

# Regex matching
for pattern_str, rx in regex_rules:
    for m in rx.finditer(text):
        match_text = m.group(0)
        sent = extract_sentence(text, m.start(), match_text)
        hits.append((pattern_str, sent))

# ── Output ──
if hits:
    print(f"检测到 {len(hits)} 个可能的禁词，分别是：")
    for rule, sent in hits:
        print(f"  • 规则「{rule}」→ 匹配句子：「{sent}」")
    print()
    print("请判断是否需要修改，直接在 response.txt 中改掉对应的句子。")
    sys.exit(1)  # non-zero signals AI needs to review
else:
    print("未检测到违禁词。")
    sys.exit(0)
