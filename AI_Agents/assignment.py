import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from pydantic import BaseModel
from utils import get_openai_api_key, get_serper_api_key, clean_markdown
import yaml
import os
os.environ["CREWAI_TESTING"] = "true"

import unittests
import dill

# set up the OpenAI model
os.environ["MODEL"] = "gpt-4o-mini"

# set up the OpenAI API key 
os.environ["OPENAI_API_KEY"] = get_openai_api_key()

# set the Serper API key for the WebsiteSearchTool
os.environ["SERPER_API_KEY"] = get_serper_api_key()

CONFIG_DIR = Path(__file__).resolve().parent / "config"

# Define file paths for YAML configurations
files = {
    'agents': CONFIG_DIR / 'agents.yaml',
    'tasks': CONFIG_DIR / 'tasks.yaml'
}

# Load configurations from YAML files
configs = {}
for config_type, file_path in files.items():
    with open(file_path, 'r') as file:
        configs[config_type] = yaml.safe_load(file)

# Assign loaded configurations to specific variables
agents_config = configs['agents']
tasks_config = configs['tasks']

# Create the tool instances for the security engineer agent
serper_kwargs = {"search_url": "https://owasp.org"}
if os.getenv("DLAI_SERPER_BASE_URL"):
    serper_kwargs["base_url"] = os.getenv("DLAI_SERPER_BASE_URL")

serper_search_tool = SerperDevTool(**serper_kwargs)
scrape_website_tool = ScrapeWebsiteTool()


# create the Senior Developer agent
senior_developer = Agent( 
    # load role, goal, and backstory from the YAML configuration
    config=agents_config['senior_developer'],
    # set verbose
    verbose=True 
)

# create the Security Engineer agent
security_engineer = Agent( 
    # load role, goal, and backstory from the YAML configuration
    config=agents_config['security_engineer'],
    # add the website search tools (you need to unpack the list)
    tools=[serper_search_tool, scrape_website_tool],
    # set verbose 
    verbose=True,
)

# create the Tech Lead agent
tech_lead = Agent(
    # load role, goal, and backstory from the YAML configuration
    config=agents_config['tech_lead'],
    # set verbose
    verbose=True
)

# GRADED CELL: Exercise 1

def security_review_output_guardrail(output):
    
    # get the (JSON) output from the TaskOutput object
    try: 
        if isinstance(output, dict):
            json_output = output
        elif hasattr(output, 'json_dict') and output.json_dict is not None:
            json_output = output.json_dict
        elif hasattr(output, 'pydantic') and output.pydantic is not None:
            json_output = output.pydantic.model_dump()
        elif hasattr(output, 'raw') and output.raw:
            import json, re
            raw_str = output.raw.strip()
            raw_str = re.sub(r"^```(?:json)?\s*", "", raw_str)
            raw_str = re.sub(r"\s*```$", "", raw_str)
            json_output = json.loads(raw_str)
        else:
            json_output = None
    except Exception as e:
        return (False, ("Error retrieving the `json_dict` argument: "
                        f"\n{str(e)}\n"
                        "Make sure you set the output_json parameter in the Task."
                        )
                )

    if not isinstance(json_output, dict):
        return (False, "Output could not be parsed as a valid JSON dictionary. Make sure you set the output_json parameter in the Task.")

    # define risk levels
    valid_risk_levels = ['low', 'medium', 'high']
    
    # Check if security_vulnerabilities key exists
    if 'security_vulnerabilities' not in json_output:
        return (False, f"Missing 'security_vulnerabilities' key in output. Got keys: {list(json_output.keys())}")
    
    # validate that each of the risk levels has a valid value
    for vuln in json_output['security_vulnerabilities']:
        # validate the risk level
        if vuln['risk_level'].lower() not in valid_risk_levels: 
            error_message = f"Invalid risk level: {vuln['risk_level']}"
            return (False, error_message) 
    
    ### START CODE HERE ###
    # validate that the highest risk level matches the highest risk level in the vulnerabilities

    # if the highest risk level is not valid risk level, return an error message
    if json_output.get("highest_risk", "").lower() not in valid_risk_levels:
        error_message = f"Invalid highest risk level: {json_output.get('highest_risk')}"
        return (False, error_message)
    
    # if it is one of the valid risk levels, then check if it matches the highest 
    # risk level in the vulnerabilities
    else:
        # get all risk_level values
        risk_levels = [vuln['risk_level'].lower() for vuln in json_output['security_vulnerabilities']] 
        
        # if "high" in risk levels, then highest risk level should be high
        if "high" in risk_levels: 
            if json_output["highest_risk"].lower() != "high":
                error_message = "Highest risk level does not match the highest risk level in the vulnerabilities." 
                return (False, error_message)
            
        # if high and medium are not present and medium is in risk levels, then highest risk level should be medium
        elif "medium" in risk_levels: 
            if json_output["highest_risk"].lower() != "medium":
                error_message = "Highest risk level does not match the highest risk level in the vulnerabilities." 
                return (False, error_message)
            
        # if high and medium are not present, then lowest risk level should be low
        elif "low" in risk_levels: 
            if json_output["highest_risk"].lower() != "low":
                error_message = "Highest risk level does not match the highest risk level in the vulnerabilities." 
                return (False, error_message)
    
    ### END CODE HERE ###

    return (True, json_output)

# create the output json for testing
invalid_json = {"highest_risk": "medium", 
                        "security_vulnerabilities": [{"risk_level": "high"}, 
                                                     {"risk_level": "medium"}]}
# test the guardrail
security_review_output_guardrail(invalid_json)

