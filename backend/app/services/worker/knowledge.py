import multiprocessing
from asyncio import CancelledError, Queue, get_running_loop
from uuid import UUID, uuid4

from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client.models import PointStruct

from app.core.config import settings
from app.core.constants import KnowledgeStatus
from app.core.logger import logger_error, logger_info
from app.db.qdrant import app_qdrant_client
from app.db.session import AsyncSessionLocal
from app.models.knowledge import Knowledge
from app.services.embedding import EmbeddingService
from app.services.extractor import extract_file_pdf
from app.services.store import StoreService

_knowledge_queue: Queue[UUID] = Queue()


def _marker_worker_process(file_path: str, result_queue):  # type: ignore
    try:
        text = extract_file_pdf(file_path)
        result_queue.put({"status": "success", "data": text})  # type: ignore
    except Exception as e:
        result_queue.put({"status": "error", "error": str(e)})  # type: ignore


async def run_marker_in_isolated_process(file_path: str) -> str:
    loop = get_running_loop()

    ctx = multiprocessing.get_context("spawn")

    manager = ctx.Manager()
    result_queue = manager.Queue()

    p = ctx.Process(target=_marker_worker_process, args=(file_path, result_queue))  # type: ignore
    p.start()

    await loop.run_in_executor(None, p.join)

    if not result_queue.empty():
        result = result_queue.get()
        if result["status"] == "success":
            return result["data"]
        else:
            raise RuntimeError(f"Marker Process: {result['error']}")
    else:
        raise RuntimeError("Marker Process has been stopped imediately")


async def process_knowledge(knowledge_id: UUID):
    await _knowledge_queue.put(knowledge_id)
    logger_info("Extractor", f"Added {knowledge_id}")


async def knowledge_worker_daemon():
    while True:
        knowledge_id = await _knowledge_queue.get()
        try:
            logger_info("RAG", f"Executing {knowledge_id}")
            await _run_rag_pipeline(knowledge_id)
        except CancelledError:
            break
        except Exception as e:
            logger_error("RAG", f"RAG pipeline {knowledge_id}: {e!s}")


async def _run_rag_pipeline(knowledge_id: UUID):
    """
    RAG processing
    """

    async with AsyncSessionLocal() as db:
        knowledge = await db.get(Knowledge, knowledge_id)
        if not knowledge:
            return
        try:
            store_service = StoreService()
            file_path = store_service.get_file_path(knowledge.id)

            knowledge.status = KnowledgeStatus.EXTRACTING
            await db.commit()

            extracted_text = await run_marker_in_isolated_process(file_path)

            knowledge.status = KnowledgeStatus.CHUNKING
            await db.commit()

            text_splitter = RecursiveCharacterTextSplitter()
            chunks = text_splitter.split_text(extracted_text)

            knowledge.status = KnowledgeStatus.EMBEDDING
            await db.commit()

            points: list[PointStruct] = []

            embedding_service = EmbeddingService(app_qdrant_client)

            for chunk in chunks:
                vector = await embedding_service.embed(chunk)
                points.append(
                    PointStruct(
                        id=str(uuid4()),
                        payload={"text": chunk, "knowledge_id": str(knowledge.id)},
                        vector=vector,
                    )
                )

            await app_qdrant_client.upsert(
                collection_name=settings.QDRANT_COLLECTION, points=points
            )

            knowledge.status = KnowledgeStatus.COMPLETED
            await db.commit()
        except Exception as e:
            logger_error("RAG", str(e))
            knowledge.status = KnowledgeStatus.FAILED
            await db.commit()
