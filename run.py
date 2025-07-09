#!/usr/bin/env python3

import json
import subprocess
import time

INTERVAL = 1800
WITH_BDEPS = False


def update_status(with_bdeps: bool) -> list[str]:
    if with_bdeps:
        command = ["emerge", "-NupDq", "--with-bdeps", "y", "world"]
    else:
        command = ["emerge", "-NupDq", "world"]

    output = subprocess.run(command, capture_output=True).stdout.decode().split("\n")
    updates = [line for line in output if "ebuild" in line or "binary" in line]

    return updates


def get_json(updates: list[str]) -> dict[str, str]:
    n_updates = len(updates)

    if n_updates > 0:
        class_ = "pending-updates"
        tooltip = "\n".join(updates)
        text = str(n_updates)

    else:
        class_ = "updated"
        tooltip = "No updates."
        text = ""

    output = {"class": class_, "alt": class_, "text": text, "tooltip": tooltip}

    return output


def main():
    while True:
        updates = update_status(with_bdeps=WITH_BDEPS)
        output = get_json(updates=updates)
        print(json.dumps(output), flush=True)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
