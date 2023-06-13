# trace.ai

Tld;r trace is a tool that helps managers be more productive by providing more information about what their employees are actually doing and working on throughout the week. Trace provides more visibility on reporting and accounting for employees time so managers waste less time collecting, sorting, and finding information about their employees (what they worked on, where they're blocked, who they're interfacing with) and more time doing what they do best.

### Tl;dr what does it actually do?
Trace hooks up and triangulates data from external data sources (starting with Slack) onto your ticketing platform (starting with Linear) so that instead of information about tickets and all your Slack thread/discussions living in separate domains (with no tie in between them), they're connected, allowing us to produce graphs, summaries, and query with natural language the most up-to-date information on what employees are working on. In short, we take all of the information about what is being worked on in Slack by your team and employees, summarize/index it, then map it onto your Linear tickets so that we can help save time reporting the most up-to-date information on what your employees worked on throughout the week (see Demo for what this concretely looks like)

### Thesis

Ticketing platforms like [Linear](https://linear.app/) and [Jira](https://www.atlassian.com/software/jira) do not provide the full picture on what employees work on. Most companies do not keep their ticketing platforms up to date and most importantly, most if not all of the discussion around tickets is happening in other platforms and tools like Slack, Zoom, Google Calendar etc. This makes it difficult for managers to quickly figure out the most up-to-info about what they're employees are working on, which is cruical to be able to help them. Trace helps save managers' time by triangulating information around discussions happening in Slack onto Linear and providing that information in different views to allow them to get a more granular, up-to-date, and informative picture on what they're employees are working on.

### Demo
1. Managers navigate to the home page where they will be greeted with a list of their employees, they can click on one to get more information
<img width="1507" alt="Screenshot 2023-06-12 at 11 08 09 PM" src="https://github.com/funnalai/trace/assets/7995105/c54aca0a-cba0-4447-be6d-d1577da15bf3">

2. An employee's dashboard currently consists of two graphs and a natural language query engine. 

#### Graph 1: Cluster of Slack Discussions
The first graph clusters and summarizes all of the employee's discussions occurring in Slack. You can see the clusters here are segmented by projects in the team's linear work space, so the manager can quickly get a sense on where Will spent most of his time this week.
<img width="1509" alt="Screenshot 2023-06-12 at 11 08 33 PM" src="https://github.com/funnalai/trace/assets/7995105/e9c654e0-4b12-457f-baf8-cfa30b89152a">

Hovering over one of the dots will provide a summary of this particular discussion thread that the manager can quickly read to get a picture of this particular discussion. In our indexing pipeline, we treat one of these discussions or `ProcessedMessages` as a collection of messages around a particular topic. Concretely, this means one data point is a summary of all of the messages in one particular thread. For initial simplification, we **assume that all messages around a particular topic occur in the thread**. So messages sent 
<img width="1508" alt="Screenshot 2023-06-12 at 11 09 02 PM" src="https://github.com/funnalai/trace/assets/7995105/280a97e7-f9a4-4146-8f44-8ee638854b76">

For context, this is what our Slack setup looks like. Obviously, this is much cleaner that most Slack usage but we thought we would start there first for simplicity.
<img width="1223" alt="Screenshot 2023-06-12 at 11 46 22 PM" src="https://github.com/funnalai/trace/assets/7995105/b740108f-d2c1-48ac-abed-4837c975d742">

In addition to providing the summary, every circle or datapoint, when clicked on will navigate directly to the associated Slack thread for this particular discussion. This allows managers to quickly get more information about a particular discussion thread if they would like to.


#### Graph 2: Time View of Discussions by Projects
The second graph Managers have access to is a time-view of when and what disucssions their employee worked on for the week. The Y-axis displays all of our projects according to our Linear workspace (which for simplicity since we used synthetic data are very high-level) and the x-axis display time. Every dot is as before one particular thread of discussion (called a `trace`). Managers can hover over one of the traces to see the summary as before and click on it to directly link to the Slack thread.
<img width="1461" alt="Screenshot 2023-06-12 at 11 08 42 PM" src="https://github.com/funnalai/trace/assets/7995105/0ee788f3-9ee4-414e-a6fc-d965c41f0549">

#### Natural Language Engine
The final affordance to Managers is this chatbot view that allows them to quickly query specific questions about all of the employee's data. 
For any question, Trace will attempt to answer it using the data as well as provide what it thinks is the most relevant discussion thread in Slack that a manager can quickly navigate to in order to get more information. Here's an example of it in action.
<img width="1510" alt="Screenshot 2023-06-12 at 11 09 42 PM" src="https://github.com/funnalai/trace/assets/7995105/06c81e78-8798-4dd4-bd45-5efbb5a067d6">
<img width="1501" alt="Screenshot 2023-06-12 at 11 09 55 PM" src="https://github.com/funnalai/trace/assets/7995105/a042065c-b93a-4472-b53e-56d6d7fadedb">
<img width="1505" alt="Screenshot 2023-06-12 at 11 10 08 PM" src="https://github.com/funnalai/trace/assets/7995105/904a9164-0d62-42b1-82f6-d907bf335131">


### How can I use it?

-   `cd server`
-   `poetry shell`
-   if it complains about python, do `which python3` to find path of the executable and do `poetry env use <path/to/executable>`
-   `poetry install` to install the dependencies
-   `make sever`
