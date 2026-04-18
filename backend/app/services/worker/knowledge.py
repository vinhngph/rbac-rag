from uuid import UUID, uuid4
from asyncio import Queue, CancelledError, get_running_loop
import multiprocessing
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client.models import PointStruct
from typing import List

from app.db.session import AsyncSessionLocal
from app.models.knowledge import Knowledge
from app.core.constants import KnowledgeStatus
from app.services.store import StoreService
from app.services.extractor import extract_file_pdf
from app.services.embed import embed_chunks
from app.db.qdrant import app_qdrant_client
from app.core.config import settings
from app.core.logger import logger_info, logger_error

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
            raise RuntimeError(f"Marker Process: {result["error"]}")
    else:
        raise RuntimeError("Marker Process has been stopped imediately")


def _embed_worker_process(chunks: List[str], result_queue):  # type: ignore
    try:
        vectors = embed_chunks(chunks)
        result_queue.put({"status": "success", "data": vectors})  # type: ignore
    except Exception as e:
        result_queue.put({"status": "error", "error": str(e)})  # type: ignore


async def run_embed_in_isolated_process(chunks: List[str]):
    loop = get_running_loop()

    ctx = multiprocessing.get_context("spawn")

    manager = ctx.Manager()
    result_queue = manager.Queue()

    p = ctx.Process(target=_embed_worker_process, args=(chunks, result_queue))  # type: ignore
    p.start()

    await loop.run_in_executor(None, p.join)

    if not result_queue.empty():
        result = result_queue.get()
        if result["status"] == "success":
            return result["data"]
        else:
            raise RuntimeError(f"Marker Process: {result["error"]}")
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
            logger_error("RAG", f"RAG pipeline {knowledge_id}: {str(e)}")


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
            file_path = store_service.get_safe_path(knowledge.id)

            knowledge.status = KnowledgeStatus.EXTRACTING
            await db.commit()

            extracted_text = await run_marker_in_isolated_process(file_path)

            knowledge.status = KnowledgeStatus.CHUNKING
            await db.commit()

            text_splitter = RecursiveCharacterTextSplitter()
            chunks = text_splitter.split_text(extracted_text)

            knowledge.status = KnowledgeStatus.EMBEDDING
            await db.commit()
            vectors = await run_embed_in_isolated_process(chunks)

            points: List[PointStruct] = []
            for chunk, vector in zip(chunks, vectors):
                points.append(
                    PointStruct(
                        id=str(uuid4()),
                        vector=vector,
                        payload={"text": chunk, "knowledge_id": str(knowledge.id)},
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
