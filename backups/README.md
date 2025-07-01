# Backups Directory

This directory is **not** intended to hold version-controlled artifacts.

It is created automatically at runtime by various scripts and deployment pipelines to temporarily store database dumps or other backup files such as:

• `custom_gpt_adapter_<timestamp>.sql` – database dump created by the Custom GPT Adapter production deployment script.
• `openmemory_<timestamp>.tar.gz` – archive produced by the OpenMemory maintenance routines.

All actual backup files are ignored by Git via the project-wide `.gitignore` rule. Only this `README.md` (and the optional `.gitkeep`) are tracked so that the folder exists in every fresh clone, keeping the runtime path predictable for scripts while ensuring the repository stays free of large or sensitive dump files.

If you need to change where backups are written, update the relevant scripts instead of committing backup data here.