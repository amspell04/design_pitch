---
name: user-story
description: Write a user story document that explains how the user's design fits a user's need, from their notes and images, then render it to PDF with build_pdf (doc_type "user_story").
---

# User story document

Goal: show a stakeholder, step by step, how the design serves a specific person trying to get something done.

## 1. Gather what you need
You need: the **persona** (who, and their context), the **goal** (what they are trying to achieve and why), and the **design** being explained (which screens or assets). If the persona or goal is missing, ask the user one short question. Never invent research findings or quotes. A persona may be a plausible example, but say so ("Example persona").

## 2. Images
Only use image files the user gave you, by their exact path. Each image should be tied to one step of the scenario. If you don't know what an image shows, or which step it belongs to, ask the user. Captions should name the step and what the user sees there.

## 3. Structure (use this order)
1. `heading` **Who this is for**: the persona in 2-3 sentences (role, context, frustrations).
2. `callout` titled "User story": exactly one sentence, "As a <persona>, I want <goal> so that <benefit>."
3. `heading` **Scenario**: a short paragraph setting the situation in which they use the design.
4. `heading` **How the design supports each step**: for each step, a `heading` with `level: 2` ("Step 1: ..."), a paragraph on what the user is doing and thinking, a paragraph on how the design helps, and the matching `image` if there is one.
5. `heading` **Acceptance criteria**: `bullets`, each a checkable statement ("The user can ... without ...").
6. `callout` titled "Takeaway": one or two sentences on how the design delivers on the user story.

Be concrete: name what is on the screen and what the user does. Do not describe design features that no step uses.

## 4. Render
Call `build_pdf` once with `doc_type="user_story"`, a clear `title`, a one-line `subtitle`, and the blocks in the order above. If it returns `status: "error"`, fix the listed problems and call it again. When it succeeds, tell the user the file path and give a two-line summary.
