def generate_sub_query_prompt(
    queries: list[str],
    parent_query: str,
    agent_role_prompt: str,
):
    return f"""
        your role: {agent_role_prompt}
        Using the following list of queries: "{queries}", and generate one additional query that can be used to search for information online. \n
        The additional query should be relevant to the main query ({parent_query}) and should be structured in a logical and coherent manner. \n
        The output should be brief and not contain any additional text, explanations, or data structures. \n
        Returns: str: The search query
    """

def create_agent_instructions():
    return """
        This task involves researching a given topic, regardless of its complexity or the availability of a definitive answer. The research is conducted by a specific Agent, defined by its type and role, with each Agent requiring distinct instructions.

        The Agent is determined by the field of the topic and the specific name of the Agent that could be utilized to research the topic provided. Agents are categorized by their area of expertise, and each Agent type is associated with a corresponding emoji.

        examples:
        task: "should I invest in apple stocks?"
        response: 
        {
            "Agent": "💰 Finance Agent",
            "agent_role_prompt: "You are a seasoned finance analyst AI assistant. Your primary goal is to compose comprehensive, astute, impartial, and methodically arranged financial reports based on provided data and trends."
        }
        task: "could reselling sneakers become profitable?"
        response: 
        { 
            "Agent":  "📈 Business Analyst Agent",
            "agent_role_prompt": "You are an experienced AI business analyst assistant. Your main objective is to produce comprehensive, insightful, impartial, and systematically structured business reports based on provided business data, market trends, and strategic analysis."
        }
        task: "what are the most interesting sites in Tel Aviv?"
        response:
        {
            "Agent:  "🌍 Travel Agent",
            "agent_role_prompt": "You are a world-travelled AI tour guide assistant. Your main purpose is to draft engaging, insightful, unbiased, and well-structured travel reports on given locations, including history, attractions, and cultural insights."
        }
    """

def generate_summary_prompt(query, data):
    """Generates the summary prompt for the given question and text.
    Args: question (str): The question to generate the summary prompt for
            text (str): The text to generate the summary prompt for
    Returns: str: The summary prompt for the given question and text
    """

    return (
        f'{data}\n Using the above text, summarize it based on the following task or query: "{query}".\n If the '
        f"query cannot be answered using the text, YOU MUST summarize the text in short.\n Include all factual "
        f"information such as numbers, stats, quotes, etc if available. "
        f"Your goal with your answer is to keep it short, concise, and accurate. Aim to keep it at 3 paragraphs max. No more than 300 words."
    )
