import matplotlib.pyplot as plt


def plot_clusters(
        ax,
        x,
        y,
        clusters,
        danger,
        x_limit,
        y_limit):

    ax.clear()
    ax.scatter(x, y, s=2, c="blue")

    cmap = plt.get_cmap("tab20")

    # store information of all dangerous clusters
    danger_by_id = {
        danger_information["cluster_id"]: danger_information
        for danger_information in danger
    }

    for cluster in clusters:

        cluster_id = cluster.get("id")

        # chec´k wethear the cluster  id matches a dangerous cluster 
        danger_information = danger_by_id.get(cluster_id)

        if danger_information is not None:
            color = "red"
        elif cluster_id is None:
            color = "black"
        else:
            color = cmap(cluster_id % 20)

        # plot clusters
        ax.scatter(
            cluster["x"],
            cluster["y"],
            s=20,
            color=color
        )

        center_x = cluster["center"]["x"]
        center_y = cluster["center"]["y"]

        # Erst prüfen, dann Koordinaten verwenden
        if center_x is None or center_y is None:
            continue

        # mark cluster mean point with x
        ax.scatter(
            center_x,
            center_y,
            s=80,
            color=color,
            marker="x"
        )

        # show id value shifted on the plot
        if cluster_id is not None:

            ax.annotate(
                str(cluster_id),
                xy=(center_x, center_y),
                xytext=(12, 8),
                textcoords="offset points",
                fontsize=10,
                fontweight="bold",
                bbox={
                    "facecolor": "white",
                    "alpha": 0.8,
                    "edgecolor": "none"
                }
            )

        # show the direction of movement
        approaching = cluster.get("approaching")

        arrow_length = 0.5

        if approaching is True:

            # moving toward sensor
            arrow_dy = -arrow_length
            arrow_color = "orange"

        elif approaching is False:

            # moving away
            arrow_dy = arrow_length
            arrow_color = "green"

        else:

            # direction unknown
            arrow_dy = None

        if arrow_dy is not None:

            ax.annotate(
                "",
                xy=(center_x, center_y + arrow_dy),
                xytext=(center_x, center_y),
                arrowprops={
                    "arrowstyle": "->",
                    "color": arrow_color,
                    "linewidth": 2
                }
            )

    # show scenario 
    if len(danger) > 0:

        danger_text_lines = []

        for danger_information in danger:

            danger_cluster_id = danger_information.get("cluster_id")
            scenario = danger_information.get(
                "scenario",
                "unknown"
            )

            danger_text_lines.append(
                f"ID {danger_cluster_id}: {scenario.upper()}"
            )

        danger_text = "\n".join(danger_text_lines)

        ax.text(
            0.02,
            0.98,
            danger_text,
            transform=ax.transAxes,
            horizontalalignment="left",
            verticalalignment="top",
            fontsize=11,
            fontweight="bold",
            color="red",
            bbox={
                "facecolor": "white",
                "alpha": 0.9,
                "edgecolor": "red"
            }
        )

    # Sensorposition
    ax.scatter(
        0,
        0,
        s=120,
        color="black",
        marker="s"
    )

    ax.set_aspect("equal")
    ax.set_xlim(-x_limit, x_limit)
    ax.set_ylim(-y_limit, y_limit)
    ax.grid(True)
