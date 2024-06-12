from researcher.master.prompts import *

import asyncio
import json
import traceback


async def get_sub_query(
    queries: list[str], parent_query: str, agent_role_prompt: str, cfg
):
    """
    Gets a single sub query given:
    - a list of queries: parent query and any other queries previously appended
    - an agent role prompt
    - a config
    Args:
        queries: list of queries
        agent_role_prompt: agent role prompt
        cfg: Config

    Returns:
        sub_query: str
    """
    prompt = generate_sub_query_prompt(queries, parent_query, agent_role_prompt)

    response = await create_chat_completion(
        model=cfg.smart_llm_model,
        messages=[
            {"role": "system", "content": f"{agent_role_prompt}"},
            {"role": "user", "content": f"task: {prompt}"},
        ],
        temperature=0,
        llm_provider=cfg.llm_provider,
    )
    return response


async def get_sub_queries(
    query: str,
    agent_role_prompt: str,
    cfg,
    parent_query: str,
    report_type: str,
):
    """
    Gets the sub queries
    Args:
        query: original query
        agent_role_prompt: agent role prompt
        cfg: Config

    Returns:
        sub_queries: List of sub queries

    """

    # assign the original query to the parent query
    parent_query = query

    num_sub_queries = cfg.num_sub_queries if cfg.num_sub_queries else 1

    # add the original query to the list of sub queries
    list_of_sub_queries = []
    list_of_sub_queries.append(query)

    # try to get the sub queries. if it fails, return just the list with the original query
    try:
        # get the sub queries
        for _ in range(num_sub_queries):
            sub_query = await get_sub_query(
                list_of_sub_queries, parent_query, agent_role_prompt, cfg
            )
            print(f"sub_query: '{sub_query}'")
            cleaned_sub_query = normalize_query(sub_query)
            print(f"cleaned_sub_query: '{cleaned_sub_query}'")
            list_of_sub_queries.append(cleaned_sub_query)

    except Exception as e:
        print(f"{Fore.RED}Error in get_sub_queries: {e}{Style.RESET_ALL}")
        print(f"Traceback: {traceback.format_exc()}{Style.RESET_ALL}")
        return list_of_sub_queries

    return list_of_sub_queries


def normalize_query(query: str) -> str:

    try:
        # Remove leading/trailing whitespace
        query = query.strip()

        # Remove extra quotes (single and double)
        query = re.sub(r"['\"]", "", query)

        # Remove any special characters or punctuation
        query = re.sub(r"[^a-zA-Z0-9\s]", "", query)

        # Convert to lowercase
        query = query.lower()

        return query

    except Exception as e:
        print(f"{Fore.RED}Error in normalize_query: {e}{Style.RESET_ALL}")
        print(f"Traceback: {traceback.format_exc()}{Style.RESET_ALL}")
        return query

