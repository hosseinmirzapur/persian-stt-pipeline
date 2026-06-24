---
name: transcript-polisher
version: 1.0.0
description: >
  Clean and structure raw ASR/STT transcriptions into polished, print-ready HTML
  articles. Handles Persian (Farsi) and similar languages with RTL layout.
  Normalizes garbled speech-to-text output, removes audio artifacts, organizes
  content into logical sections, and produces a beautiful Vazirmatn-typeset
  article optimized for Ctrl+P → PDF export. Use when a user provides a
  transcribed.txt or similar raw STT transcript from a lecture, speech, or
  recorded session and wants a readable, publishable article.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Question
triggers:
  - transcribe
  - transcription
  - normalize transcript
  - clean transcript
  - polish transcript
  - raw text to article
  - speech to text cleanup
  - transcribed file
  - stt output
  - asr output
license: MIT
---

# Transcript Polisher — Raw STT to Polished Article

Turn messy automatic speech recognition (ASR) transcripts into clean, structured, print-ready HTML articles. Designed primarily for Persian (Farsi) but applicable to any RTL or LTR language with similar ASR artifacts.

## Overview

Speech-to-text engines produce transcripts riddled with:
- **Garbled phonetically-similar words** (e.g., `ارز کنم موضوع شما` instead of `عرض کنم خدمت شما`)
- **Repeated filler phrases** from the speaker's oral delivery style
- **Audio cut artifacts** (sound drops, internet interruptions, side chatter)
- **Inconsistent number formats** (spoken-out vs digit)
- **Missing punctuation and paragraph breaks**

This skill systematically normalizes those artifacts while preserving **every bit of substantive content**, then wraps the result in a beautiful, print-optimized HTML document.

## Input Expectations

The tool will receive a file (often `transcribed.txt`) containing:
- Raw STT output, one line per audio segment
- Persian text with pervasive phonetic garbling
- Interleaved audio/environmental artifacts (`صدا قطع شد`, `اه الان وصله`, etc.)
- Zero formatting, no paragraphs, no headings

## Step-by-Step Workflow

### Step 1: Read & Catalog Artifacts

Read the entire transcript first. Build a mental (or written) catalog of:

**Repeated ASR errors** — words the engine consistently misheard:
| Garbled (ASR output) | Correct |
|---|---|
| `ارز کنم موضوع شما` / `عرض کنم موضوع شما` / `از کنم حضور شما` | `عرض کنم خدمت شما` |
| `حیعت مدیره` / `حیط مدیره` / `حید مدیره` / `حیات و مدیره` | `هیئت مدیره` |
| `علل بدل` / `علال بدر` / `علال بدله` / `علل بدله` | `علی‌البدل` |
| `آینامه` / `آینامی` | `آیین‌نامه` |
| `مادی` | `ماده` |
| `عوضیت` | `عضویت` |
| `شاقل` | `شاغل` |
| `طابع` | `تابع` |
| `اوائد` | `عوائد` |
| `تحسیس` | `تأسیس` |
| `مختزی` | `مقتضی` |
| `ارزامیه` | `الزامی` |
| `منعود` | `منوط` |
| `تدریز` | `تدریس` |
| `وضایف` | `وظایف` |
| `حضور قیاب` | `حضور و غیاب` |
| `حضر نکردیم` | `حاضر نکردیم` |
| `دفتر اصناد رسمی` | `دفتر اسناد رسمی` |
| `مناسب` (as in `در مناسب خوب`) | `مناصب` |
| `مصبت` (as in `مصبت قرار دادیم`) | `ثبت` |
| `چشم بوشی` | `چشم‌پوشی` |
| `اقماز کردیم` | `اغماض کردیم` |
| `نظامات` (verify context) | Usually correct — means "regulations" |
| `وظایف` | Correct as-is in Persian |

**Audio/environmental artifacts** to remove entirely:
- `صدا قطع شد`, `قطع شده بود`, `اه الان وصله؟`, `وصل شده`
- `خانم پورسکری میگه صدا قطع هست`
- Internet/connection complaints, side comments to participants
- Repeated filler like `عرض کنم خدمت شما` used >40 times → keep 2-3 for transition

**Number format conversions:**
| Spoken | Written |
|---|---|
| `هزار سه شونزده` | `۱۳۱۶` |
| `هزار سه پنجه و چهار` | `۱۳۵۴` |
| `سی چهل تومن` / `سی چلتومنبره` | `۳۰-۴۰ میلیون تومان` |
| `ده درصد` | `۱۰٪` |
| `بیست هشت دوازده نود و نه` | `۲۸/۱۲/۱۳۹۹` |

### Step 2: Normalize the Text

