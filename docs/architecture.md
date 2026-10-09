# Idea

Create an agent that can help create and format executive branding pitch documents. The user gives the agent text,
notes and images; the agent writes the document content and a local tool renders it to a PDF. The agent can also look
at the screens/images the user created and critique them (like I did with Muse).

For this project we rely on open-weight models run locally, since this is a personal workflow improvement.

# Outputs

Two document types, rendered by the same tool:

| doc_type     | Purpose                                                         | Skill            |
|--------------|-----------------------------------------------------------------|------------------|
| `pitch`      | Executive branding pitch: situation, big idea, approach, evidence, impact, the ask | `executive-pitch` |
| `user_story` | Explains how the design fits a user story: persona, story, scenario, step-by-step design support, acceptance criteria | `user-story` |

These are prose documents (not slides). Images are the user's own; the agent places and captions them. It does not
generate images.

# Agent

Framework: Google ADK (`google-adk`) with LiteLLM + Ollama.

- name: `pitchy` (`agents/pitchy/agent.py`)
- model: local Ollama model via `LiteLlm`. Currently `qwen3.5:2b` (text only). Image critique needs a
  vision-capable model.
- tools: `build_pdf`, `image_info`
- skills: `executive-pitch`, `user-story`, `critique-image`
- callback: `before_model_callback=save_uploaded_images`

## Responsibilities split

The model decides *what to say*. Deterministic code does everything else.

| Model (judgment)                                  | Code (deterministic)                          |
|---------------------------------------------------|-----------------------------------------------|
| Pick doc type, ask for missing information        | Validate block structure and image paths      |
| Write content following a skill's structure       | Lay out and render the PDF                    |
| Look at images and critique them                  | Measure images (resolution, contrast, colours) |
| Caption and place images                          | Save chat uploads to disk                     |

## Tools

### `build_pdf(title, doc_type, blocks, output_name, subtitle="", author="")` (`tools.py`)
Renders with ReportLab (pure Python, no system dependencies). Output goes to `agents/pitchy/output/`.

`blocks` is an ordered list of typed dicts:

- `heading` (`text`, `level` 1 or 2)
- `paragraph` (`text`, supports `**bold**` and `*italic*`)
- `bullets` (`items`)
- `image` (`path`, optional `caption`)
- `callout` (`text`, optional `title`)

Validates everything before writing anything. Returns `{"status": "ok", "path", "pages"}` or
`{"status": "error", "errors": [...]}` so the model can correct and retry. Output is a cover page plus content pages
with page numbers; `doc_type` selects the label and accent colour.

### `image_info(path)` (`image_tools.py`)
Returns resolution, format, aspect ratio, file size, brightness, contrast, dominant colours and warnings
(low resolution for full-width use, very dark/bright, low contrast, extreme aspect ratio). Gives the model facts a
visual read cannot.

## Skills (`agents/pitchy/skills/<name>/SKILL.md`)

Skills are instructions only: when to ask questions, what structure to write, how to call the tool. Names must be
kebab-case and match their folder.

- `executive-pitch`: gather facts, then situation, big idea, approach (with images), why it works, impact, the ask.
- `user-story`: persona, one-sentence story, scenario, one section per step tying an image to how the design helps,
  acceptance criteria, takeaway.
- `critique-image`: look, then call `image_info`, apply a rubric (hierarchy, legibility, layout, colour, consistency,
  purpose, technical quality), output a verdict, strengths, ranked issues and placement/caption per image.

## Image handling

A vision model receives attached images as raw bytes with no filename, but `build_pdf` and `image_info` need paths.
`save_uploaded_images` (a `before_model_callback`) writes attached images to `agents/pitchy/inputs/` and appends
`[Attached image saved at <path>]` to the user message. It is idempotent (hash-named files, note only added once).
Images referenced only by a typed path can be measured and placed, but the model cannot see them.

## Flow

```
user text + images
   -> save_uploaded_images (callback)        saves uploads, adds paths to the message
   -> agent picks doc type, asks for gaps
   -> [optional] critique-image skill + image_info
   -> executive-pitch | user-story skill     writes blocks
   -> build_pdf                              validates, renders, returns path
   -> agent reports path + short summary
```

# Layout

```
agents/
  requirements.txt
  pitchy/
    agent.py          root agent
    tools.py          build_pdf
    image_tools.py    image_info, save_uploaded_images
    skills/           executive-pitch, user-story, critique-image
    output/           generated PDFs (gitignored)
    inputs/           saved uploads (gitignored)
docs/
  architecture.md
  plan.md
```

# Constraints and risks

- **Model size**: a 2B model is unlikely to chain skill loading, writing and a valid structured tool call reliably.
  Needs a larger model, and a vision model for critique.
- **Hallucinated critique/content**: small vision models invent details. Skills say to judge only what is visible,
  use only provided facts, and ask when information is missing.
- **Open-weight/local only**: no hosted image generation or hosted models.
- **Open questions**: Docker packaging (Dockerfile is empty), brand theming (colours/fonts/logo are currently fixed
  defaults), whether pitch and user story should share a "gather facts" step.
