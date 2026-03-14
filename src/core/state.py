from typing import Annotated, TypedDict, List, Dict, Any, Optional
from langchain_core.messages import AnyMessage   
from langgraph.graph.message import add_messages

class DeLabsState(TypedDict):
    #core conversational messages
    messages : Annotated[List[AnyMessage], add_messages]

    #Research content of Scientist
    research_content : str
    paper_references : List[str] 

    #Content of the Archeitect
    archeiture_draft : str
    hyperparameters : Dict[str, Any]

    #ML Engineer & SysOps
    code_filepaths : Dict[str, Any]
    hardware_telementry : Dict[str,str]

    #Telemetery n QA Agent
    training_metrics : Dict[str, Any]
    error_logs : List[str]

    #Human in the loop
    human_feedback : Optional[str]
    requires_approval : bool