# test the guardrail
unittests.test_security_review_output_guardrail(security_review_output_guardrail)

# GRADED CELL: Exercise 2

def review_decision_guardrail(output):
    # get the raw output from the TaskOutput object
    try:
        raw_text = output if isinstance(output, str) else getattr(output, 'raw', '') or str(output)
    except Exception as e:
        return (False, ("Error retrieving the `raw` argument: "
                        f"\n{str(e)}\n"
                        "Make sure you set the raw parameter in the Task."
                        )
                )

    # define the keywords to check for in the output
    keywords = ["approve", "request changes", "escalate"]
    
    ### START CODE HERE ###

    # check if any of the keywords are present in the output
    if not any(keyword in raw_text.lower() for keyword in keywords):
        # write a suitable message to the console
        error_message = "Output does not include one of the valid actionable decisions."
        return (False, error_message)

    # if all checks pass, return True, and the output
    return (True, raw_text)

    ### END CODE HERE ###

# create the raw output for testing
input = 'Final decision: Elevate to human'

# test the guardrail
review_decision_guardrail(input)

# test the guardrail
unittests.test_review_decision_guardrail(review_decision_guardrail)

# GRADED CELL: Exercise 3

# Define the pydantic model for the code quality analysis output
class CodeQualityJSON(BaseModel):
    critical_issues: list[str]
    minor_issues: list[str]
    reasoning: str

### START CODE HERE ###

# Create the quality analysis task
analyze_code_quality = Task(
    # Load the expected output, and name from the YAML configuration
    config=tasks_config['analyze_code_quality'], 
    # Define the output type as a pydantic model
    output_json=CodeQualityJSON,
    # Define the agent that will perform this task
    agent=senior_developer, 
)

### END CODE HERE ###

# test the analyze_code_quality task
unittests.test_analyze_code_quality(analyze_code_quality)

# GRADED CELL: Exercise 4

### START CODE HERE ###

# Define the pydantic model for the security vulnerabilities
class SecurityVulnerability(BaseModel):
    description:str
    risk_level:str
    evidence:str

# Define the pydantic model for the security review output
class ReviewSecurityJSON(BaseModel):
    security_vulnerabilities: list[SecurityVulnerability] 
    blocking:bool
    highest_risk:str
    security_recommendations:list[str]

# Create the security review task
review_security = Task(
    # Load the expected output, agent, and name from the YAML configuration
    config=tasks_config['review_security'], 
    # Define the output type as a pydantic model
    output_json=ReviewSecurityJSON,
    # Add the security_review_output_guardrail guardrail
    guardrails=[security_review_output_guardrail],
    # Define the agent that will perform this task
    agent=security_engineer 
)

### END CODE HERE ###

# test the review_security task
unittests.test_review_security(review_security, SecurityVulnerability, ReviewSecurityJSON)

# GRADED CELL: Exercise 5

### START CODE HERE ###

# Create the review decision task
make_review_decision = Task(
    # Load the expected output, agent, and name from the YAML configuration
    config=tasks_config['make_review_decision'], 
    # Set the Markdown parameter to get the final report in Markdown format
    markdown=True,
    # Add the review_decision_guardrail guardrail
    guardrails=[review_decision_guardrail],
    # Set the context with the previous task objects
    context=[analyze_code_quality, review_security], 
    # Define the agent that will perform this task
    agent=tech_lead 
)

### END CODE HERE ###

# test the make_review_decision task
unittests.test_make_review_decision(make_review_decision)

# GRADED CELL: Exercise 6

# Define the execution hook to read the PR file
def read_file_hook(inputs):
    
    ### START CODE HERE ###
    
    # get the file_path from the inputs
    filename = inputs.get("file_path")
    
    ### END CODE HERE ###

    # if the filename is not provided, raise an error
    if not filename:
        raise ValueError("Missing 'file_path' in inputs")

    # try reading the file
    try:
        path = Path(filename)
        if not path.is_absolute() and not path.exists():
            candidate = Path(__file__).resolve().parent / filename
            if candidate.exists():
                path = candidate
        with open(path, "r") as f:
            file_contents = f.read()
    # if there are any issues, raise an error
    except Exception as e:
        raise RuntimeError(f"Failed to read file {filename}: {e}")

    
    ### START CODE HERE ###

    # add the file contents to the inputs
    inputs["file_content"] = file_contents
    
    # return the modified inputs
    return inputs

    ### END CODE HERE ###

# test the read_file_hook
unittests.test_read_file_hook(read_file_hook)

# GRADED CELL: Exercise 7

### START CODE HERE ###

# Create the code review crew
crew = Crew(
    # add the list of agents
    agents=[senior_developer, security_engineer, tech_lead],
    # add the list of tasks (in order of execution) 
    tasks=[analyze_code_quality, review_security, make_review_decision],
    # add memory to the crew
    memory=True,
    # add the before-kickoff hook to read the PR file
    # you need to pass a list with the hook function from Ex 8
    before_kickoff_callbacks= [read_file_hook]
)

### END CODE HERE ###

# test the crew
unittests.test_crew(crew)

# GRADED CELL: Exercise 8

# define the file path for the PR file
file_path = "files/code_changes.txt" 

### START CODE HERE ###
print(crew)
# kickoff the crew
result = crew.kickoff(
    # add the inputs dictionary with the file path
    inputs={"file_path": file_path}
    )

### END CODE HERE ###

# Save the result to a dill file
with open('result.dill', 'wb') as f:
    dill.dump(result, f)

# clean the markdown output, in case the report is wrapped with code fences
clean_report = clean_markdown(result.raw)

# display the final report as markdown
print(clean_report)