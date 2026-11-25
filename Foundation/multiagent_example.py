import sys
from pathlib import Path

# Add project root to sys.path so utils can be imported
sys.path.append(str(Path(__file__).resolve().parent.parent))

from crewai import Agent, Task, Crew
import os
os.environ["CREWAI_TESTING"] = "true"
from utils import get_openai_api_key, get_exa_api_key

# import the tools
from crewai_tools import EXASearchTool, ScrapeWebsiteTool


# Create the EXASearchTool instance
exa_search_tool = EXASearchTool(base_url=get_exa_api_key())
# Create the ScrapeWebsiteTool instance
scrape_website_tool = ScrapeWebsiteTool()


# define the research planner agent
research_planner = Agent(
    role="Research Planner",
    goal="Analyze queries and break them down into smaller, specific research topics.",
    backstory=(
         "You are a research strategist who excels at breaking down complex questions "
         "into manageable research components. You identify what needs to be researched "
         "and create clear research objectives."
    ),
    verbose=True, # set to True to see detailed agent actions
    max_rpm=150,
    max_iter=15
)

researcher = Agent(
    role="Internet Researcher",
    goal="Research thoroughly all assigned topics",
    ### START CODE HERE ###
    backstory=(
        "You are a skilled researcher with experience in online investigation "
        "and data collection. You know how to find reliable sources, extract relevant information, "
        "and always verify facts across multiple sources to avoid misinformation or hallucination. "
        "You never invent facts and always trace information to its origin."
    ),
    # add the 2 tool instances you created
    tools=[exa_search_tool, scrape_website_tool],
    ### END CODE HERE ###
    verbose=True,
    max_rpm=150,
    max_iter=15
)

fact_checker = Agent(
    role="Fact Checker",
    goal=(
        "Verify data for accuracy, identify inconsistencies, "
        "and flag potential misinformation"
    ),
    ### START CODE HERE ###
    backstory=(
        "You are a quality assurance specialist with expertise in fact-checking "
        "and identifying misinformation and hallucinations. You cross-reference information, "
        "spot inconsistencies, and ensure all data meets high accuracy standards. You rigorously"
        "check for hallucinated or invented content and require that all facts be supported"
        "by evidence."
    ),
    tools=[exa_search_tool, scrape_website_tool],
    ### END CODE HERE ###
    verbose=True,
    max_rpm=150,
    max_iter=15
)

report_writer = Agent(
    role="Report Writer",
    goal="Write clear, concise, and well-structured reports based on gathered information",
    ### START CODE HERE ###
    backstory=(
         "You are an expert writer who specializes in creating clear, well-structured "
        "research reports. You synthesize complex information into readable formats and "
        "always include proper citations and sources."
    ),
    ### END CODE HERE ###
    verbose=True,max_rpm=150,
    max_iter=15
)

# define the create research plan task
create_research_plan_task = Task(
    description=(
        "Based on the user's query, break it down into specific topics and key questions, "
        "and create a focused research plan."
        "The user's query is: {user_query}"
    ),
    expected_output=(
        "A research plan with main research topics to investigate, "
        "key questions for each topic, and success criteria for the research."
        ),
    agent=research_planner,
)

# define the gather research data task
gather_research_data_task = Task(
    description=(
        "Using the research plan, collect information on all identified topics. "
        "Cite all sources used."
    ),
    ### START CODE HERE ###
    expected_output=(
        "Comprehensive research data including: information for each "
        "research topic, and citation used along with source credibility notes."         
    ),
    agent=researcher
    ### END CODE HERE ###
)

#define the verify information quality task
verify_information_quality_task = Task(
    description=(
        "Review all collected research. Identify any conflicting information, "
        "potential misinformation, or gaps that need addressing."
    ),
    ### START CODE HERE ###
    expected_output=( 
        "A report with all the original data you got plus any "
        "verified facts vs. questionable information, make sure this is as comprehensive "
        "as possible for final report generation"
    ),
    agent=fact_checker
    ### END CODE HERE ###
)

# define the write final report task
write_final_report_task = Task(
    description=(
        "Create a comprehensive report that answers the original query using all verified research data. "
        "Structure it with clear sections, include citations, and provide actionable insights."
    ),

    expected_output=( 
        "A final research report containing: execution summary,"
        "detailed findings that answer the user's query, supporting evidence and analysis,"
        "complete source citations, and actionable insights."
    ),
    agent=report_writer
)

# create the crew with the defined agents and tasks
crew = Crew(
    ### START CODE HERE ###
    agents=[research_planner, researcher, fact_checker, report_writer],
    tasks=[create_research_plan_task, gather_research_data_task, verify_information_quality_task, write_final_report_task]
    ### 
)

### START CODE HERE ###

# Write your query, which will be used as input for the tasks.
user_query = "Evaluate the top five emerging AI tools for automating competitive market analysis inlcuding their features, limitations, cost, and ideal use cases for mid-sized marketing firm."

### END CODE HERE ###

result = crew.kickoff(
    inputs={
        "user_query": user_query,
    }
)

print(result.raw)