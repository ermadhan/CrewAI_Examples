import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from crewai import Agent, Task, Crew, LLM
from crewai_tools import EXASearchTool, ScrapeWebsiteTool
import os
os.environ["CREWAI_TESTING"] = "true"
from utils import get_openai_api_key, get_exa_api_key
from pathlib import Path
import yaml

# set the OpenAI model (gpt-4o-mini)
os.environ["MODEL"] = "gpt-4o-mini"
# set up the OpenAI API key 
os.environ["OPENAI_API_KEY"] = get_openai_api_key()
# set the exa API key
os.environ["EXA_API_KEY"] = get_exa_api_key()
CONFIG_DIR = Path(__file__).resolve().parent / "config"

# import packages needed for the custom tool
from crewai.tools import BaseTool
from crewai import LLM
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json

# Define the custom tool for creating plots
class CustomPlotTool(BaseTool):
    ### START CODE HERE ###
    name: None="None"
    description: None="None"
    def _run(self, research: None) -> str:
    ### END CODE HERE ###
        try:
            extraction_prompt = f"""
            You are an expert data visualization assistant. Analyze the provided research text and identify meaningful, insightful charts that can be created to visualize quantifiable data supporting the research's key insights and findings. Only suggest charts for data that includes numerical values, measurable trends, comparisons, or categorical distributions that can be effectively plotted.

            Focus on creating visualizations that highlight trends, comparisons, distributions, or relationships that add value to the research. Avoid suggesting charts for purely qualitative or non-quantifiable information.

            For each chart, provide a JSON object with:
              - "chart_type" (string: choose from "line" for trends over time/continuous, "bar" for comparisons, "histogram" for distributions, "scatter" for relationships, "pie" for proportions)
              - "x_axis" (string: variable name for x-axis, e.g., "year", "category")
              - "y_axis" (string: variable name for y-axis, e.g., "value", "count")
              - "color" (string: optional variable for color grouping/hue, or null if not applicable)
              - "Title" (string: descriptive, insightful title that explains what the chart shows)
              - "data" (dictionary: keys matching x_axis, y_axis, and color variables; values as lists of extracted numerical/categorical data from the research)

            Ensure data is accurately extracted and formatted as lists. If a variable has multiple series (e.g., for color), include all in the data dictionary.

            If no quantifiable data suitable for meaningful visualization is present in the research, return an empty array [].

            Text:
            {research}

            Example output (return valid JSON only):
            [
              {{"chart_type": "line", "x_axis": "year", "y_axis": "funding_amount", "color": "sector", "Title": "AI Research Funding Trends by Sector", "data": {{"year": [2020, 2021, 2022], "funding_amount": [2.5, 3.8, 5.2], "sector": ["Healthcare", "Finance", "Tech"]}}}},
              {{"chart_type": "bar", "x_axis": "tool_name", "y_axis": "adoption_rate", "color": null, "Title": "Market Adoption Rates of AI Tools", "data": {{"tool_name": ["ToolA", "ToolB", "ToolC"], "adoption_rate": [45, 67, 23]}}}}
            ]

            Return only the JSON array, no additional text or explanations.
            """
            llm = LLM(model="gpt-4o-mini",)  # Initialize the LLM instance
            llm_response = llm.call([{"role": "user", "content": extraction_prompt}])

            # Clean the response to extract just the JSON part
            llm_response = llm_response.strip()
            if llm_response.startswith('```json'):
                llm_response = llm_response[7:]  # Remove ```json
            if llm_response.endswith('```'):
                llm_response = llm_response[:-3]  # Remove ```
            llm_response = llm_response.strip()

            # --- Step 2: Parse the LLM output ---
            charts_data = json.loads(llm_response)

            if not isinstance(charts_data, list) or len(charts_data) == 0:
                return "No information found in the research to visualize."

            plots_created = []

            # --- Step 3: Create plots for each chart ---
            for i, chart_info in enumerate(charts_data):
                try:
                    # Extract chart configuration
                    chart_type = chart_info.get("chart_type", None).lower()
                    x_axis = chart_info.get("x_axis", "x")
                    y_axis = chart_info.get("y_axis", "y") 
                    title = chart_info.get("Title", f"Chart {i+1}")
                    hue = chart_info.get("color", None)
                    data = chart_info.get("data", {})

                    # Create DataFrame from the data
                    df = pd.DataFrame(data)

                    if df.empty:
                        continue

                    # Create the plot
                    plt.figure(figsize=(10, 6))

                    if chart_type == "line":
                        sns.lineplot(data=df, x=x_axis, y=y_axis, marker="o", hue=hue)
                    elif chart_type in ["bar", "column"]:
                        sns.barplot(data=df, x=x_axis, y=y_axis, hue=hue)
                    elif chart_type == "histogram":
                        plt.hist(df[y_axis], bins=10, alpha=0.7, hue=hue)
                        plt.xlabel(y_axis)
                        plt.ylabel("Frequency")
                    elif chart_type == "scatter":
                        # Default to scatter plot
                        sns.scatterplot(data=df, x=x_axis, y=y_axis, hue=hue)
                    elif chart_type == "pie":
                        # For pie chart, assume y_axis is values, x_axis is labels
                        plt.pie(df[y_axis], labels=df[x_axis], autopct='%1.1f%%', startangle=90)
                        plt.title(title)
                        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

                    plt.title(title)
                    plt.xticks(rotation=45)
                    plt.tight_layout()

                    # --- Step 4: Save the plot ---
                    os.makedirs("plots", exist_ok=True)
                    filename = f"plots/plot_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    plt.savefig(filename, dpi=300, bbox_inches='tight')
                    plt.close()

                    plots_created.append(filename)

                except Exception as e:
                    print(f"Error creating chart {i+1}: {str(e)}")
                    continue

            if plots_created:
                return f"Successfully created {len(plots_created)} plots: {', '.join(plots_created)}"
            else:
                return "No plots could be created from the extracted data."

        except json.JSONDecodeError as e:
            return f"Error parsing LLM response as JSON: {str(e)}"
        except Exception as e:
            return f"Error generating smart plot: {str(e)}"

