import warnings
warnings.filterwarnings('ignore')

from crewai import Task, Agent, Crew
import os
os.environ["CREWAI_TESTING"] = "true"
from utils import get_openai_api_key

os.environ["OPENAI_API_KEY"] = get_openai_api_key() 