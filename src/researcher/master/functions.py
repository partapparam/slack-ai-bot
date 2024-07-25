from src.researcher.master.prompts import *
from src.researcher.scraper.scraper import Scraper
from src.researcher.llm.llm import *
import asyncio
import json
import traceback



def get_retriever(retriever):
    """
    Get the search retriever 
    Args:
        retriever: str

    Returns:
        retriever: Retriever

    """
    match retriever:
        case "googleSerp":
            from src.researcher.retrievers import SerperSearch
            retriever = SerperSearch
        case "duckduckgo":
            from src.researcher.retrievers import Duckduckgo
            retriever = Duckduckgo
        case _:
            raise Exception("Retriever not found.")
    return retriever


async def choose_agent(query, cfg):
    """
    Chooses the agent based on query
    Args:
        query: str
        cfg: Config

    Returns:
        agent: Agent name
        agent_role_prompt: Agent role prompt
    """
    try:
        response = await create_chat_completion(
            model=cfg.smart_llm_model,
            messages=[
                {"role": "system", "content": f"{create_agent_instructions()}"},
                {"role": "user", "content": f"task: {query}"},
            ],
            temperature=cfg.temperature,
            llm_provider=cfg.llm_provider,
        )
        agent_dict = json.loads(response)
        return agent_dict["agent"], agent_dict["agent_role_prompt"]
    except Exception as e:
        return (
            "Default Agent",
            "You are an AI critical thinker research assistant. Your sole purpose is to write well written, critically acclaimed, objective and structured reports on given text.",
        )

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
        temperature=cfg.temperature,
        llm_provider=cfg.llm_provider,
    )
    return response


async def get_sub_queries(
    query: str,
    agent_role_prompt: str,
    cfg
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
            # cleaned_sub_query = normalize_query(sub_query)
            # print(f"cleaned_sub_query: '{cleaned_sub_query}'")
            list_of_sub_queries.append(sub_query)

    except Exception as e:
        print(f"LOGS: Error in get_sub_queries: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return list_of_sub_queries

    return list_of_sub_queries


# def normalize_query(query: str) -> str:

#     try:
#         # Remove leading/trailing whitespace
#         query = query.strip()

#         # Remove extra quotes (single and double)
#         query = re.sub(r"['\"]", "", query)

#         # Remove any special characters or punctuation
#         query = re.sub(r"[^a-zA-Z0-9\s]", "", query)

#         # Convert to lowercase
#         query = query.lower()

#         return query

#     except Exception as e:
#         print(f"Error in normalize_query: {e}")
#         print(f"Traceback: {traceback.format_exc()}")
#         return query


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
        print(f"Error in scrape_urls: {e}")
        print(f"Traceback: {traceback.format_exc()}")
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
        # if summary:
        #     await stream_output("logs", f"🌐 Summarizing url: {url}", websocket)
        #     await stream_output("logs", f"📃 {summary}", websocket)
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
        print(f"Error in summarize: {e}")

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

async def generate_report(  
    query,
    context,
    agent_role_prompt,
    report_type,
    cfg,
    main_topic: str = "",
    existing_headers: list = [],
):
    """
    generates the final report
    Args:
        query:
        context:
        agent_role_prompt:
        report_type:
        cfg:
        main_topic:
        existing_headers:

    Returns:
        report:

    """
    generate_prompt = get_prompt_by_report_type(report_type)
    report = ""

    
    content = (
        f"{generate_prompt(query, context, cfg.report_format, cfg.total_words)}"
    )

    try:
        report = await create_chat_completion(
            model=cfg.smart_llm_model,
            messages=[
                {"role": "system", "content": f"{agent_role_prompt}"},
                {"role": "user", "content": content},
            ],
            temperature=0,
            llm_provider=cfg.llm_provider,
            stream=True,
            max_tokens=cfg.smart_token_limit,
        )
    except Exception as e:
        print(f"Error in generate_report: {e}")

    return report


