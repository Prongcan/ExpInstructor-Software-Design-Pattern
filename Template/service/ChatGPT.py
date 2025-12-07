from openai import OpenAI
import os


def _get_client():
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_APIKEY")
    # Fall back to the original hard-coded value (not recommended, kept for compatibility)
    if not api_key:
        api_key = "YOUR_OPENAI_API_KEY"
    return OpenAI(api_key=api_key)


def chat(prompt, pdf_url, model: str = "gpt-4o"):
    client = _get_client()
    # 标准 OpenAI API：使用 chat.completions.create
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": pdf_url},
                    },
                ],
            }
        ],
    )
    return response.choices[0].message.content


def chat_simple(prompt: str, model: str = "gpt-4o") -> str:
    client = _get_client()
    # 标准 OpenAI API：使用 chat.completions.create
    response = client.chat.completions.create(
        model=model,
        temperature=0.1,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def embed_texts(texts: list[str], model: str = "text-embedding-3-small") -> list[list[float]]:
    """Batch text embeddings. Returns an embedding list matching the input order."""
    client = _get_client()
    # OpenAI embeddings API expects list of inputs
    resp = client.embeddings.create(model=model, input=texts)
    # resp.data[i].embedding -> list[float]
    return [item.embedding for item in resp.data]