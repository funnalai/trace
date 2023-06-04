import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from sklearn.cluster import DBSCAN
from sklearn.manifold import TSNE
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from langchain.llms import OpenAI
from langchain import PromptTemplate
import numpy as np
import io
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import chart_studio.plotly as py
from datetime import datetime
import os


def get_natural_convs_title(summaries):
    """
    Create few-word, topic-based summarization of a list of conversation summaries
    """
    llm = OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"),
                 temperature=0)
    docs = [Document(page_content=text) for text in summaries]
    prompt = """
    Write a title for the following summaries of conversations
    "{text}"
    TITLE:
    """
    prompt_template = PromptTemplate(template=prompt, input_variables=["text"])

    summarize_chain = load_summarize_chain(
        llm, chain_type="map_reduce")
    title = summarize_chain({"input_documents": docs},
                            return_only_outputs=True)
    print("look here: ", title)
    return title["output_text"]


def vis_convos(data, name):
    # Load the data from the JSON object
    # create a numpy array that is a list of all the embeddings
    embeddings = np.array([conv['embedding'] for conv in data])
    summaries = [conv['summary'] for conv in data]

    # Reduce the dimensionality of the vectors
    vectors_2d = TSNE(n_components=2, perplexity=min(
        len(data) - 2, 30)).fit_transform(embeddings)
    # Apply DBSCAN clustering
    db = DBSCAN(eps=0.5, min_samples=5).fit(vectors_2d)

    labels = db.labels_
    # Find the unique labels (cluster IDs).
    unique_labels = set(labels)
    titles = []

    # For each label...
    for label in unique_labels:
        # Get the indices of the points that belong to the current cluster.
        indices = [i for i, x in enumerate(labels) if x == label]
        # Get the summaries corresponding to these indices.
        cluster_summaries = [summaries[i] for i in indices]
        # Now, you have a list of all summaries associated with the current cluster.
        # Feed this list to your title-creating tool.
        # This is an example. Replace the following line with your actual tool.
        # TODO: fix natural convs_title
        title = get_natural_convs_title(cluster_summaries)
        titles.append(title)

    # Create scatter trace
    scatter = go.Scatter(
        x=[v[0] for v in vectors_2d],
        y=[v[1] for v in vectors_2d],
        mode="markers",
        marker=dict(color=labels, colorscale="Viridis"),
    )

    # Create figure
    fig = go.Figure(data=[scatter])
    # Hide axis
    fig.update_layout(showlegend=False, xaxis=dict(
        visible=False), yaxis=dict(visible=False))
    # Get the centroid of each cluster and annotate
    centroids = [np.mean([vectors_2d[i] for i in range(
        len(vectors_2d)) if labels[i] == label], axis=0) for label in unique_labels]

    for centroid, title in zip(centroids, titles):
        fig.add_annotation(
            x=centroid[0], y=centroid[1], text=title, showarrow=False)

    # Set title
    fig.update_layout(title=f"""Cluster of {name}’s conversations""")

    # Save the Plotly visualization as an HTML file
    output_file = "plotly_clusters_visualization.html"
    fig.write_html(output_file)
    # read contents of html file and return it as string
    with open(output_file) as f:
        html_string = f.read()
        return html_string


def view_time_conversations(conversations, name):
    # Sort conversations based on start time
    sorted_conversations = sorted(
        conversations, key=lambda conv: conv["startTime"])

    # Create a Plotly subplot
    fig = make_subplots(
        rows=1, cols=1,
        shared_yaxes=True,
        subplot_titles=[f"What {name} has been talking about"]
    )

    # Dictionary to track y-values for each projectId
    project_y_values = {}

    # Plot each conversation as a horizontal line
    for conv in sorted_conversations:
        start_time = datetime.strptime(
            conv["startTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
        end_time = datetime.strptime(conv["endTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
        project_id = conv["projectId"]
        summary = conv["summary"]

        if project_id not in project_y_values:
            # Assign a new y-value for the projectId
            y = len(project_y_values) + 1
            project_y_values[project_id] = y
        else:
            # Reuse the existing y-value for the projectId
            y = project_y_values[project_id]

        fig.add_trace(go.Scatter(
            x=[start_time, end_time],
            y=[y, y],
            mode="lines+markers",
            marker=dict(symbol="circle", size=10),
            name=summary
        ))

    # Set y-axis labels using project IDs
    y_ticks = list(range(1, len(project_y_values) + 1))
    y_labels = [str(project_id) for project_id in project_y_values.keys()]
    fig.update_yaxes(ticktext=y_labels, tickvals=y_ticks, title="Project ID")

    # Format x-axis labels
    fig.update_xaxes(
        tickformat="%A, %d %B %Y %H:%M",  # Example: Monday, 30 May 2023 10:00
        tickangle=45
    )

    # Adjust figure layout
    fig.update_layout(
        height=600,
        margin=dict(l=40, r=40, t=40, b=40),
        paper_bgcolor="white"
    )

    # Save the Plotly visualization as an HTML file
    output_file = "plotly_time_visualization.html"
    fig.write_html(output_file)
    # read contents of html file and return it as string
    with open(output_file) as f:
        html_string = f.read()
        return html_string
