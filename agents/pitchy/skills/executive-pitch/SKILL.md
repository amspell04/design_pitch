---
name: executive-pitch
description: Write an executive branding pitch document from the user's notes and images, then render it to PDF with build_pdf (doc_type "pitch").
---

# Executive pitch

Goal: a short, persuasive document an executive can read in five minutes and decide on.

## 1. Gather what you need
You need: the **problem or opportunity**, the **proposed brand/design direction**, the **evidence** (research, metrics, examples), the **audience** (who decides), and the **ask**. If the problem, the direction or the ask is missing, ask the user one short question. Never invent metrics, quotes or customer facts. If something is unknown, leave it out.

## 2. Images
Only use image files the user gave you, by their exact path. If you don't know what an image shows, ask the user for a one-line description. Place each image next to the text it supports and give it a caption that says what to notice, not just what it is.

## 3. Structure (use this order)
1. `heading` **The situation**: one paragraph on the problem or opportunity, in the audience's terms.
2. `callout` titled "The big idea": the proposal in one or two sentences.
3. `heading` **Our approach**: the design direction. Use `bullets` for 3-5 key elements, and `image` blocks for the visuals.
4. `heading` **Why it works**: the evidence. Facts and examples only.
5. `heading` **Impact**: what changes if approved (for customers, for the business).
6. `callout` titled "The ask": what you need decided, by when, and the next step.

Keep the whole document to 1-3 pages of content. Lead with the conclusion. Prefer short paragraphs and concrete words over adjectives.

## 4. Render
Call `build_pdf` once with `doc_type="pitch"`, a clear `title`, a one-line `subtitle`, and the blocks in the order above. If it returns `status: "error"`, fix the listed problems and call it again. When it succeeds, tell the user the file path and give a two-line summary of what the document says.
