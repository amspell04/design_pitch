# Plan

Status key: [x] done and checked, [~] built but not tested with a model, [ ] not started.

## Phase 0: Idea and scope
- [x] Decide on prose documents (not slides) built from the user's text and images
- [x] Two document types: executive pitch, user story
- [x] Drop generated visuals; add image critique instead
- [x] Local open-weight models only; Google ADK + LiteLLM + Ollama

## Phase 1: Renderer
- [x] `build_pdf` tool with typed blocks, validation, cover page, footer (`tools.py`)
- [x] Tested by hand with block JSON; output visually checked (cover, callout, bullets, image + caption)
- [x] Invalid input returns readable errors and writes nothing
- [x] `output/` gitignored

## Phase 2: Skills
- [x] `executive-pitch` skill
- [x] `user-story` skill
- [x] Skills as `SKILL.md` folders with kebab-case names (ADK requirement); old empty `.py` skill files removed
- [~] Skills followed correctly by a model (not tested)

## Phase 3: Agent wiring
- [x] Fix `agent.py`: imports, tool name mismatch, skills loaded from `skills/`
- [x] Agent module loads; skills and tools register
- [x] `agents/requirements.txt`
- [ ] Run the agent end to end with Ollama (`adk run` / `adk web` from `agents/`)

## Phase 4: Image critique
- [x] `image_info` tool (resolution, contrast, colours, warnings), tested on a sample and a missing file
- [x] `critique-image` skill with rubric and output format
- [x] `save_uploaded_images` callback so attached images get file paths (tested with a fake upload)
- [~] Real attachment flow in `adk web` with a vision model (not tested)

## Next

1. **Environment**: create a Python 3.13 venv (current `.venv` is empty, 3.10) and `pip install -r agents/requirements.txt`.
2. **Pick models**: pull a vision-capable Ollama model and a stronger text model than `qwen3.5:2b`; update `agent.py`.
3. **First real run**: give the agent a short brief and 2-3 images for each document type. Check:
   - does it load the right skill, ask about gaps, and not invent facts?
   - does it emit valid blocks, or loop on `build_pdf` errors?
   - are attached images saved and placed correctly?
4. **Tune from failures**: tighten skill wording, or split writing and block-building into two steps if the model struggles.
5. **Critique quality**: compare critiques against the actual images; adjust the rubric if they are generic or wrong.
6. **Critique to document handoff**: confirm verdicts feed into the pitch/user-story (flag or omit images that need rework).
7. **Dockerfile**: currently empty. Package the agent; Ollama stays on the host.
8. **Brand theming**: configurable accent colour, font and logo on the cover instead of fixed defaults.
9. **Tests**: unit tests for `build_pdf` validation and `image_info`.
10. **Optional**: a shared "gather facts" step so pitch and user story write from one brief; a `critique-design` skill
    that judges a design against a stakeholder's ask (an earlier stub was removed).
