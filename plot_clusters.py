import matplotlib.pyplot as plt


def plot_clusters(
    ax,
    x,
    y,
    clusters,
    danger,
    x_limit,
    y_limit
):

    ax.clear()
    ax.scatter(x, y, s=2, c="blue")
    cmap = plt.get_cmap("tab20")

    dangerous_ids = {
        d["cluster_id"]
        for d in danger
    }

    for cluster in clusters:
        cluster_id = cluster.get("id")
        if cluster_id in dangerous_ids:
            color = "red"
        elif cluster_id is None:
            color = "black"
        else:
            color = cmap(cluster_id % 20)
        
        label = f"ID: {cluster_id}"
        ax.scatter(cluster["x"], cluster["y"], s=20, c=[color])
        center_x = cluster["center"]["x"]
        center_y = cluster["center"]["y"]

        if center_x is None or center_y is None:
            continue

        ax.scatter(center_x, center_y, s=80, c=[color], marker="x")
        ax.text(center_x, center_y, label, fontsize=10, fontweight="bold", bbox=dict(facecolor="white", alpha=0.8))

        if cluster.get("moves_toward_sensor") is True:

            ax.arrow(center_x, center_y, -0.3 * center_x, -0.3 * center_y, width=0.01, head_width=0.08, head_length=0.12, color="green")

    ax.scatter(0, 0, s=120, c="black", marker="s")

    ax.set_aspect("equal")
    ax.set_xlim(-x_limit, x_limit)
    ax.set_ylim(-y_limit, y_limit)
    ax.grid(True)
