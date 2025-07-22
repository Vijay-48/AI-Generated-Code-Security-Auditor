"""
Caching service for AI Code Security Auditor
Provides intelligent caching for scan results, LLM responses, and patches
"""
import json
import hashlib
import asyncio
from typing import Any, Dict, Optional, List
from datetime import datetime, timezone
import redis.asyncio as redis
from app.config import settings

class CacheService:
    """
    Smart caching service with hierarchical cache keys and TTL management
    
    Cache Key Strategy:
    - Scan Results: scan:{code_hash}:{language}:{tools_config}
    - LLM Responses: llm:{model}:{content_hash}:{operation_type}
    - Patches: patch:{vulnerability_id}:{code_hash}:{model}
    - Job Status: job:{job_id}
    """
    
    def __init__(self):
        self.redis_client = None
        self.connected = False
        
    async def connect(self):
        """Initialize Redis connection"""
        try:
            if settings.REDIS_PASSWORD:
                connection_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
            else:
                connection_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
            
            self.redis_client = redis.from_url(
                connection_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Test connection
            await self.redis_client.ping()
            self.connected = True
            print("✅ Redis cache connected successfully")
            
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            self.connected = False
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            self.connected = False

    def _generate_cache_key(self, prefix: str, *components) -> str:
        """Generate consistent cache key from components"""
        # Create hash from components for consistent key generation
        content = "|".join(str(c) for c in components)
        hash_part = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"{prefix}:{hash_part}"
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate hash for content-based caching"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    async def get_scan_results(self, code: str, language: str, tools_config: Dict) -> Optional[Dict]:
        """Retrieve cached scan results"""
        if not self.connected:
            return None
            
        try:
            code_hash = self._generate_content_hash(code)
            tools_hash = self._generate_content_hash(json.dumps(tools_config, sort_keys=True))
            cache_key = self._generate_cache_key("scan", code_hash, language, tools_hash)
            
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                result = json.loads(cached_data)
                result['cache_hit'] = True
                result['cached_at'] = result.get('cached_at')
                return result
                
        except Exception as e:
            print(f"Cache get error: {e}")
        
        return None
    
    async def cache_scan_results(self, code: str, language: str, tools_config: Dict, results: Dict):
        """Cache scan results with appropriate TTL"""
        if not self.connected:
            return
            
        try:
            code_hash = self._generate_content_hash(code)
            tools_hash = self._generate_content_hash(json.dumps(tools_config, sort_keys=True))
            cache_key = self._generate_cache_key("scan", code_hash, language, tools_hash)
            
            # Add metadata
            results_with_meta = {
                **results,
                'cached_at': datetime.now(timezone.utc).isoformat(),
                'cache_key': cache_key,
                'cache_hit': False
            }
            
            await self.redis_client.setex(
                cache_key,
                settings.CACHE_TTL_SCAN_RESULTS,
                json.dumps(results_with_meta)
            )
            
        except Exception as e:
            print(f"Cache set error: {e}")
    
    async def get_llm_response(self, model: str, content: str, operation_type: str) -> Optional[Dict]:
        """Retrieve cached LLM response"""
        if not self.connected:
            return None
            
        try:
            content_hash = self._generate_content_hash(content)
            cache_key = self._generate_cache_key("llm", model, content_hash, operation_type)
            
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
                
        except Exception as e:
            print(f"LLM cache get error: {e}")
        
        return None
    
    async def cache_llm_response(self, model: str, content: str, operation_type: str, response: Dict):
        """Cache LLM response with long TTL"""
        if not self.connected:
            return
            
        try:
            content_hash = self._generate_content_hash(content)
            cache_key = self._generate_cache_key("llm", model, content_hash, operation_type)
            
            response_with_meta = {
                **response,
                'cached_at': datetime.now(timezone.utc).isoformat(),
                'model_used': model,
                'operation_type': operation_type
            }
            
            await self.redis_client.setex(
                cache_key,
                settings.CACHE_TTL_LLM_RESPONSES,
                json.dumps(response_with_meta)
            )
            
        except Exception as e:
            print(f"LLM cache set error: {e}")
    
    async def get_patch_cache(self, vulnerability_id: str, code: str, model: str) -> Optional[Dict]:
        """Get cached patch for specific vulnerability and code combination"""
        if not self.connected:
            return None
            
        try:
            code_hash = self._generate_content_hash(code)
            cache_key = self._generate_cache_key("patch", vulnerability_id, code_hash, model)
            
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
                
        except Exception as e:
            print(f"Patch cache get error: {e}")
        
        return None
    
    async def cache_patch(self, vulnerability_id: str, code: str, model: str, patch: Dict):
        """Cache generated patch with extended TTL"""
        if not self.connected:
            return
            
        try:
            code_hash = self._generate_content_hash(code)
            cache_key = self._generate_cache_key("patch", vulnerability_id, code_hash, model)
            
            patch_with_meta = {
                **patch,
                'cached_at': datetime.now(timezone.utc).isoformat(),
                'vulnerability_id': vulnerability_id,
                'model_used': model
            }
            
            await self.redis_client.setex(
                cache_key,
                settings.CACHE_TTL_PATCHES,
                json.dumps(patch_with_meta)
            )
            
        except Exception as e:
            print(f"Patch cache set error: {e}")
    
    async def set_job_progress(self, job_id: str, progress: Dict):
        """Update job progress for real-time tracking"""
        if not self.connected:
            return
            
        try:
            cache_key = f"job:{job_id}"
            progress_with_timestamp = {
                **progress,
                'updated_at': datetime.now(timezone.utc).isoformat(),
                'job_id': job_id
            }
            
            # Short TTL for job progress (jobs should complete within 1 hour)
            await self.redis_client.setex(
                cache_key,
                3600,
                json.dumps(progress_with_timestamp)
            )
            
        except Exception as e:
            print(f"Job progress set error: {e}")
    
    async def get_job_progress(self, job_id: str) -> Optional[Dict]:
        """Get current job progress"""
        if not self.connected:
            return None
            
        try:
            cache_key = f"job:{job_id}"
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
                
        except Exception as e:
            print(f"Job progress get error: {e}")
        
        return None
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics and health metrics"""
        if not self.connected:
            return {"status": "disconnected"}
            
        try:
            info = await self.redis_client.info()
            
            # Count different types of keys
            all_keys = await self.redis_client.keys("*")
            stats = {
                "status": "connected",
                "total_keys": len(all_keys),
                "scan_cache_keys": len([k for k in all_keys if k.startswith("scan:")]),
                "llm_cache_keys": len([k for k in all_keys if k.startswith("llm:")]),
                "patch_cache_keys": len([k for k in all_keys if k.startswith("patch:")]),
                "job_keys": len([k for k in all_keys if k.startswith("job:")]),
                "redis_memory_used": info.get("used_memory_human", "unknown"),
                "redis_uptime": info.get("uptime_in_seconds", 0),
                "cache_hit_ratio": "calculated_by_application"  # Would need counters
            }
            
            return stats
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def clear_cache(self, cache_type: Optional[str] = None):
        """Clear cache by type or all cache"""
        if not self.connected:
            return False
            
        try:
            if cache_type:
                pattern = f"{cache_type}:*"
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                    print(f"Cleared {len(keys)} {cache_type} cache entries")
            else:
                await self.redis_client.flushdb()
                print("Cleared all cache entries")
            
            return True
            
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False

# Global cache instance
cache_service = CacheService()

async def init_cache():
    """Initialize cache service"""
    await cache_service.connect()

async def shutdown_cache():
    """Shutdown cache service"""
    await cache_service.disconnect()