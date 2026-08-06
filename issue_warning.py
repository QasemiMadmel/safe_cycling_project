# issue_warning.py

import json
import os
import time
import threading

from gpiozero import DigitalOutputDevice


WARNING_GPIO_PIN = 17  # physical pin 11
WARNING_DURATION = 1.0

DANGER_STATUS_FILE = ("/home/strawberry/safe_cycling_project/runtime/danger_status.json")


def write_danger_status(danger_active: bool) -> None:

    temporary_file = DANGER_STATUS_FILE

    try:
        with open(
            temporary_file,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                {"danger": danger_active},
                file
            )

            file.flush()
            os.fsync(file.fileno())

        os.replace(
            temporary_file,
            DANGER_STATUS_FILE
        )

        print(
            "Web danger status:",
            danger_active,
            "at",
            time.monotonic()
        )

    except OSError as error:
        print("Could not write web danger status:")
        print(error)


def issue_warning(
    danger_event: threading.Event,
    stop_event: threading.Event
) -> None:

    warning_output = DigitalOutputDevice(
        WARNING_GPIO_PIN,
        active_high=True,
        initial_value=False
    )

    write_danger_status(False)

    try:
        while not stop_event.is_set():

            # Regular timeout allows the thread to notice stop_event.
            danger_detected = danger_event.wait(timeout=0.1)

            if stop_event.is_set():
                break

            if not danger_detected:
                continue

            danger_event.clear()

            warning_output.on()
            write_danger_status(True)

            warning_until = (
                time.monotonic()
                + WARNING_DURATION
            )

            print("danger occurred")

            while not stop_event.is_set():

                remaining_time = (
                    warning_until
                    - time.monotonic()
                )

                if remaining_time <= 0:
                    break

                new_danger = danger_event.wait(
                    timeout=min(remaining_time, 0.1)
                )

                if new_danger:
                    print("new danger occurred")

                    danger_event.clear()

                    # Only extend the warning duration.
                    # The JSON status is already true.
                    warning_until = (
                        time.monotonic()
                        + WARNING_DURATION
                    )

            warning_output.off()
            write_danger_status(False)

    finally:
        print("danger event stopped")

        warning_output.off()
        warning_output.close()

        write_danger_status(False)
