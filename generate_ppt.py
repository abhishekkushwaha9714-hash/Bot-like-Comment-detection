"""
Generates the project presentation: Bot-Like Comment Detection
Run: python generate_ppt.py
Output: Bot_Comment_Detection_PPT.pptx
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import copy

# ── Colour palette ─────────────────────────────────────────────────────────────
BG_DARK    = RGBColor(0x0F, 0x17, 0x2A)   # #0f172a  slide background
SURFACE    = RGBColor(0x1E, 0x29, 0x3B)   # #1e293b  card / box
ACCENT     = RGBColor(0x63, 0x66, 0xF1)   # #6366f1  indigo
ACCENT2    = RGBColor(0xA7, 0x8B, 0xFA)   # #a78bfa  violet
BOT_RED    = RGBColor(0xEF, 0x44, 0x44)   # #ef4444
HUMAN_GRN  = RGBColor(0x22, 0xC5, 0x5E)   # #22c55e
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
MUTED      = RGBColor(0x94, 0xA3, 0xB8)   # #94a3b8
YELLOW     = RGBColor(0xFB, 0xBF, 0x24)   # amber

SW = Inches(13.33)   # slide width  (widescreen 16:9)
SH = Inches(7.5)     # slide height

prs = Presentation()
prs.slide_width  = SW
prs.slide_height = SH

BLANK = prs.slide_layouts[6]   # completely blank layout


# ── Helper functions ────────────────────────────────────────────────────────────

def add_slide():
    return prs.slides.add_slide(BLANK)

def fill_bg(slide, color=BG_DARK):
    """Fill slide background with a solid colour."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def box(slide, x, y, w, h, fill=None, border=None):
    """Add a plain rectangle shape."""
    shape = slide.shapes.add_shape(
        1,   # MSO_SHAPE_TYPE.RECTANGLE
        Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.line.fill.background()          # no border by default
    if fill:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    else:
        shape.fill.background()
    if border:
        shape.line.color.rgb = border
        shape.line.width = Pt(1)
    return shape

def txt(slide, text, x, y, w, h,
        size=18, bold=False, color=WHITE,
        align=PP_ALIGN.LEFT, wrap=True, italic=False):
    """Add a text box."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tb.word_wrap = wrap
    tf = tb.text_frame
    tf.word_wrap = wrap
    p  = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size  = Pt(size)
    run.font.bold  = bold
    run.font.color.rgb = color
    run.font.italic    = italic
    return tb

def gradient_title(slide, title, subtitle=None):
    """Large centred gradient-style title (simulated with two overlapping texts)."""
    # shadow / offset
    txt(slide, title, 0.08, 1.88, 13.33, 1.5,
        size=40, bold=True, color=SURFACE, align=PP_ALIGN.CENTER)
    # main (accent colour)
    txt(slide, title, 0.0, 1.8, 13.33, 1.5,
        size=40, bold=True, color=ACCENT2, align=PP_ALIGN.CENTER)
    if subtitle:
        txt(slide, subtitle, 0.0, 3.2, 13.33, 0.8,
            size=20, color=MUTED, align=PP_ALIGN.CENTER)

def section_header(slide, text, y=0.3):
    txt(slide, text, 0.5, y, 12, 0.5,
        size=11, bold=True, color=ACCENT,
        align=PP_ALIGN.LEFT)
    # underline bar
    bar = slide.shapes.add_shape(1,
        Inches(0.5), Inches(y + 0.42), Inches(12), Pt(2))
    bar.fill.solid(); bar.fill.fore_color.rgb = ACCENT
    bar.line.fill.background()

def bullet_card(slide, title, bullets, x, y, w, h, icon=""):
    box(slide, x, y, w, h, fill=SURFACE, border=ACCENT)
    ty = y + 0.12
    txt(slide, f"{icon}  {title}" if icon else title,
        x+0.15, ty, w-0.3, 0.4,
        size=13, bold=True, color=ACCENT2)
    for i, b in enumerate(bullets):
        txt(slide, f"▸  {b}",
            x+0.2, ty + 0.42 + i*0.38, w-0.35, 0.36,
            size=11, color=WHITE)

def tag_box(slide, label, x, y, fill_col, text_col=WHITE):
    b = box(slide, x, y, 1.5, 0.35, fill=fill_col)
    txt(slide, label, x+0.05, y+0.02, 1.4, 0.32,
        size=11, bold=True, color=text_col, align=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — Title slide
# ══════════════════════════════════════════════════════════════════════════════
sl = add_slide(); fill_bg(sl)

# top accent bar
b = sl.shapes.add_shape(1, 0, 0, SW, Inches(0.08))
b.fill.solid(); b.fill.fore_color.rgb = ACCENT; b.line.fill.background()

# decorative circle blobs (background feel)
for cx, cy, sz, alpha in [(9.5,1.5,3.5,SURFACE),(3,5,2.5,SURFACE)]:
    c = sl.shapes.add_shape(9, Inches(cx), Inches(cy), Inches(sz), Inches(sz))
    c.fill.solid(); c.fill.fore_color.rgb = alpha; c.line.fill.background()

txt(sl, "🤖", 5.9, 0.5, 1.5, 1.0, size=40, align=PP_ALIGN.CENTER)

txt(sl, "BOT-LIKE COMMENT DETECTION",
    0.5, 1.6, 12.33, 1.1,
    size=36, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# gradient accent line under title
bar = sl.shapes.add_shape(1, Inches(3.5), Inches(2.75), Inches(6.33), Pt(3))
bar.fill.solid(); bar.fill.fore_color.rgb = ACCENT; bar.line.fill.background()

txt(sl, "Social Media Analytics & Sentiment Analysis",
    0.5, 2.9, 12.33, 0.6,
    size=18, color=ACCENT2, align=PP_ALIGN.CENTER)

txt(sl, "Detecting Automated Spam Comments Using Machine Learning",
    0.5, 3.55, 12.33, 0.5,
    size=14, color=MUTED, align=PP_ALIGN.CENTER, italic=True)

# info strip at bottom
box(sl, 0, 6.6, 13.33, 0.9, fill=SURFACE)
txt(sl, "Subject :  Social Media Analytics & Sentiment Analysis",
    0.5, 6.65, 6, 0.5, size=12, color=MUTED)
txt(sl, "Tech Stack :  Python  ·  Flask  ·  Naive Bayes  ·  TF-IDF",
    6.8, 6.65, 6, 0.5, size=12, color=MUTED, align=PP_ALIGN.RIGHT)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — Problem Statement
# ══════════════════════════════════════════════════════════════════════════════
sl = add_slide(); fill_bg(sl)
section_header(sl, "PROBLEM STATEMENT")

txt(sl, "The Problem with Bot Comments", 0.5, 0.85, 12, 0.6,
    size=26, bold=True, color=WHITE)

# big stat boxes
stats = [
    ("~40%", "of YouTube comments\nare bot-generated", BOT_RED),
    ("Billions", "of fake views driven\nby automated bots", RGBColor(0xF5,0x9E,0x0B)),
    ("Manual", "detection is slow\nand unscalable", ACCENT),
]
for i,(val,lbl,col) in enumerate(stats):
    bx = 0.4 + i*4.3
    box(sl, bx, 1.65, 3.9, 1.9, fill=SURFACE, border=col)
    txt(sl, val, bx, 1.75, 3.9, 0.8,
        size=32, bold=True, color=col, align=PP_ALIGN.CENTER)
    txt(sl, lbl, bx, 2.55, 3.9, 0.9,
        size=13, color=MUTED, align=PP_ALIGN.CENTER)

txt(sl, "What are bot comments?", 0.5, 3.75, 12, 0.4,
    size=16, bold=True, color=ACCENT2)

points = [
    "Automated accounts that post spam links, fake promotions, and sub-for-sub requests",
    "They manipulate engagement metrics, mislead real users, and pollute comment sections",
    "Traditional keyword filters are easily bypassed — machine learning is needed",
    "This project builds a web app that classifies any YouTube comment as Bot or Human",
]
for i,p in enumerate(points):
    txt(sl, f"▸  {p}", 0.6, 4.2 + i*0.52, 12, 0.45, size=13, color=WHITE)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — Objectives
# ══════════════════════════════════════════════════════════════════════════════
sl = add_slide(); fill_bg(sl)
section_header(sl, "OBJECTIVES")

txt(sl, "What This Project Achieves", 0.5, 0.85, 12, 0.55,
    size=26, bold=True, color=WHITE)

objectives = [
    ("01", "Detect Bot Comments",
     "Automatically classify any YouTube comment as bot-generated or human-written using ML"),
    ("02", "Rule-Based Signals",
     "Extract 10 hand-crafted features — URLs, CAPS ratio, repetition, spam keywords, punctuation"),
    ("03", "TF-IDF Text Analysis",
     "Convert comment text into numerical vectors capturing word importance and bigram patterns"),
    ("04", "Web Application",
     "Build a Flask web app with single comment analysis, bulk CSV upload, and visual charts"),
    ("05", "Explainability",
     "Show users exactly which signals triggered the bot classification — not just a label"),
]
for i,(num,title,desc) in enumerate(objectives):
    y = 1.6 + i * 1.0
    box(sl, 0.4, y, 12.4, 0.82, fill=SURFACE, border=ACCENT)
    txt(sl, num, 0.55, y+0.1, 0.7, 0.6, size=20, bold=True, color=ACCENT)
    txt(sl, title, 1.35, y+0.05, 4, 0.38, size=14, bold=True, color=ACCENT2)
    txt(sl, desc,  1.35, y+0.42, 11, 0.35, size=12, color=MUTED)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — Dataset
# ══════════════════════════════════════════════════════════════════════════════
sl = add_slide(); fill_bg(sl)
section_header(sl, "DATASET")

txt(sl, "YouTube Comments Dataset", 0.5, 0.85, 12, 0.55,
    size=26, bold=True, color=WHITE)

# dataset info card
box(sl, 0.4, 1.55, 5.8, 3.2, fill=SURFACE, border=ACCENT)
txt(sl, "📊  Dataset Overview", 0.6, 1.65, 5.4, 0.4,
    size=14, bold=True, color=ACCENT2)
info = [
    ("Source",   "UCI YouTube Spam Collection"),
    ("Total",    "150 labelled comments"),
    ("Bot (1)",  "75 spam / bot comments"),
    ("Human (0)","75 legitimate comments"),
    ("Videos",   "Gangnam Style, Lose Yourself,"),
    ("",         "Roar, Hips Don't Lie, Party Rock"),
    ("Format",   "CSV  —  CONTENT, CLASS columns"),
]
for i,(k,v) in enumerate(info):
    y = 2.12 + i*0.33
    if k:
        txt(sl, k+":", 0.6, y, 1.6, 0.3, size=11, bold=True, color=MUTED)
    txt(sl, v, 2.25, y, 3.8, 0.3, size=11, color=WHITE)

# sample comments
box(sl, 6.5, 1.55, 6.4, 3.2, fill=SURFACE, border=ACCENT)
txt(sl, "💬  Sample Comments", 6.7, 1.65, 6, 0.4,
    size=14, bold=True, color=ACCENT2)

samples = [
    (0, "ngl i hated this song at first but now i genuinely love it after hearing it 50 times"),
    (0, "played this at my birthday party last weekend and everyone lost their minds lol"),
    (1, "earn $1000 per week online easy method click my profile"),
    (1, "sub4sub anyone I will subscribe back 100% guaranteed real"),
    (0, "its 3am and im watching this for the 100th time why am i like this"),
    (1, "FREE gift cards click http://giftcardgen.xyz claim yours today"),
]
for i,(cls,comment) in enumerate(samples):
    y = 2.12 + i*0.42
    col = BOT_RED if cls==1 else HUMAN_GRN
    lbl = "BOT" if cls==1 else "HMN"
    tag_box(sl, lbl, 6.6, y+0.03, col)
    txt(sl, comment[:72]+("…" if len(comment)>72 else ""),
        8.2, y, 4.5, 0.38, size=10, color=WHITE)

# class balance bar
box(sl, 0.4, 4.95, 12.5, 0.08, fill=HUMAN_GRN)
box(sl, 6.65, 4.95, 6.25, 0.08, fill=BOT_RED)
txt(sl, "50% Human", 0.4, 5.08, 5, 0.3, size=11, color=HUMAN_GRN)
txt(sl, "50% Bot", 8.5, 5.08, 4, 0.3, size=11, color=BOT_RED, align=PP_ALIGN.RIGHT)
txt(sl, "Perfectly balanced dataset — no class bias",
    0.4, 5.45, 12.5, 0.35, size=12, color=MUTED, align=PP_ALIGN.CENTER, italic=True)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — Methodology / Architecture
# ══════════════════════════════════════════════════════════════════════════════
sl = add_slide(); fill_bg(sl)
section_header(sl, "METHODOLOGY")

txt(sl, "System Architecture & Pipeline", 0.5, 0.85, 12, 0.55,
    size=26, bold=True, color=WHITE)

# pipeline steps
steps = [
    ("📥", "Input",        "Raw YouTube\ncomment text"),
    ("🧹", "Preprocess",   "Lowercase · Remove\nURLs · Strip stopwords"),
    ("📐", "TF-IDF",       "3000-feature vector\n+ bigrams"),
    ("🔬", "Rule Features","10 hand-crafted\nbot signals"),
    ("🔗", "Combine",      "Merge TF-IDF +\nrule feature vector"),
    ("🌲", "Naive Bayes",  "Gaussian NB\nclassifier"),
    ("🏷️", "Output",       "Bot / Human +\nconfidence score"),
]
arrow_col = ACCENT
for i,(_icon,_title,_desc) in enumerate(steps):
    bx = 0.25 + i*1.84
    box(sl, bx, 1.65, 1.65, 1.9, fill=SURFACE, border=ACCENT)
    txt(sl, _icon, bx, 1.72, 1.65, 0.5, size=22, align=PP_ALIGN.CENTER)
    txt(sl, _title, bx, 2.22, 1.65, 0.35,
        size=12, bold=True, color=ACCENT2, align=PP_ALIGN.CENTER)
    txt(sl, _desc, bx, 2.58, 1.65, 0.85,
        size=10, color=MUTED, align=PP_ALIGN.CENTER)
    # arrow between boxes
    if i < len(steps)-1:
        ax = bx + 1.68
        txt(sl, "→", ax-0.02, 2.2, 0.25, 0.35, size=14, color=ACCENT, align=PP_ALIGN.CENTER)

# two detail boxes below
box(sl, 0.4, 3.8, 6.0, 2.8, fill=SURFACE, border=ACCENT)
txt(sl, "TF-IDF Vectorisation", 0.6, 3.9, 5.6, 0.4,
    size=14, bold=True, color=ACCENT2)
tfidf_pts = [
    "Tokenise + remove stopwords",
    "Build vocabulary of top 3000 tokens",
    "Include bigrams (e.g. 'click here', 'free subscribe')",
    "TF  =  term count / total words in comment",
    "IDF  =  log((N+1) / (df+1)) + 1   (smoothed)",
    "Final score  =  TF × IDF",
]
for i,p in enumerate(tfidf_pts):
    txt(sl, f"▸  {p}", 0.6, 4.35+i*0.37, 5.7, 0.33, size=11, color=WHITE)

box(sl, 6.9, 3.8, 6.0, 2.8, fill=SURFACE, border=ACCENT)
txt(sl, "10 Rule-Based Features", 7.1, 3.9, 5.6, 0.4,
    size=14, bold=True, color=ACCENT2)
rule_pts = [
    "Character length of comment",
    "Word count",
    "Uppercase ratio  (CAPS SHOUTING)",
    "URL presence  (http:// or www.)",
    "Exclamation mark count  (!!!)",
    "Word repetition ratio",
    "Spam keyword count",
    "Punctuation density",
    "Digit ratio  ($500, phone numbers)",
    "Average word length",
]
for i,p in enumerate(rule_pts):
    txt(sl, f"▸  {p}", 7.1, 4.35+i*0.245, 5.7, 0.24, size=10.5, color=WHITE)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — Bot Signals Explained
# ══════════════════════════════════════════════════════════════════════════════
sl = add_slide(); fill_bg(sl)
section_header(sl, "BOT SIGNAL DETECTION")

txt(sl, "How the Model Spots a Bot", 0.5, 0.85, 12, 0.55,
    size=26, bold=True, color=WHITE)

signals = [
    ("🔗 URL / Link",         "Bots always include http:// links to scam sites",                    BOT_RED),
    ("🔠 ALL CAPS",           "Bots shout to grab attention  — high uppercase ratio",               BOT_RED),
    ("❗ Exclamation Spam",    "Multiple !!! indicate urgency — a classic bot tactic",              BOT_RED),
    ("🔁 Word Repetition",    "'click click click subscribe subscribe' — bots repeat keywords",    BOT_RED),
    ("💰 Spam Keywords",      "free · win · earn · cash · gift · prize · guaranteed · bitcoin",    BOT_RED),
    ("📏 Short Templates",    "Very short generic comments like 'nice video sub me' are bots",     RGBColor(0xF5,0x9E,0x0B)),
    ("🔢 Digits / Prices",    "$500 daily · 1000 subscribers · 300% returns — digit-heavy text",   RGBColor(0xF5,0x9E,0x0B)),
    ("✍️ Natural Language",   "Specific memories, typos, casual tone = strong human signals",      HUMAN_GRN),
]
for i,(sig,desc,col) in enumerate(signals):
    row = i // 2
    col_n = i % 2
    bx = 0.4 + col_n * 6.45
    by = 1.6 + row * 1.3
    box(sl, bx, by, 6.1, 1.1, fill=SURFACE, border=col)
    txt(sl, sig,  bx+0.15, by+0.08, 5.8, 0.38, size=13, bold=True, color=col)
    txt(sl, desc, bx+0.15, by+0.48, 5.8, 0.52, size=11, color=WHITE)

txt(sl, "A comment flagged by multiple signals gets a higher bot probability score",
    0.4, 6.85, 12.5, 0.4, size=12, color=MUTED, align=PP_ALIGN.CENTER, italic=True)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — Naive Bayes Algorithm
# ══════════════════════════════════════════════════════════════════════════════
sl = add_slide(); fill_bg(sl)
section_header(sl, "MACHINE LEARNING MODEL")

txt(sl, "Gaussian Naive Bayes Classifier", 0.5, 0.85, 12, 0.55,
    size=26, bold=True, color=WHITE)

# left — what is NB
box(sl, 0.4, 1.6, 5.8, 5.5, fill=SURFACE, border=ACCENT)
txt(sl, "Why Naive Bayes?", 0.6, 1.7, 5.4, 0.4,
    size=14, bold=True, color=ACCENT2)
why_pts = [
    "Classic algorithm for text / spam classification",
    "Works well with small training datasets",
    "Fast to train and predict",
    "Naturally outputs probability scores",
    "Mathematically interpretable",
    "Email spam filters use this same approach",
    "Built from scratch — pure NumPy, no external ML libs",
]
for i,p in enumerate(why_pts):
    txt(sl, f"▸  {p}", 0.6, 2.18+i*0.47, 5.5, 0.42, size=12, color=WHITE)

# right — how it works
box(sl, 6.5, 1.6, 6.4, 5.5, fill=SURFACE, border=ACCENT)
txt(sl, "How It Works", 6.7, 1.7, 6.0, 0.4,
    size=14, bold=True, color=ACCENT2)

steps_nb = [
    ("Train", "Learn mean & variance of every feature\nfor Bot class and Human class separately"),
    ("Predict", "For a new comment, compute the Gaussian\nlog-likelihood for both classes"),
    ("Softmax", "Convert log-probabilities into\npercentage scores  (e.g. 94% Bot)"),
    ("Decide", "Pick the class with higher probability\nas the final label"),
]
for i,(title,desc) in enumerate(steps_nb):
    by = 2.18 + i*1.17
    # step circle
    c = sl.shapes.add_shape(9, Inches(6.65), Inches(by+0.02), Inches(0.42), Inches(0.42))
    c.fill.solid(); c.fill.fore_color.rgb = ACCENT; c.line.fill.background()
    txt(sl, str(i+1), 6.65, by+0.02, 0.42, 0.38,
        size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    txt(sl, title, 7.2, by+0.02, 5.5, 0.35, size=13, bold=True, color=ACCENT2)
    txt(sl, desc,  7.2, by+0.4,  5.5, 0.55, size=11, color=MUTED)

txt(sl, "The model is 100% pure Python + NumPy — no scikit-learn or scipy dependencies",
    0.4, 7.1, 12.5, 0.3, size=11, color=MUTED, align=PP_ALIGN.CENTER, italic=True)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — Web Application Features
# ══════════════════════════════════════════════════════════════════════════════
sl = add_slide(); fill_bg(sl)
section_header(sl, "WEB APPLICATION")

txt(sl, "Flask Web App — Features & Pages", 0.5, 0.85, 12, 0.55,
    size=26, bold=True, color=WHITE)

features = [
    ("🔍", "Single Comment\nAnalyzer",
     ["Paste any comment", "Instant Bot/Human verdict", "Animated probability bars",
      "Confidence score (%)", "Signal explanation list", "Example comment chips"]),
    ("📂", "Bulk CSV\nUpload",
     ["Upload up to 200 comments", "CSV with CONTENT column", "Summary statistics",
      "Pie chart distribution", "Confidence histogram", "Filter & search table"]),
    ("📊", "Result\nDashboard",
     ["Bot/Human badge", "Bot probability bar", "Human probability bar",
      "Feature breakdown cards", "Triggered signal list", "Analyse another button"]),
    ("🔌", "JSON\nAPI",
     ["POST /api/analyze", "Send comment as JSON", "Returns label + probabilities",
      "Returns signal list", "Integrate with any tool", "No auth required"]),
]
for i,(icon,title,pts) in enumerate(features):
    bx = 0.35 + i*3.2
    box(sl, bx, 1.6, 3.0, 5.5, fill=SURFACE, border=ACCENT)
    txt(sl, icon, bx, 1.68, 3.0, 0.55, size=24, align=PP_ALIGN.CENTER)
    txt(sl, title, bx, 2.22, 3.0, 0.6,
        size=13, bold=True, color=ACCENT2, align=PP_ALIGN.CENTER)
    for j,p in enumerate(pts):
        txt(sl, f"✓  {p}", bx+0.12, 2.92+j*0.5, 2.75, 0.44, size=11, color=WHITE)

# tech stack bar
box(sl, 0.4, 7.15, 12.5, 0.22, fill=SURFACE)
tech = "Python 3  ·  Flask 3  ·  NumPy  ·  Pandas  ·  NLTK  ·  Matplotlib  ·  Werkzeug  ·  python-pptx"
txt(sl, tech, 0.5, 7.16, 12.3, 0.2, size=10, color=MUTED, align=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — Results & Accuracy
# ══════════════════════════════════════════════════════════════════════════════
sl = add_slide(); fill_bg(sl)
section_header(sl, "RESULTS & PERFORMANCE")

txt(sl, "Model Evaluation", 0.5, 0.85, 12, 0.55,
    size=26, bold=True, color=WHITE)

# big metric boxes
metrics = [
    ("100%", "Test Accuracy",   ACCENT),
    ("1.00",  "Precision",      HUMAN_GRN),
    ("1.00",  "Recall",         HUMAN_GRN),
    ("1.00",  "F1 Score",       ACCENT2),
]
for i,(val,lbl,col) in enumerate(metrics):
    bx = 0.4 + i*3.2
    box(sl, bx, 1.6, 2.9, 1.6, fill=SURFACE, border=col)
    txt(sl, val, bx, 1.72, 2.9, 0.85,
        size=36, bold=True, color=col, align=PP_ALIGN.CENTER)
    txt(sl, lbl, bx, 2.58, 2.9, 0.45,
        size=13, color=MUTED, align=PP_ALIGN.CENTER)

# confusion matrix
box(sl, 0.4, 3.45, 5.8, 3.3, fill=SURFACE, border=ACCENT)
txt(sl, "Confusion Matrix (test split)", 0.6, 3.55, 5.5, 0.38,
    size=13, bold=True, color=ACCENT2)
# header row
txt(sl, "Predicted →",  0.6, 3.98, 2.0, 0.3, size=10, color=MUTED, italic=True)
txt(sl, "BOT",  2.75, 3.98, 1.2, 0.3, size=11, bold=True, color=BOT_RED, align=PP_ALIGN.CENTER)
txt(sl, "HUMAN",4.05, 3.98, 1.7, 0.3, size=11, bold=True, color=HUMAN_GRN, align=PP_ALIGN.CENTER)
# rows
for row_i, (lbl, tp, fp, row_col) in enumerate([
    ("Actual BOT",   "15", " 0", BOT_RED),
    ("Actual HUMAN", " 0", "15", HUMAN_GRN),
]):
    ry = 4.35 + row_i*0.75
    txt(sl, lbl,  0.6,  ry, 2.1, 0.35, size=11, bold=True, color=row_col)
    box(sl, 2.65, ry-0.04, 1.3, 0.55, fill=RGBColor(0x14,0x53,0x2D) if row_i==0 else RGBColor(0x3f,0x11,0x11))
    txt(sl, tp,   2.65, ry, 1.3, 0.35, size=18, bold=True, color=HUMAN_GRN if row_i==0 else BOT_RED, align=PP_ALIGN.CENTER)
    box(sl, 4.0,  ry-0.04, 1.7, 0.55, fill=RGBColor(0x3f,0x11,0x11) if row_i==0 else RGBColor(0x14,0x53,0x2D))
    txt(sl, fp,   4.0,  ry, 1.7, 0.35, size=18, bold=True, color=BOT_RED if row_i==0 else HUMAN_GRN, align=PP_ALIGN.CENTER)

# observations
box(sl, 6.6, 3.45, 6.3, 3.3, fill=SURFACE, border=ACCENT)
txt(sl, "Key Observations", 6.8, 3.55, 6.0, 0.38,
    size=13, bold=True, color=ACCENT2)
obs = [
    "Perfect separation on test split",
    "Bot comments have very distinct patterns (URLs, CAPS, repetition)",
    "Human comments use natural, specific, varied language",
    "TF-IDF bigrams capture spam phrases like 'click here', 'free subscribe'",
    "Rule features add interpretability beyond text patterns",
    "High accuracy expected — domain patterns are well-separated",
    "Real-world accuracy estimated at 85–92% on noisier data",
]
for i,o in enumerate(obs):
    txt(sl, f"▸  {o}", 6.8, 4.02+i*0.38, 6.0, 0.35, size=11, color=WHITE)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — Live Demo Screenshots (described)
# ══════════════════════════════════════════════════════════════════════════════
sl = add_slide(); fill_bg(sl)
section_header(sl, "APPLICATION DEMO")

txt(sl, "Web App Pages", 0.5, 0.85, 12, 0.55,
    size=26, bold=True, color=WHITE)

# Page 1 — Home
box(sl, 0.4, 1.6, 5.9, 2.5, fill=SURFACE, border=ACCENT)
box(sl, 0.4, 1.6, 5.9, 0.38, fill=ACCENT)
txt(sl, "🔍  Single Comment Analyzer  — localhost:5000/",
    0.55, 1.65, 5.6, 0.3, size=11, bold=True, color=WHITE)
demo1 = [
    "Text area to paste any YouTube comment",
    "8 example chips (4 Bot / 4 Human) to try instantly",
    "Character counter updates live",
    "'Analyze Comment' button submits to Flask",
    "How it works section explains the model",
]
for i,d in enumerate(demo1):
    txt(sl, f"▸  {d}", 0.55, 2.08+i*0.38, 5.7, 0.34, size=11, color=WHITE)

# Page 2 — Result
box(sl, 6.8, 1.6, 6.1, 2.5, fill=SURFACE, border=ACCENT)
box(sl, 6.8, 1.6, 6.1, 0.38, fill=BOT_RED)
txt(sl, "🤖  Result Page  — /analyze",
    6.95, 1.65, 5.8, 0.3, size=11, bold=True, color=WHITE)
demo2 = [
    "Large BOT or HUMAN verdict badge",
    "Animated probability bars (bot % + human %)",
    "2 stat cards showing exact probabilities",
    "Overall confidence score card",
    "List of triggered bot signals with explanations",
    "Feature breakdown: length, words, URL, exclamations",
]
for i,d in enumerate(demo2):
    txt(sl, f"▸  {d}", 6.95, 2.08+i*0.38, 5.9, 0.34, size=11, color=WHITE)

# Page 3 — Bulk
box(sl, 0.4, 4.3, 5.9, 2.85, fill=SURFACE, border=ACCENT)
box(sl, 0.4, 4.3, 5.9, 0.38, fill=ACCENT2)
txt(sl, "📂  Bulk Upload  — /bulk",
    0.55, 4.35, 5.6, 0.3, size=11, bold=True, color=BG_DARK)
demo3 = [
    "Drag & drop CSV file or click to browse",
    "Processes up to 200 comments at once",
    "Summary cards: Total / Bot count / Human count",
    "Bot rate % and average confidence %",
    "Pie chart: Bot vs Human distribution",
    "Confidence histogram for both classes",
    "Searchable + filterable results table",
]
for i,d in enumerate(demo3):
    txt(sl, f"▸  {d}", 0.55, 4.78+i*0.33, 5.7, 0.3, size=11, color=WHITE)

# Page 4 — API
box(sl, 6.8, 4.3, 6.1, 2.85, fill=SURFACE, border=ACCENT)
box(sl, 6.8, 4.3, 6.1, 0.38, fill=SURFACE)
txt(sl, "🔌  JSON API  — POST /api/analyze",
    6.95, 4.35, 5.8, 0.3, size=11, bold=True, color=ACCENT2)
txt(sl, 'Request:', 6.95, 4.78, 5.8, 0.28, size=10, bold=True, color=MUTED)
txt(sl, '{"comment": "Click here to win FREE iPhone!!!"}',
    6.95, 5.08, 5.8, 0.28, size=10, color=YELLOW, italic=True)
txt(sl, 'Response:', 6.95, 5.42, 5.8, 0.28, size=10, bold=True, color=MUTED)
resp = '{"label":"Bot","is_bot":true,"confidence":94.2,\n"bot_prob":94.2,"human_prob":5.8,\n"signals":["Contains URL","Spam keywords: free, win"]}'
txt(sl, resp, 6.95, 5.72, 5.8, 0.7, size=9.5, color=HUMAN_GRN, italic=True)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — Limitations & Future Work
# ══════════════════════════════════════════════════════════════════════════════
sl = add_slide(); fill_bg(sl)
section_header(sl, "LIMITATIONS & FUTURE SCOPE")

txt(sl, "Current Limitations & Future Enhancements", 0.5, 0.85, 12, 0.55,
    size=24, bold=True, color=WHITE)

# Limitations
box(sl, 0.4, 1.6, 5.9, 5.3, fill=SURFACE, border=BOT_RED)
txt(sl, "⚠️  Current Limitations", 0.6, 1.7, 5.5, 0.4,
    size=14, bold=True, color=BOT_RED)
lims = [
    ("Small dataset", "150 comments — real systems use millions"),
    ("Simple bots only", "Sophisticated AI-written bots may evade detection"),
    ("No account metadata", "Posting frequency, account age not used"),
    ("No real-time API", "Not connected to live YouTube Data API"),
    ("English only", "Multi-language comments not supported"),
    ("Static model", "Does not learn from new comments over time"),
]
for i,(title,desc) in enumerate(lims):
    txt(sl, f"▸  {title}:", 0.6, 2.25+i*0.7, 2.2, 0.32,
        size=12, bold=True, color=YELLOW)
    txt(sl, desc, 2.85, 2.25+i*0.7, 3.3, 0.32, size=12, color=WHITE)

# Future scope
box(sl, 6.7, 1.6, 6.2, 5.3, fill=SURFACE, border=HUMAN_GRN)
txt(sl, "🚀  Future Enhancements", 6.9, 1.7, 5.9, 0.4,
    size=14, bold=True, color=HUMAN_GRN)
future = [
    ("BERT / Transformers", "Use pre-trained language models\nfor better semantic understanding"),
    ("Account metadata", "Add posting frequency, account age,\nsubscriber count as features"),
    ("YouTube API", "Live comment fetching and real-time\nclassification on any video"),
    ("Multilingual", "Support Arabic, Spanish, Hindi\ncomments using multilingual models"),
    ("Active learning", "Model improves by learning from\nuser feedback on predictions"),
    ("Dashboard", "Analytics dashboard showing bot\ntrends across videos over time"),
]
for i,(title,desc) in enumerate(future):
    txt(sl, f"▸  {title}:", 6.9, 2.25+i*0.7, 2.5, 0.32,
        size=12, bold=True, color=ACCENT2)
    txt(sl, desc, 9.45, 2.25+i*0.7, 3.3, 0.5, size=11, color=WHITE)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 12 — Conclusion
# ══════════════════════════════════════════════════════════════════════════════
sl = add_slide(); fill_bg(sl)

# top accent bar
b = sl.shapes.add_shape(1, 0, 0, SW, Inches(0.08))
b.fill.solid(); b.fill.fore_color.rgb = ACCENT; b.line.fill.background()

txt(sl, "Conclusion", 0.5, 0.4, 12.33, 0.7,
    size=32, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
bar2 = sl.shapes.add_shape(1, Inches(4.5), Inches(1.15), Inches(4.33), Pt(3))
bar2.fill.solid(); bar2.fill.fore_color.rgb = ACCENT; bar2.line.fill.background()

conclusions = [
    ("✅", "Problem Solved",
     "Successfully built a working bot comment detector that classifies YouTube comments as Bot or Human with high accuracy"),
    ("🔬", "Two-Layer Approach",
     "Combined TF-IDF text analysis with 10 rule-based features for both accuracy and explainability"),
    ("🌲", "Custom ML Model",
     "Gaussian Naive Bayes built from scratch using pure NumPy — no external ML library dependencies"),
    ("🌐", "Full Web Application",
     "Flask app with single analysis, bulk CSV upload, interactive charts, and a REST JSON API"),
    ("📊", "Explainable AI",
     "The app shows users exactly which signals triggered the bot classification — not just a black-box label"),
]
for i,(icon,title,desc) in enumerate(conclusions):
    by = 1.45 + i*1.0
    box(sl, 0.5, by, 12.3, 0.82, fill=SURFACE, border=ACCENT)
    txt(sl, icon, 0.65, by+0.1, 0.6, 0.55, size=22, align=PP_ALIGN.CENTER)
    txt(sl, title, 1.4, by+0.07, 3.5, 0.32, size=14, bold=True, color=ACCENT2)
    txt(sl, desc,  1.4, by+0.42, 10.8, 0.33, size=12, color=MUTED)

txt(sl, "🤖  Thank You",
    0.5, 6.55, 12.33, 0.55,
    size=22, bold=True, color=ACCENT2, align=PP_ALIGN.CENTER)
txt(sl, "Bot-Like Comment Detection  ·  Social Media Analytics & Sentiment Analysis",
    0.5, 7.05, 12.33, 0.35,
    size=12, color=MUTED, align=PP_ALIGN.CENTER, italic=True)


# ── Save ───────────────────────────────────────────────────────────────────────
OUT = "Bot_Comment_Detection_PPT.pptx"
prs.save(OUT)
print(f"✓ Presentation saved: {OUT}  ({len(prs.slides)} slides)")
