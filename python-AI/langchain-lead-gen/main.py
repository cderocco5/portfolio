import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.agents.agent import AgentExecutor
from langchain.agents.react.agent import create_react_agent
from tools import scrape_tool, search_tool, save_tool

load_dotenv()

# Pydantic models
class LeadResponse(BaseModel):
    company: str
    contact_info: str
    email: str
    summary: str
    outreach_message: str
    tools_used: list[str]

class LeadResponseList(BaseModel):
    leads: list[LeadResponse]

# LLM setup
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
)

tools = [scrape_tool, search_tool, save_tool]

# ReAct prompt
prompt = PromptTemplate.from_template("""Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}""")

# Build agent
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=50,
    max_execution_time=300,
    handle_parsing_errors=True,
    return_intermediate_steps=True
)
# Run agent
query = """
Find and qualify exactly 2 local small businesses in New Jersey that might need IT services.
For each: use scrape to find them, search for details, then return a JSON object matching this schema:
{ "leads": [ { "company", "contact_info", "email", "summary", "outreach_message", "tools_used" } ] }
After building the list, use the save tool to store it. Return only valid JSON.
"""

result = agent_executor.invoke({"input": query})
raw_response = result["output"]



if "Agent stopped" in raw_response or not raw_response.strip():
    print("\n--- INTERMEDIATE STEPS ---")
    for step in result.get("intermediate_steps", []):
        print(step)
else:
    try:
        parsed_data = LeadResponseList.model_validate(json.loads(raw_response))
        print(parsed_data)
    except Exception as e:
        print("Could not parse structured response. Raw output:", raw_response)
        print("Error:", e)

