
import matplotlib.pyplot as plt


def plot_clusters(
    ax,
    x,
    y,
    clusters,
    cluster_colors,
    x_limit,
    y_limit
):

    ax.clear()

    ax.scatter(
        x,
        y,
        s=2,
        c="blue"
    )

    for cluster in clusters:

        cluster_id = cluster.get("id")

        if cluster_id is None:

            color = "red"
            label = "None"

        else:

            color = cluster_colors[
                (cluster_id - 1) % len(cluster_colors)
            ]

            label = str(cluster_id)

        ax.scatter(
            cluster["x"],
            cluster["y"],
            s=20,
            c=color
        )

        center_x = cluster["center"]["x"]
        center_y = cluster["center"]["y"]

        if center_x is not None and center_y is not None:

            ax.text(
                center_x,
                center_y,
                label,
                fontsize=10
            )

    ax.set_aspect("equal")

    ax.set_xlim(
        -x_limit,
        x_limit
    )

    ax.set_ylim(
        -y_limit,
        y_limit
    )

    ax.grid(True)
