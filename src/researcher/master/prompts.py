
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
