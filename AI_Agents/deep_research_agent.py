# Add project root to sys.path so utils can be imported
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from crewai import Agent, Task, Crew
from crewai_tools import EXASearchTool, ScrapeWebsiteTool
import os
os.environ["CREWAI_TESTING"] = "true"
from utils import get_openai_api_key, get_exa_api_key
import yaml

# set the OpenAI model (gpt-4o-mini)
os.environ["MODEL"] = "gpt-4o-mini"
# set up the OpenAI API key 
os.environ["OPENAI_API_KEY"] = get_openai_api_key()
# set the EXA API key
os.environ["EXA_API_KEY"] = get_exa_api_key()

# create the tool instances
exa_search_tool = EXASearchTool(base_url=os.getenv("EXA_BASE_URL")) 
scrape_website_tool = ScrapeWebsiteTool()

CONFIG_DIR = Path(__file__).resolve().parent / "config"

# load the configuration file for the agents
with open(CONFIG_DIR / 'agents.yaml', 'r') as file:
        agent_config = yaml.safe_load(file)

print(agent_config)

# create the agents using the configuration
research_planner = Agent(
        config=agent_config['research_planner'],
        verbose=True,
        max_rpm=150,
        max_iter=15
        )
internet_researcher = Agent(
        config=agent_config['internet_researcher'],
        tools=[exa_search_tool, scrape_website_tool],
        verbose=True,
        max_rpm=150,
        max_iter=15
        )
fact_checker = Agent(
        config=agent_config['fact_checker'],
        tools=[exa_search_tool, scrape_website_tool],
        verbose=True,
        max_rpm=150,
        max_iter=15
        )
report_writer = Agent(
        config=agent_config['report_writer'],
        verbose=True,
        max_rpm=150,
        max_iter=15
        )

import re

# write the custom guardrail function
def write_report_guardrail(output):
    # get the raw output from the TaskOutput object
    try:
        output = output if type(output)==str else output.raw 
    except Exception as e:
        return (False, ("Error retrieving the `raw` argument: "
                        f"\n{str(e)}\n"
                        )
                )
    
    # convert the output to lowercase
    output_lower = output.lower()

    # check that the summary section exists
    if not re.search(r'#+.*summary', output_lower):
        return (False, 
                "The report must include a Summary section with a header like '## Summary'"
                )

    # check that the insights or recommendations sections exist
    if not re.search(r'#+.*insights|#+.*recommendations', output_lower):
        return (False, 
                "The report must include an Insights section with a header like '## Insights'"
                )

    ### START CODE HERE ###

    # check that the citations (or references) section exists
    if not re.search(r'#+.*citations|#+.*references', output_lower):
        return (False,
                "The report must include a Citations (or References) section with a header like '## Citations'"
                )

    ### END CODE HERE ###
    return (True, output)

test_report_pass = """
# Report title

## Executive Summary
This is a summary.

## Insights
These are the insights.

## Citations
1. Citation 1
2. Citation 2
"""

result = write_report_guardrail(test_report_pass)
print(result)

test_report_fail = """
# Report title

## Executive Summary
This is a summary.
"""

result_fail = write_report_guardrail(test_report_fail)
print(result_fail)

# load the configuration file for the tasks
with open(CONFIG_DIR / 'tasks.yaml', 'r') as file:
    task_config = yaml.safe_load(file)

### START CODE HERE ###

# create the tasks using the configuration
create_research_plan = Task(
    config=task_config['create_research_plan'],
    agent=research_planner
)

gather_research_data = Task(
    config=task_config['gather_research_data'],
    agent=internet_researcher,
)

verify_information_quality = Task(
    config=task_config['verify_information_quality'],
    agent=fact_checker,
)

write_final_report = Task(
    config=task_config['write_final_report'],
    agent=report_writer,
    guardrails=[write_report_guardrail],
)

### END CODE HERE ###

def save_file_hook(result):
    """
    Save the final research report to a local markdown file
    """
    try:
        # Get the final report content from the last task output
        if hasattr(result, 'tasks_output') and result.tasks_output:
            report_content = result.tasks_output[-1].raw
        else:
            report_content = str(result)
        
        filename = f"research_report.md"
        
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"Report successfully saved to: {filename}")
        
    except Exception as e:
        print(f"Error saving report to file: {str(e)}")

# Create the urban planning crew
deep_research_crew = Crew(
    # include all the agents
    agents=[research_planner, 
            internet_researcher, 
            fact_checker, 
            report_writer],
    # include all the tasks in the order to be executed
    tasks=[create_research_plan, 
           gather_research_data, 
           verify_information_quality, 
           write_final_report],

    ### START CODE HERE ###
    
    # add memory to the crew
    memory=True,
    # add the after kickoff hook
    after_kickoff_callbacks=[save_file_hook]

    ### END CODE HERE ###
)

### START CODE HERE ###

# write your query in the "user_query" value
inputs = {
    "user_query": "Evaluate the top five emerging AI tools for automating competitive market analysis, including their features, limitations, costs, and ideal use cases for a mid-sized marketing firm."
}

### END CODE HERE ###

# Execute the crew's tasks
result = deep_research_crew.kickoff(inputs=inputs)
print(result)