Apply the catalog systematically:
1. Fix all garbled words using the reference table
2. Remove audio artifacts and repeated filler (keep only what aids readability)
3. Convert spoken numbers to standard Persian digits
4. Smooth sentence fragments into flowing prose — join broken lines, add conjunctions where needed
5. **CRITICAL: Do not remove any substantive content.** The quantity of information in the final text must match the original. Only remove audio artifacts and gratuitous filler.

### Step 3: Structure Into Sections

Identify the natural topic boundaries in the lecture/discourse:

1. **Introduction** — what is this about, why it matters
2. **Historical/legal background** — earlier laws, original framework
3. **Changes and evolution** — how laws/structures evolved
4. **Details and specifics** — articles, conditions, requirements
5. **Related topics** — insurance, retirement, etc.
6. **Final remarks** — exam info, closing words

Reorganize the normalized text into these sections. The original transcript may jump around — that's normal. Re-order for clarity but preserve every fact.

### Step 4: Build the HTML Article

Create a single self-contained HTML file with the following design spec:

```
Design Spec:
- Language: RTL (dir="rtl"), lang="fa"
- Font: Vazirmatn from Google Fonts (weights 300-800)
- Body bg: #fafaf7, Article bg: #fffdfa (warm paper)
- Text color: #1a1a1a, line-height: 2
- Max-width: 750px, centered
- Headings: Gold/amber accents (#8b6914, #c9a96e)
- Print-optimized: @page margins, @media print removes bg, 
  print-color-adjust: exact for highlights, page-break-inside: avoid
- Legal quotes: bordered block with #f5f0e8 bg, gold right border
- Highlight boxes: #f0ebe0 bg for notes and tips
- Footer with attribution
- No animations, no JS dependencies
- Prepare for Ctrl+P → A4 PDF
```

#### HTML Template Skeleton

```html
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>...</title>
  <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    /* RTL, paper aesthetic, print rules, legal-quote, highlight-box, heading styles */
  </style>
</head>
<body>
  <div class="page">
    <header class="article-header">...</header>
    <!-- sections -->
    <footer class="article-footer">...</footer>
  </div>
</body>
</html>
```

### Step 5: Verify

Read through the final HTML and confirm:
- [ ] Every substantive fact from the original is present
- [ ] No garbled words remain
- [ ] No audio artifacts remain
- [ ] Sections flow logically
- [ ] HTML validates (no unclosed tags, proper nesting)
- [ ] Print styles are applied
- [ ] Font loads correctly (Vazirmatn from Google Fonts)

## Persian-Specific Notes

### Common ASR Confusion Patterns in Persian

The Persian language presents unique challenges for speech-to-text due to:
- **Homophones**: Words that sound identical but differ in spelling (e.g., `طعام` vs `طعام`)
- **Colloquial elision**: Dropped consonants in fast speech (`میرم` instead of `می‌روم`)
- **Arabic borrowings**: Words with `ع`, `غ`, `ح` that STT often mangles
- **Izafat**: The `-e` suffix often gets merged with adjacent words
- **Compound verbs**: `عرض کنم` can become `ارز کنم`, `از کنم`, etc.

### Working with the Reference Table

The table in Step 1 is not exhaustive — add to it as you encounter new patterns. The most frequently garbled phrase in Persian lecture STT output is `عرض کنم خدمت شما` which can appear as:
- `ارز کنم موضوع شما`
- `عرض کنم موضوع شما`
- `از کنم حضور شما`
- `عرض کنم خدمت شما` (correct)
- `از کنم`
- `ارز کنم`
- ...any combination thereof

Always normalize to `عرض کنم خدمت شما` or remove if it's used as pure filler (>3 times).

## Design Reference

The `article.html` produced by this skill should follow the same visual language as the golden reference at `/home/smartinex/workspace/scripts/article.html` (the first output produced for this skill).

Key design elements to replicate:
- Warm, paper-like color palette (#fafaf7 / #fffdfa)
- Gold accent (#c9a96e, #8b6914) for headings and borders
- Vazirmatn as the sole typeface
- Legal quotes with tinted background and right border
- Highlight boxes for notes
- Clean, generous spacing (line-height: 2)
- Print-first mindset (everything must survive Ctrl+P to PDF cleanly)

## Quality Checklist

Before declaring the task complete, verify:

| Check | Criterion |
|---|---|
| Content completeness | All original facts preserved |
| Accuracy | Every correction is valid Persian |
| Cleanliness | No audio artifacts, garbled words, or filler |
| Structure | Logical section flow with headings |
| Print readiness | `@page`, `@media print`, `page-break-inside` |
| Font | Vazirmatn loaded, RTL direction correct |
| Visual | Paper-like, gold accents, no JS dependencies |
