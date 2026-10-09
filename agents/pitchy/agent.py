import os
from pathlib import Path

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.skills import load_skills_from_dir
from google.adk.tools import skill_toolset

from .image_tools import image_info, save_uploaded_images
from .tools import build_pdf

skills = load_skills_from_dir(Path(__file__).parent / "skills")

root_agent = Agent(
    model=LiteLlm(model=os.getenv("PITCHY_MODEL", "ollama_chat/qwen3.5:2b"), think=False),
    name="pitchy",
    instruction=(
        "You help users create branding documents as PDFs from the text and images they give you. "
        "There are two document types: an executive pitch (load the executive-pitch skill) and a "
        "user story explaining how a design fits a user's need (load the user-story skill). "
        "If it's unclear which one the user wants, ask. Always load the matching skill before writing, "
        "follow its structure, and finish by calling build_pdf. When the user asks for feedback on "
        "images, load the critique-image skill. Only use image paths the user gave you, "
        "and never invent facts, metrics or quotes; ask the user if something is missing."
    ),
    tools=[
        skill_toolset.SkillToolset(skills=skills),
        build_pdf,
        image_info,
    ],
    before_model_callback=save_uploaded_images,
)
