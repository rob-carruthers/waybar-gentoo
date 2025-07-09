#!/usr/bin/env python3

from datetime import datetime
import json
from pathlib import Path
import subprocess
import time

EIX_CACHE = "/var/cache/eix/portage.eix"
INTERVAL = 300
WITH_BDEPS = False


def get_updates(with_bdeps: bool) -> list[str]:
    if with_bdeps:
        command = ["emerge", "-NupDq", "--with-bdeps", "y", "world"]
    else:
        command = ["emerge", "-NupDq", "world"]

    output = subprocess.run(command, capture_output=True).stdout.decode().split("\n")
    updates = [line for line in output if "ebuild" in line or "binary" in line]

    return updates


def get_json(updates: list[str], updated_time_epoch: float | None = None) -> dict[str, str]:
    n_updates = len(updates)

    if n_updates > 0:
        class_ = "pending-updates"
        tooltip = "\n".join(updates)
        text = str(n_updates)

    else:
        class_ = "updated"
        tooltip = "No updates."
        text = ""

    if updated_time_epoch is not None:
        updated_time = datetime.fromtimestamp(updated_time_epoch)
        updated_time_formatted = updated_time.strftime("%d/%m %H:%M")
        tooltip += f"\n\n(DB updated: {updated_time_formatted})"

    output = {"class": class_, "alt": class_, "text": text, "tooltip": tooltip}

    return output


def get_db_last_updated_time() -> float | None:
    cache_file = Path(EIX_CACHE)
    if cache_file.exists():
        updated_time_epoch = cache_file.stat().st_mtime
    else:
        updated_time_epoch = None

    return updated_time_epoch


def do_output(updated_time_epoch: float | None = None) -> None:
    updates = get_updates(with_bdeps=WITH_BDEPS)
    output = get_json(updates=updates, updated_time_epoch=updated_time_epoch)
    print(json.dumps(output), flush=True)


def main():
    updated_time_epoch = get_db_last_updated_time()
    previous_update_time = updated_time_epoch
    do_output(updated_time_epoch)

    while True:
        time.sleep(INTERVAL)
        updated_time_epoch = get_db_last_updated_time()

        if updated_time_epoch is None or previous_update_time is None:
            do_output(updated_time_epoch)

        elif updated_time_epoch > previous_update_time:
            previous_update_time = updated_time_epoch
            do_output(updated_time_epoch)


if __name__ == "__main__":
    main()
