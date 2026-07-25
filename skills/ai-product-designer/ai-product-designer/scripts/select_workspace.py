#!/usr/bin/env python3
"""Open the native macOS folder chooser and print the selected workspace path."""

from __future__ import annotations

import argparse
import subprocess
import sys


def select_workspace(prompt: str) -> str:
    if sys.platform != "darwin":
        raise RuntimeError("Native folder selection is currently supported on macOS only.")

    script = (
        "on run argv\n"
        "  set selectedFolder to choose folder with prompt (item 1 of argv)\n"
        "  return POSIX path of selectedFolder\n"
        "end run"
    )
    result = subprocess.run(
        ["osascript", "-e", script, prompt],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip()
        if "(-128)" in message:
            raise KeyboardInterrupt
        raise RuntimeError(message or "フォルダ選択画面を開けませんでした。")
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prompt",
        default="AI Product Designerの作業フォルダを選択してください",
    )
    args = parser.parse_args()
    try:
        workspace = select_workspace(args.prompt)
    except KeyboardInterrupt:
        print("Folder selection was cancelled.", file=sys.stderr)
        return 2
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1
    print(workspace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
