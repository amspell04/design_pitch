---
name: critique-image
description: Critique design images the user provides (mockups, logos, layouts, photos) for use in a pitch or user story, using what you see plus measured facts from image_info.
---

# Image critique

Goal: honest, specific, useful feedback the user can act on, and a clear verdict on whether each image belongs in the document.

## 1. Look, then measure
For each image: study it, then call `image_info` with its path (given by the user, or shown as "[Attached image saved at ...]"). Use the measurements to back up or correct your impression. Never claim a number you didn't get from `image_info`. If you cannot actually see the image, say so and ask for a description instead of guessing.

## 2. Rubric
Judge only what is actually visible. Skip a point that doesn't apply.
- **Hierarchy**: is it clear where to look first, second, third?
- **Legibility**: text size and contrast, readable at the size it will appear on a page.
- **Layout and spacing**: alignment, consistent margins, crowding or dead space.
- **Colour**: palette cohesion, accessible contrast, fit with the brand colours if the user gave them.
- **Consistency**: type, icon and component style match each other, and the rest of the set.
- **Purpose**: does it support the point it is attached to? Is it clear what the viewer should take from it?
- **Technical quality**: resolution, blur, compression, cropping (use `image_info` warnings).

## 3. Output format
Per image, keep it short:
1. **Verdict**: use as is / use after small fixes / rework first (one line).
2. **Strengths**: 1-3 specific points.
3. **Issues**: ordered by impact, each with a concrete fix ("Increase the body text size; it is unreadable at page width", not "improve readability").
4. **Placement**: which part of the document it fits best, and a suggested caption.

If there are several images, finish with 2-3 lines on how well they work as a set (consistency, gaps).

## 4. Rules
- Critique the work, be direct but constructive. Do not flatter.
- Don't invent context (brand guidelines, audience, intent). If it affects the critique, ask.
- If asked to continue to a document, load the matching skill and use the verdicts: leave out or flag images that need rework, and write captions from your placement notes.
