from typing import List, Dict, Any, Callable, TypeVar, Generic
from concurrent.futures import ThreadPoolExecutor
import asyncio
from openai import OpenAI
import logging
from functools import partial

T = TypeVar('T')
R = TypeVar('R')

class BatchProcessor(Generic[T, R]):
    """Generic batch processor for OpenAI API calls"""
    
    def __init__(self, 
                 batch_size: int = 20,
                 max_workers: int = 5,
                 max_retries: int = 3,
                 retry_delay: float = 1.0):
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(__name__)

    async def process_batch_async(self,
                                items: List[T],
                                process_func: Callable[[List[T]], List[R]]) -> List[R]:
        """Process items in batches asynchronously"""
        results = []
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            try:
                batch_results = await self._process_with_retry(batch, process_func)
                results.extend(batch_results)
            except Exception as e:
                self.logger.error(f"Batch processing error: {str(e)}")
                # Return empty results for failed items
                results.extend([None] * len(batch))
        return results

    def process_batch(self,
                     items: List[T],
                     process_func: Callable[[List[T]], List[R]]) -> List[R]:
        """Process items in batches synchronously"""
        return asyncio.run(self.process_batch_async(items, process_func))

    async def _process_with_retry(self,
                                batch: List[T],
                                process_func: Callable[[List[T]], List[R]],
                                attempt: int = 1) -> List[R]:
        """Process batch with retry logic"""
        try:
            return process_func(batch)
        except Exception as e:
            if attempt < self.max_retries:
                self.logger.warning(f"Retry attempt {attempt} for batch processing: {str(e)}")
                await asyncio.sleep(self.retry_delay * attempt)
                return await self._process_with_retry(batch, process_func, attempt + 1)
            raise 