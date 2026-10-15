# 🤖 Bot-Like Comment Detection

A web application for detecting bot-generated comments on YouTube using Machine Learning.

**Subject:** Social Media Analytics & Sentiment Analysis  
**Tech Stack:** Python · Flask · scikit-learn · TF-IDF · Random Forest

---

## Features

- **Single comment analysis** — paste any comment and get an instant bot/human verdict
- **Confidence scores** — probability breakdown with animated visual bars
- **Signal detection** — explains *why* a comment was flagged (URLs, CAPS, repetition, spam keywords)
- **Bulk CSV upload** — classify up to 200 comments at once
- **Charts** — pie chart and confidence histogram for bulk results
- **Filter & search** — filter bulk results by Bot/Human, search by text

---

## Project Structure

```
Bot like comment detection/
├── app.py                  # Flask application
├── train_model.py          # Model training script
├── requirements.txt        # Python dependencies
├── data/
│   └── youtube_spam.csv    # Labelled YouTube comments dataset
├── model/                  # Saved model files (auto-generated)
│   ├── classifier.pkl
│   └── tfidf.pkl
├── templates/
│   ├── base.html           # Base layout (nav, footer)
│   ├── index.html          # Single comment analyzer page
│   ├── result.html         # Prediction result page
│   └── bulk.html           # Bulk upload page
└── static/
    ├── css/style.css       # Dark-theme stylesheet
    └── js/main.js          # UI interactions
```

---

## Setup & Run

### 1. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Train the model (optional — app auto-trains on first run)

```bash
python train_model.py
```

### 4. Start the web app

```bash
python app.py
```

Open your browser at **http://127.0.0.1:5000**

---

## How the Model Works

| Step | Detail |
|------|--------|
| **Dataset** | UCI YouTube Spam Collection — 1,956 real comments (spam / ham) |
| **Text features** | TF-IDF vectoriser with 3,000 features and bigrams |
| **Rule features** | 10 hand-crafted signals: URL presence, uppercase ratio, word repetition, exclamation count, spam keywords, punctuation density, digit ratio, comment length, word count, average word length |
| **Classifier** | Random Forest with 200 trees, balanced class weights |
| **Output** | Binary label (Bot / Human) + probability scores |

### Bot signals detected

- 🔗 External URLs / shortened links  
- 🔠 Excessive uppercase (shouting)  
- 🔁 High word repetition (copy-paste templates)  
- ❗ Multiple exclamation marks  
- 💰 Spam keywords: *free, click, win, earn, subscribe, money, gift, prize…*  
- 📏 Suspiciously short comments  

---

## API Usage

The app also exposes a simple JSON endpoint:

```bash
curl -X POST http://127.0.0.1:5000/api/analyze \
     -H "Content-Type: application/json" \
     -d '{"comment": "Click here to win a FREE iPhone!!!"}'
```

**Response:**
```json
{
  "label": "Bot",
  "is_bot": true,
  "confidence": 94.2,
  "bot_prob": 94.2,
  "human_prob": 5.8,
  "signals": ["Contains URL / external link", "Excessive exclamation marks (3)", "Spam keywords detected: free, click, win"],
  "comment": "Click here to win a FREE iPhone!!!"
}
```

---

## Bulk Upload Format

Upload a `.csv` file with a column named `CONTENT`, `content`, `comment`, or `text`:

```
CONTENT
"I love this song so much!"
"CLICK HERE FOR FREE VBUCKS http://scam.link"
"Subscribe subscribe subscribe now please"
```

---

## Dataset

The dataset (`data/youtube_spam.csv`) is based on the
[UCI YouTube Spam Collection](https://archive.ics.uci.edu/dataset/380/youtube)
— a public set of real YouTube comments labelled as spam or legitimate (ham),
collected from five popular music videos.

- **Class 0** — Human / legitimate comment  
- **Class 1** — Bot / spam comment  
