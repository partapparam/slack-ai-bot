from langchain_community.vectorstores import FAISS
import os


class Memory:
    def __init__(self, embedding_provider, **kwargs):

        _embeddings = None
        match embedding_provider:
            case "openai":
                from langchain_openai import OpenAIEmbeddings
                _embeddings = OpenAIEmbeddings()
            case _:
                raise Exception("Embedding provider not found.")

        self._embeddings = _embeddings

    def get_embeddings(self):
        return self._embeddings