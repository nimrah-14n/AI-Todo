---
id: "005"
title: "Phase I Interactive Menu UI"
stage: "green"
date: "2025-12-31"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "phase1-console"
branch: "master"
user: "User"
command: "SP.IMPLEMENT — Interactive Menu UI"
labels: ["cli","menu","interactive","phase1"]
links:
  spec: "null"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - "phase-1/src/todo/menu.py (new)"
  - "phase-1/src/todo/__main__.py (modified)"
  - "phase-1/main.py (new)"
tests:
  - "All 65 existing tests pass"
---

## Prompt

SP.IMPLEMENT — Interactive Menu UI

Role:
You are an expert Python CLI application developer.

Task:
Implement an interactive, menu-driven terminal interface for the Todo Application (Phase I) that displays a formatted heading and numbered options when `python main.py` is executed.

UI Requirements:
- Display the following heading exactly at the top of the terminal:

  ==============================================
  TODO APPLICATION - PHASE I
  ==============================================

- Show the current number of tasks
- Display a numbered menu with the following options:
  1. Add Task
  2. View Tasks
  3. Update Task
  4. Delete Task
  5. Mark Task Complete
  6. Exit

- Prompt the user with:
  `Select an option (1-6):`

Behavior Rules:
- Run inside a continuous loop until the user selects "Exit"
- Validate user input and handle invalid selections gracefully
- Use plain ASCII only (no external libraries)
- Do not remove or break existing Phase 1 functionality
- Map each menu option to the corresponding TaskManager functions

## Response snapshot

Created interactive menu-driven terminal interface for Phase I Todo Application:
1. New `menu.py` module with `run_menu()` function displaying formatted header, task count, and numbered menu options
2. Updated `__main__.py` to use new menu interface by default (with `--repl` flag for legacy mode)
3. New `main.py` entry point at project root
4. All 65 existing tests pass without modification
5. Menu maps to TaskManager: add_task, get_all_tasks, update_task, delete_task, toggle_complete

## Outcome

- ✅ Impact: Interactive menu-driven interface implemented for Phase I todo application
- 🧪 Tests: All 65 existing tests pass (no regression)
- 📁 Files: 3 files created/modified
- 🔁 Next prompts: None
- 🧠 Reflection: Leveraged existing TaskManager and CLI formatting functions to avoid code duplication. Added `--repl` flag for backward compatibility with legacy command-based interface.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): All 65 tests PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add input validation helper functions to menu.py for reusability
