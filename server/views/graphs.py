import matplotlib.pyplot as plt
from datetime import datetime


def view_time_conversations(conversations):
    # Sort conversations based on start time
    sorted_conversations = sorted(
        conversations, key=lambda conv: conv["startTime"])

    # Create a figure and axis
    fig, ax = plt.subplots()

    # Dictionary to track y-values for each projectId
    project_y_values = {}

    # Plot each conversation as a horizontal line
    for conv in sorted_conversations:
        start_time = datetime.strptime(
            conv["startTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
        end_time = datetime.strptime(conv["endTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
        project_id = conv["projectId"]

        if project_id not in project_y_values:
            # Assign a new y-value for the projectId
            y = len(project_y_values) + 1
            project_y_values[project_id] = y
        else:
            # Reuse the existing y-value for the projectId
            y = project_y_values[project_id]

        ax.plot([start_time, end_time], [y, y], marker="o")

    # Set y-axis limits
    ax.set_ylim(0.5, len(project_y_values) + 0.5)

    # Set y-axis ticks and labels
    y_ticks = list(range(1, len(project_y_values) + 1))
    # Use projectIds as y-axis labels
    y_labels = [str(project_id) for project_id in project_y_values.keys()]
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)

    # Format x-axis labels
    date_format = "%A, %d %B %Y %H:%M"  # Example: Monday, 30 May 2023 10:00
    x_ticks = ax.get_xticks()
    formatted_dates = [datetime.fromtimestamp(
        ts).strftime(date_format) for ts in x_ticks]
    ax.set_xticklabels(formatted_dates, rotation=45)

    # Set axis labels and title
    ax.set_xlabel("Time")
    ax.set_ylabel("Project ID")  # Change y-axis label to "Project ID"
    ax.set_title("Conversations Over Time")

    plt.tight_layout()
    plt.show()
