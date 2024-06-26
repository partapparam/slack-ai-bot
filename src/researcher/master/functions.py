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


def scrape_urls(urls, query, cfg=None):
    """
    Scrapes the urls
    Args:
        urls: List of urls
        cfg: Config (optional)

    Returns:
        text: str

    """
    sources = []
    # content = []

    user_agent = (
        cfg.user_agent
        if cfg
        else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
    )
    try:
        scraper = Scraper(urls, query, user_agent, cfg.scraper)
        # unpack the generator
        sources = scraper.run()
    except Exception as e:
        print(f"{Fore.RED}Error in scrape_urls: {e}{Style.RESET_ALL}")
        print(f"Traceback: {traceback.format_exc()}{Style.RESET_ALL}")
    return sources

async def summarize(query, content, agent_role_prompt, cfg, websocket=None):
    """
    Asynchronously summarizes a list of URLs.

    Args:
        query (str): The search query.
        content (list): List of dictionaries with 'url' and 'raw_content'.
        agent_role_prompt (str): The role prompt for the agent.
        cfg (object): Configuration object.

    Returns:
        list: A list of dictionaries with 'url' and 'summary'.
    """

    # Function to handle each summarization task for a chunk
    async def handle_task(url, chunk):
        summary = await summarize_url(query, chunk, agent_role_prompt, cfg)
        if summary:
            await stream_output("logs", f"🌐 Summarizing url: {url}", websocket)
            await stream_output("logs", f"📃 {summary}", websocket)
        return url, summary

    # Function to split raw content into chunks of 10,000 words
    def chunk_content(raw_content, chunk_size=10000):
        words = raw_content.split()
        for i in range(0, len(words), chunk_size):
            yield " ".join(words[i : i + chunk_size])

    # Process each item one by one, but process chunks in parallel
    concatenated_summaries = []
    for item in content:
        url = item["url"]
        raw_content = item["raw_content"]

        # Create tasks for all chunks of the current URL
        chunk_tasks = [handle_task(url, chunk) for chunk in chunk_content(raw_content)]

        # Run chunk tasks concurrently
        chunk_summaries = await asyncio.gather(*chunk_tasks)

        # Aggregate and concatenate summaries for the current URL
        summaries = [summary for _, summary in chunk_summaries if summary]
        concatenated_summary = " ".join(summaries)
        concatenated_summaries.append({"url": url, "summary": concatenated_summary})

    return concatenated_summaries

async def summarize_url(query, raw_data, agent_role_prompt, cfg):
    """
    Summarizes the text
    Args:
        query:
        raw_data:
        agent_role_prompt:
        cfg:

    Returns:
        summary: str

    """
    summary = ""
    try:
        summary = await create_chat_completion(
            model=cfg.fast_llm_model,
            messages=[
                {"role": "system", "content": f"{agent_role_prompt}"},
                {
                    "role": "user",
                    "content": f"{generate_summary_prompt(query, raw_data)}",
                },
            ],
            temperature=0,
            llm_provider=cfg.llm_provider,
        )
    except Exception as e:
        print(f"{Fore.RED}Error in summarize: {e}{Style.RESET_ALL}")

    print(
        f"""
        from summarize_url:
        query: {query}
        raw_data: {raw_data}
        agent_role_prompt: {agent_role_prompt}
        cfg:
        summary: {summary}
        """
    )
    return summary


