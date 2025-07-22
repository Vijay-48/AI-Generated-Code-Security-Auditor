"""
Git Repository Integration Service
Handles Git repository cloning, file discovery, and metadata extraction
"""
import os
import git
import tempfile
import hashlib
import fnmatch
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse
import shutil
import asyncio
from concurrent.futures import ThreadPoolExecutor

@dataclass
class RepositoryInfo:
    """Repository metadata and configuration"""
    url: str
    branch: str = "main"
    commit: Optional[str] = None
    local_path: Optional[str] = None
    clone_path: Optional[str] = None
    
    # Scanning configuration
    include_patterns: List[str] = None
    exclude_patterns: List[str] = None
    max_file_size: int = 1024 * 1024  # 1MB default
    max_files: int = 1000  # Safety limit
    
    def __post_init__(self):
        if self.include_patterns is None:
            # Default patterns for security scanning
            self.include_patterns = [
                "*.py", "*.js", "*.jsx", "*.ts", "*.tsx", 
                "*.java", "*.go", "*.rb", "*.php", "*.cs",
                "*.cpp", "*.c", "*.h", "*.hpp", "*.rs",
                "*.sh", "*.bash", "*.ps1", "*.yaml", "*.yml",
                "*.json", "*.xml", "*.sql", "*.dockerfile", "Dockerfile*"
            ]
        
        if self.exclude_patterns is None:
            # Default exclusions
            self.exclude_patterns = [
                "*/node_modules/*", "*/.git/*", "*/venv/*", "*/env/*",
                "*/__pycache__/*", "*/build/*", "*/dist/*", "*/target/*",
                "*.min.js", "*.min.css", "*/vendor/*", "*/.vscode/*",
                "*/.idea/*", "*/coverage/*", "*/test_*", "*_test.*",
                "*/tests/*", "*/spec/*", "*/mock*", "*/fixtures/*"
            ]

@dataclass 
class FileInfo:
    """Information about a discovered file"""
    path: str
    relative_path: str
    size: int
    language: str
    content_hash: str
    last_modified: float

