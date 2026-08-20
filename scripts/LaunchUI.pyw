"""Double-click launcher for the L5X Memory Analyzer UI -- no command prompt.

Requires `pip install -e .` to have been run once from the repo root first
(same as running it from the command line). Starts the server with no file
pre-loaded -- use the File Open... button in the browser once it opens.

To make a desktop shortcut (James, 2026-08-20): right-click this file ->
Send to -> Desktop (create shortcut). Windows runs .pyw files with
pythonw.exe by default, which has no console window, so double-clicking the
shortcut just opens your browser straight to the tool.
"""

from l5x_memory_analyzer.ui.server import run

if __name__ == "__main__":
    run(None, open_browser=True)
