from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)


def split_text(text: str):
    if not text:
        return []

    return splitter.split_text(text)