class GitRepositoryService:
    """
    Service for Git repository operations and file discovery
    Supports both remote repositories and local paths
    """
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Language detection mapping
        self.language_extensions = {
            '.py': 'python',
            '.js': 'javascript', 
            '.jsx': 'javascript',
            '.ts': 'javascript',
            '.tsx': 'javascript',
            '.java': 'java',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.cs': 'csharp',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.rs': 'rust',
            '.sh': 'bash',
            '.bash': 'bash',
            '.ps1': 'powershell'
        }
    
    async def clone_repository(self, repo_info: RepositoryInfo) -> str:
        """
        Clone repository to temporary location
        Returns the path to cloned repository
        """
        if repo_info.local_path:
            # Use local repository
            if not os.path.exists(repo_info.local_path):
                raise ValueError(f"Local repository path does not exist: {repo_info.local_path}")
            return repo_info.local_path
        
        # Create temporary directory for cloning
        temp_dir = tempfile.mkdtemp(prefix="security_scan_repo_")
        clone_path = os.path.join(temp_dir, "repo")
        
        try:
            print(f"🔄 Cloning repository: {repo_info.url}")
            
            # Run git clone in thread to avoid blocking
            await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._clone_repo_sync,
                repo_info.url,
                clone_path,
                repo_info.branch,
                repo_info.commit
            )
            
            repo_info.clone_path = clone_path
            print(f"✅ Repository cloned to: {clone_path}")
            return clone_path
            
        except Exception as e:
            # Cleanup on failure
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            raise Exception(f"Failed to clone repository: {str(e)}")
    
    def _clone_repo_sync(self, url: str, clone_path: str, branch: str, commit: Optional[str]):
        """Synchronous git clone operation"""
        try:
            # Clone with depth=1 for faster cloning
            repo = git.Repo.clone_from(
                url, 
                clone_path,
                branch=branch,
                depth=1 if not commit else None
            )
            
            # Checkout specific commit if provided
            if commit:
                repo.git.checkout(commit)
                
        except git.exc.GitError as e:
            raise Exception(f"Git operation failed: {str(e)}")
    
    async def discover_files(self, repo_info: RepositoryInfo, repo_path: str) -> List[FileInfo]:
        """
        Discover scannable files in repository
        Returns list of FileInfo objects
        """
        print(f"🔍 Discovering files in repository...")
        
        discovered_files = await asyncio.get_event_loop().run_in_executor(
            self.executor,
            self._discover_files_sync,
            repo_path,
            repo_info
        )
        
        print(f"📁 Discovered {len(discovered_files)} scannable files")
        return discovered_files
    
    def _discover_files_sync(self, repo_path: str, repo_info: RepositoryInfo) -> List[FileInfo]:
        """Synchronous file discovery"""
        files = []
        repo_path_obj = Path(repo_path)
        
        # Walk through all files
        for file_path in repo_path_obj.rglob("*"):
            if not file_path.is_file():
                continue
                
            try:
                # Get relative path
                relative_path = file_path.relative_to(repo_path_obj)
                relative_str = str(relative_path)
                
                # Check exclusion patterns
                if self._should_exclude_file(relative_str, repo_info.exclude_patterns):
                    continue
                
                # Check inclusion patterns
                if not self._should_include_file(relative_str, repo_info.include_patterns):
                    continue
                
                # Get file stats
                stat = file_path.stat()
                
                # Check file size limit
                if stat.st_size > repo_info.max_file_size:
                    continue
                
                # Detect language
                language = self._detect_language(file_path)
                if not language:
                    continue  # Skip unsupported languages
                
                # Calculate content hash for caching
                content_hash = self._calculate_file_hash(file_path)
                
                files.append(FileInfo(
                    path=str(file_path),
                    relative_path=relative_str,
                    size=stat.st_size,
                    language=language,
                    content_hash=content_hash,
                    last_modified=stat.st_mtime
                ))
                
                # Safety limit
                if len(files) >= repo_info.max_files:
                    print(f"⚠️ Reached maximum file limit ({repo_info.max_files})")
                    break
                    
            except (OSError, ValueError) as e:
                # Skip files that can't be processed
                continue
        
        return files
    
    def _should_exclude_file(self, file_path: str, exclude_patterns: List[str]) -> bool:
        """Check if file should be excluded based on patterns"""
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(f"/{file_path}", pattern):
                return True
        return False
    
    def _should_include_file(self, file_path: str, include_patterns: List[str]) -> bool:
        """Check if file should be included based on patterns"""
        for pattern in include_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False
    
    def _detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file extension"""
        return self.language_extensions.get(file_path.suffix.lower())
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()[:16]  # First 16 chars for shorter keys
        except Exception:
            return "unknown"
    
    async def get_repository_metadata(self, repo_path: str) -> Dict[str, Any]:
        """Extract repository metadata"""
        try:
            repo = git.Repo(repo_path)
            
            # Get current commit info
            commit = repo.head.commit
            
            return {
                "current_branch": repo.active_branch.name if not repo.head.is_detached else None,
                "current_commit": commit.hexsha,
                "commit_message": commit.message.strip(),
                "commit_author": str(commit.author),
                "commit_date": commit.committed_datetime.isoformat(),
                "remote_url": repo.remotes.origin.url if repo.remotes else None,
                "total_commits": len(list(repo.iter_commits())),
                "is_dirty": repo.is_dirty()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def cleanup_repository(self, repo_info: RepositoryInfo):
        """Clean up cloned repository"""
        if repo_info.clone_path and os.path.exists(repo_info.clone_path):
            try:
                parent_dir = os.path.dirname(repo_info.clone_path)
                shutil.rmtree(parent_dir, ignore_errors=True)
                print(f"🧹 Cleaned up repository: {repo_info.clone_path}")
            except Exception as e:
                print(f"⚠️ Failed to cleanup repository: {e}")

# Global service instance
git_service = GitRepositoryService()