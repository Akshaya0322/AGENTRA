from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_query(self, text: str):
        return self.model.encode(text).tolist()


def get_embedding_model():
    from config.settings import EMBEDDING_MODEL_NAME
    return EmbeddingModel(EMBEDDING_MODEL_NAME)
