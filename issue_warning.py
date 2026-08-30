import json
import os
import time
import threading

from gpiozero import DigitalOutputDevice


WARNING_GPIO_PIN = 17
SAFE_GPIO_PIN = 27

WARNING_DURATION = 2.0
SWITCH_DELAY = 0.02

DANGER_STATUS_FILE = (
    "/home/strawberry/safe_cycling_project/runtime/danger_status.json"
)


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

    safe_output = DigitalOutputDevice(
        SAFE_GPIO_PIN,
        active_high=True,
        initial_value=False
    )

    warning_output.off()
    safe_output.on()

    print("STATE: SAFE -> green ON, red OFF")

    write_danger_status(False)

    try:
        while not stop_event.is_set():

            danger_detected = danger_event.wait(
                timeout=0.1
            )

            if stop_event.is_set():
                break

            if not danger_detected:
                continue

            danger_event.clear()

            safe_output.off()

            time.sleep(SWITCH_DELAY)

            warning_output.on()

            print("STATE: DANGER -> green OFF, red ON")

            write_danger_status(True)

            warning_until = (
                time.monotonic()
                + WARNING_DURATION
            )

            while not stop_event.is_set():

                remaining_time = (
                    warning_until
                    - time.monotonic()
                )

                if remaining_time <= 0:
                    break

                new_danger = danger_event.wait(
                    timeout=min(
                        remaining_time,
                        0.1
                    )
                )

                if new_danger:

                    print("new danger occurred")

                    danger_event.clear()

                    warning_until = (
                        time.monotonic()
                        + WARNING_DURATION
                    )

            if stop_event.is_set():
                break

            warning_output.off()

            time.sleep(SWITCH_DELAY)

            safe_output.on()

            print("STATE: SAFE -> green ON, red OFF")

            write_danger_status(False)

    finally:

        print("warning thread stopped")

        warning_output.off()
        safe_output.off()

        warning_output.close()
        safe_output.close()

        write_danger_status(False)
