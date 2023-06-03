import matplotlib.pyplot as plt
from datetime import datetime


# Example conversation data
dummy_conversations = [
    {
        "startTime": "2023-05-30T10:00:00",
        "endTime": "2023-05-30T11:30:00",
        "summary": "Conversation 1"
    },
    {
        "startTime": "2023-05-30T12:00:00",
        "endTime": "2023-05-30T13:00:00",
        "summary": "Conversation 2"
    },
    {
        "startTime": "2023-05-30T14:00:00",
        "endTime": "2023-05-30T15:30:00",
        "summary": "Conversation 3"
    }
]


def view_time_conversations(conversations):
    # Sort conversations based on start time
    sorted_conversations = sorted(
        conversations, key=lambda conv: conv["startTime"])

    # Create a figure and axis
    fig, ax = plt.subplots()

    # Plot each conversation as a horizontal line
    for i, conv in enumerate(sorted_conversations):
        start_time = datetime.fromisoformat(conv["startTime"])
        end_time = datetime.fromisoformat(conv["endTime"])
        y = i + 1  # y-value for each conversation, incrementing by 1
        ax.plot([start_time, end_time], [y, y], marker="o")

    # Set y-axis limits
    ax.set_ylim(0.5, len(sorted_conversations) + 0.5)

    # Set y-axis ticks and labels
    y_ticks = list(range(1, len(sorted_conversations) + 1))
    y_labels = [conv["summary"] for conv in sorted_conversations]
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)

    # Format x-axis labels
    date_format = "%A, %d %B %Y %H:%M"  # Example: Monday, 30 May 2023 10:00
    formatted_dates = [date.strftime(date_format) for date in ax.get_xticks()]
    ax.set_xticklabels(formatted_dates, rotation=45)

    # Set axis labels and title
    ax.set_xlabel("Time")
    ax.set_ylabel("Conversation")
    ax.set_title("Conversations Over Time")

    plt.tight_layout()
    plt.show()
