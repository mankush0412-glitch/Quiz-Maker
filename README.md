# Telegram Quiz Maker Bot

A Telegram bot that converts `.txt` files into interactive Telegram Quiz polls with explanations.

## Features

- Upload a `.txt` file with quiz questions
- Bot sends up to **14 questions** as Telegram Quiz polls
- Each poll has a **10-second** timer
- Options sent **without serial numbers** (just clean text)
- **Solution/Explanation** shown automatically after user answers
- Correct answer tracked by Telegram natively

## Setup

### 1. Get a Telegram Bot Token

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the instructions
3. Copy the bot token you receive

### 2. Environment Variables

Create a `.env` file or set the following in your environment:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Bot

```bash
python bot.py
```

## Deploy on Render

1. Create a new **Background Worker** on [Render](https://render.com)
2. Connect your GitHub repo
3. Set the following:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
   - **Environment Variables:** Add `TELEGRAM_BOT_TOKEN`

> Telegram bots use long-polling — they work as a Background Worker on Render without needing an HTTP port.

## `.txt` File Format

Each question follows this format:

```
Question text here?
A) Option one
B) Option two
C) Option three
D) Option four
Answer: B
Solution: This is the explanation shown after the user answers.

Next question here?
A) Option one
B) Option two
C) Option three
D) Option four
Answer: A
Solution: Explanation for the second question.
```

### Rules

| Rule | Detail |
|------|--------|
| Question separator | Blank line between each question block |
| Options | Labeled `A)`, `B)`, `C)`, `D)` etc. — **no serial numbers in text** |
| Answer line | Must start with `Answer:` followed by the option letter |
| Solution line | Starts with `Solution:` — **optional**, shown after user answers |
| Max questions | **14 per file** (extra are ignored) |
| Solution length | Max 200 characters (Telegram limit) |

### Supported Solution/Explanation Keywords

The bot recognizes any of these prefixes:
- `Solution:`
- `Explanation:`
- `Exp:`
- `Sol:`
- `Reason:`
- `Hint:`

### Example

```
Income from house property is chargeable under:
A) Section 14
B) Section 22
C) Section 23
D) Section 24
Answer: B
Solution: Section 22 specifically deals with income from house property. Section 23 defines annual value and Section 24 covers deductions.
```

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message with menu buttons |
| `/createquiz` | Start quiz creation (then send .txt file) |
| `/help` | Show formatting guide |
| `/token` | Get your user access token |

## Example Interaction

1. User sends `/createquiz`
2. Bot: "Ready to create your quiz! Please send me a .txt file."
3. User uploads `questions.txt`
4. Bot confirms: "Successfully sent 14 quiz questions!"
5. Bot sends 14 quiz polls one by one (2-second gap each)
6. After each poll, when user answers, the **solution** appears automatically

## File Structure

```
quiz-bot/
├── bot.py                  # Main bot — commands, file handler, poll sender
├── quiz_parser.py          # .txt file parser (questions + solutions)
├── requirements.txt        # python-telegram-bot==21.9
├── render.yaml             # Render deploy config (Background Worker)
├── sample_questions.txt    # Sample HP income tax questions with solutions
├── .env.example            # Environment variable template
├── .gitignore
└── README.md
```
