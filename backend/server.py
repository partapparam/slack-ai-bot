from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Union, List
from gpt_researcher.master.agent import GPTResearcher
from gpt_researcher.master.source import Source
import json
import datetime

app = FastAPI()
