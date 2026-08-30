import os


FILES_PER_MEASUREMENT = 4


def cleanup_old_measurements(
    measurement_dir,
    max_measurement_files
):

    if not os.path.exists(measurement_dir):
        return

    measurement_files = []

    for filename in os.listdir(measurement_dir):

        filepath = os.path.join(
            measurement_dir,
            filename
        )

        if os.path.isfile(filepath):
            measurement_files.append(filepath)

    measurement_files.sort(
        key=os.path.getmtime
    )

    while (
        len(measurement_files) + FILES_PER_MEASUREMENT
        > max_measurement_files
    ):

        files_to_delete = measurement_files[
            :FILES_PER_MEASUREMENT
        ]

        for filepath in files_to_delete:

            try:
                os.remove(filepath)
                print(
                    "Deleted old measurement file:",
                    filepath
                )

            except OSError as error:
                print(
                    "Could not delete:",
                    filepath
                )
                print(error)

        measurement_files = measurement_files[
            FILES_PER_MEASUREMENT:
        ]
