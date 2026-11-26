import sys
from pathlib import Path

# Add project root to sys.path so utils can be imported
sys.path.append(str(Path(__file__).resolve().parent.parent))

from crewai import Agent, Task, Crew
import dill
import unittests

import os
os.environ["CREWAI_TESTING"] = "true"
from utils import get_openai_api_key

# set up the OpenAI model to use
os.environ["MODEL"] = 'gpt-4o-mini'

# read and save the policies content
with open('code_changes.txt', 'r') as file:
    code_changes = file.read()
print(code_changes)

# GRADED CELL: Exercise 1
# import the required tools
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
# get the Serper API key
from utils import get_serper_api_key
serper_api_key = get_serper_api_key()

### START CODE HERE ###
# create the instance of the SerperDevTool. Set the search_url to "https://owasp.org"
serper_search_tool = SerperDevTool(search_url="https://owasp.org")

# create the instance of the ScrapeWebsiteTool, which does not need any arguments
scrape_website_tool = ScrapeWebsiteTool()
### END CODE HERE ###

# test the tools
unittests.test_tools(serper_search_tool, scrape_website_tool)

# GRADED CELL: Exercise 2

### START CODE HERE ### 

# Create the senior developer agent
senior_developer = Agent(
    role="Senior Developer",
    goal="Lead the development team and ensure high-quality code.",
    backstory=(
        "You have extensive experience in software development and have led multiple successful projects."
    ),
            
    # set verbose (suggested: True)
    verbose=True,
)

### END CODE HERE ###

# test the senior developer agent
unittests.test_senior_developer_agent(senior_developer)

# GRADED CELL: Exercise 3

### START CODE HERE ###

# Create the security engineer agent
security_engineer = Agent(
    role="Security Engineer",
    goal="Ensure the security of the software systems and protect against vulnerabilities.",
    backstory=( 
        "You have a strong background in cybersecurity and have successfully mitigated numerous security threats."
    ),
            
    # set verbose (suggested: True)
    verbose=True,
    # assign the tools you created in Exercise 1
    tools=[serper_search_tool, scrape_website_tool],
)

### END CODE HERE ###
# test the security engineer agent
unittests.test_security_engineer_agent(security_engineer)

# GRADED CELL: Exercise 4

### START CODE HERE ###

# Create the tech lead agent
tech_lead = Agent(
    role="Tech Lead",
    goal="Oversee the technical direction of the team and ensure successful project delivery.",
    backstory=(
            "You have a proven track record in leading technical teams and delivering complex projects successfully."
        ),
        
    # set verbose (suggested: True)
    verbose=True,
)
### END CODE HERE ###

# test the tech lead agent
unittests.test_tech_lead_agent(tech_lead)

# GRADED CELL: Exercise 5

### START CODE HERE ###

# Create the quality analysis task
analyze_code_quality = Task(
    description=( 
        "Analyze the code changes {code_changes} to ensure it meets quality standards and best practices."
    ),
    
    expected_output=(
        "A detailed report highlighting code quality issues in the provided code changes and suggestions for improvement. report should be JSON formatted with following keys:"
        "critical_issues, minor_issues, reasoning"
    ),
    
    name="Analyze Code Quality", #DO NOT CHANGE THIS NAME
    agent=senior_developer
)

### END CODE HERE ###

# test the quality analysis task
unittests.test_analyze_code_quality_task(analyze_code_quality)

# GRADED CELL: Exercise 6

### START CODE HERE ###

# Create the security review task
review_security = Task(
    description=( 
        "Use the SerperDevTool to find the most relevant security best practices from OWASP"
        "and pass the URLs to the ScrapeWebsiteTool to get detailed information for the code change {code_changes}."
    ),
    
    expected_output=( 
        "A detailed report highlighting security issues and best practices found, with reasoning."
        "Report should be JSON formatted with following keys: security_vulnerabilities, blocking, highest_risk, security_recommendations"
    ),
    
    agent=security_engineer,
    name="Review Security", # DO NOT CHANGE THIS NAME
)

### END CODE HERE ###

# test the security review task
unittests.test_review_security_task(review_security)

# GRADED CELL: Exercise 7

### START CODE HERE ###

# Create the review decision task
make_review_decision = Task(
    description=( 
        "Make a decision based on the results of the code quality analysis and security review tasks for the code changes {code_changes}."
    ),
   
    expected_output=(
        "A final review decision indicating whether the code changes should be approved, rejected, or require further modifications. report should be JSON formatted with following keys: decision, reasoning"
    ), 
    
    agent=tech_lead,
    # add the two previous tasks as context
    context=[analyze_code_quality, review_security], 
    name="Review Decision", #DO NOT CHANGE THIS NAME
)

### END CODE HERE ###

# test the review decision task
unittests.test_make_review_decision_task(make_review_decision)

# GRADED CELL: Exercise 8

### START CODE HERE ###

# Create the code review crew
crew = Crew(
    # add the list of agents
    agents=[senior_developer, security_engineer, tech_lead],
    # add the list of tasks    
    tasks=[analyze_code_quality, review_security, make_review_decision],
)

### END CODE HERE ###

# test the crew
unittests.test_crew(crew)

# define the inputs dictionary for the crew
inputs = {
    "code_changes": code_changes,
}

# GRADED CELL: Exercise 9

### START CODE HERE ###

# kickoff the crew
result = crew.kickoff(inputs=inputs)

### END CODE HERE ###

print("-----------------------------------------") 
print("result.tasks_output for all tasks") 
print(result.tasks_output) 
print("-----------------------------------------") 
print("result.tasks_output for the first task (analyze_code_quality)")
print(result.tasks_output[0].raw) 
print("-----------------------------------------") 
print("result.tasks_output for the second task (review_security)")
print(result.tasks_output[1].raw) 
print("-----------------------------------------") 
print("result.tasks_output for the third task (make_review_decision)")
print(result.tasks_output[2].raw) 


with open("results.dill", "wb") as f:
    dill.dump(result, f)

from utils import get_dict_keys

# check the result of the first task

# Get the raw output
raw_output = result.tasks_output[0].raw

# See if it can be parsed as a dictionary, and get the keys
get_dict_keys(raw_output)

# check the result of the second task

# Get the raw output
raw_output = result.tasks_output[1].raw

# See if it can be parsed as a dictionary, and get the keys
get_dict_keys(raw_output)

# check the result of the third task

# Get the raw output
raw_output = result.tasks_output[2].raw

# See if it can be parsed as a dictionary, and get the keys
get_dict_keys(raw_output)