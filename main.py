import pandas as pd
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType
from utilities.prompt import AGENT_SYSTEM_PROMPT
import os
from dotenv import load_dotenv

load_dotenv()

EXCEL_FILE = "C:/Users/227457/Downloads/RLB Data Dictionary Temp.xlsx"
df = pd.read_excel(EXCEL_FILE)

def smart_lookup_metric_details(metric_query):
    # 1. Try exact (case-insensitive) match first
    exact_match = df[df['Metrics'].str.lower() == metric_query.strip().lower()]
    if not exact_match.empty:
        row = exact_match.iloc[0]
        # Show all columns, including new ones like Report and Tab if present
        details = []
        for col in df.columns:
            if pd.notna(row[col]) and str(row[col]).strip() != "":
                details.append(f"**{col}:** {row[col]}")
        return "\n".join(details)

    # 2. If no exact match, try partial/fuzzy match (general, not hard-coded)
    query_words = [word.strip().lower() for word in metric_query.replace("&", " ").replace("/", " ").split() if len(word.strip()) > 2]
    match_mask = df['Metrics'].str.lower().apply(
        lambda metric: any(qw in metric for qw in query_words) if isinstance(metric, str) else False
    )
    matches = df[match_mask]

    if matches.empty:
        # No match at all
        return f"No relevant metrics found for '{metric_query}'. Try more general keywords or check the metric list."
    elif len(matches) == 1:
        row = matches.iloc[0]
        details = []
        for col in df.columns:
            if pd.notna(row[col]) and str(row[col]).strip() != "":
                details.append(f"**{col}:** {row[col]}")
        return "\n".join(details)
    else:
        # Multiple matches, list and prompt user
        options = ", ".join(matches['Metrics'].tolist())
        response = (
            f"I found multiple relevant metrics for your query '{metric_query}':\n"
            f"{options}\n"
            "Please specify which metric you'd like details about, or ask for more than one!"
        )
        return response

lookup_tool = Tool(
    name="MetricLookup",
    func=smart_lookup_metric_details,
    description="Find and explain any metric by name or topic. Input: metric name, part of a metric, or general topic."
)

llm = ChatOpenAI(model="gpt-4o", temperature=0)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = initialize_agent(
    tools=[lookup_tool],
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=False,
    handle_parsing_errors=True,
    memory=memory,
    system_message=AGENT_SYSTEM_PROMPT  # Use your imported prompt!
)
