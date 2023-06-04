import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from sklearn.cluster import DBSCAN
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI
from langchain import PromptTemplate
import numpy as np
import io
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import chart_studio.plotly as py
from datetime import datetime
import os
import re


def get_natural_convs_title(summaries):
    """
    Create few-word, topic-based summarization of a list of conversation summaries
    """
    llm = OpenAI(temperature=0.7, max_tokens=200)
    text_splitter = CharacterTextSplitter(chunk_size=400, chunk_overlap=20)

    user_text = ' '.join(summaries)[:20000]

    texts = text_splitter.split_text(user_text)
    docs = [Document(page_content=t) for t in texts]

    prompt_template = """
        Output 3 diverse key topics of the following conversations. Don't go more than 3. 
        Conversations:
        "{text}"
        Output format should be [keyword1, keyword2, keyword3].
        
        KEYWORDS:
        """
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])
    chain = load_summarize_chain(llm, chain_type="map_reduce",
                                 return_intermediate_steps=False, map_prompt=PROMPT, combine_prompt=PROMPT)
    summary = chain({"input_documents": docs}, return_only_outputs=True)

    # Return the summary.
    return summary['output_text']


def truncate_text(text, max_length):
    words = text.split()  # Split the text into individual words
    truncated_text = []
    current_chunk = ""

    for word in words:
        if len(current_chunk) + len(word) + 1 <= max_length:
            current_chunk += " " + word  # Add the word to the current chunk
        else:
            # Add the completed chunk to the list
            truncated_text.append(current_chunk.strip())
            current_chunk = word  # Start a new chunk with the current word

    if current_chunk:
        # Add the last chunk to the list if it exists
        truncated_text.append(current_chunk.strip())

    return truncated_text


def get_post_hover_preview(data, truncated_summaries):
    all_hover_previews = []
    for i in range(len(data)):
        truncated_summary = truncated_summaries[i]
        curr_data = data[i]
        print("curr_data: ", curr_data)
        strResult = "<a style='color:white' href='" + curr_data["slackUrl"] + "'" + "><i>Summary:</i><br>" + \
            ("<br>".join(truncated_summary)) + "</a><extra></extra>"
        all_hover_previews.append(strResult)
    return all_hover_previews


def vis_convos(data, name):
    # Load the data from the JSON object
    # create a numpy array that is a list of all the embeddings
    embeddings = np.array([conv['embedding'] for conv in data])
    summaries = [conv['summary'] for conv in data]
    truncated_summaries = [truncate_text(
        summary, 30) for summary in summaries]
    processed_truncated_summaries = get_post_hover_preview(
        data, truncated_summaries)
    print("hello: ", processed_truncated_summaries[0])

    # Reduce the dimensionality of the vectors
    vectors_2d = PCA(n_components=2).fit_transform(embeddings)*10

    # Apply DBSCAN clustering
    db = DBSCAN(eps=0.8, min_samples=10).fit(vectors_2d)

    labels = db.labels_
    # Find the unique labels (cluster IDs).
    unique_labels = set(labels)
    titles = []

    # For each label...
    for label in unique_labels:
        # Get the indices of the points that belong to the current cluster
        indices = [i for i, x in enumerate(labels) if x == label]

        # Get the summaries corresponding to these indices
        cluster_summaries = [summaries[i] for i in indices]

        # Now, you have a list of all summaries associated with the current cluster
        # Feed this list to your title-creating tool
        print(len(' '.join(cluster_summaries)))
        # This is an example. Replace the following line with your actual tool
        title = get_natural_convs_title(cluster_summaries)
        # title = cluster_summaries
        print(title)
        titles.append(title)

    pattern = r"^.+(?=1\.)"
    cleaned_titles = [re.sub(pattern, '', s) for s in titles]

    # Create scatter trace
    scatter = go.Scatter(
        x=[v[0] for v in vectors_2d],
        y=[v[1] for v in vectors_2d],
        mode='markers',
        text=list(map(lambda x: x['slackUrl'], data)),
        marker=dict(
            color=labels,  # assign color based on remapped labels
            colorscale='Viridis',
            size=20,
            # adding a border to the markers can also help differentiate them
            line=dict(width=0.5, color='gray')
        ),
        hovertemplate=processed_truncated_summaries,
        hoverlabel=dict(font=dict(color="white"))
    )

    # Create figure
    fig = go.Figure(data=[scatter])
    # Hide axis
    # Get the centroid of each cluster and create annotations
    centroids = [np.mean([vectors_2d[i] for i in range(
        len(vectors_2d)) if labels[i] == label], axis=0) for label in unique_labels]
    annotations = [dict(x=centroid[0], y=centroid[1], text=title, showarrow=False,
                        font=dict(
                            size=12,  # Specify the font size
                            color='black',  # Specify the font color
                            family='Arial'  # Specify the font family
    ))
        for centroid, title in zip(centroids, cleaned_titles)]

    # Create layout
    layout = go.Layout(
        title=f"Cluster of {name}'s conversations",
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        annotations=annotations,
        hovermode='closest',
    )
    # Set title
    fig = go.Figure(data=[scatter], layout=layout)

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