# create tools instances
exa_search_tool = EXASearchTool(base_url=os.getenv("EXA_BASE_URL"))
scrape_website_tool = ScrapeWebsiteTool()

# load the configuration file for the agents
with open('config/agents.yaml', 'r') as file:
        agent_config = yaml.safe_load(file)


# create the agents using the configuration
research_planner = Agent(
        config=agent_config['research_planner'],
        verbose=True,
        max_rpm=150,
        max_iter=15
        )

internet_researcher = Agent( 
        config=agent_config['internet_researcher'],
        verbose=True,
        tools=[exa_search_tool, scrape_website_tool],
        max_rpm=150,
        max_iter=15
        )

fact_checker = Agent(
        config=agent_config['fact_checker'],
        verbose=True,
        tools=[exa_search_tool, scrape_website_tool],
        max_rpm=150,
        max_iter=15
        )

report_writer = Agent(
        config=agent_config['report_writer'],
        verbose=True,
        ### START CODE HERE ### 
        # add the automatic plot tool
        tools=[CustomPlotTool()],
        ### END CODE HERE ###
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

    # check that the citations (or references) section exists
    if not re.search(r'#+.*citations|#+.*references', output_lower): 
        return (False, 
                "The report must include a Citations (or References) section with a header like '## Citations'"
                )
    return (True, output)

# load the configuration file for the tasks
with open('config/tasks_tools.yaml', 'r') as file:
    task_config = yaml.safe_load(file)


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
        
        filename = f"research_report-p2.md"
        
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
    # add memory to the crew
    memory=True,
    # add the after kickoff hook
    after_kickoff_callbacks=[save_file_hook]
)

### START CODE HERE ###

# write your query in the "user_query" value
inputs = { 
        "user_query": "Evaluate the top five emerging AI tools for automating competitive market analysis, including their features, limitations, costs, and ideal use cases for a mid-sized marketing firm."
}
### END CODE HERE ### 

# Execute the crew's tasks
result = deep_research_crew.kickoff(inputs=inputs)