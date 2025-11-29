"""
File Manager Module for Child Agent

Provides safe file operations with validation, permission checks,
and comprehensive error handling.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from loguru import logger


class FileOperation(BaseModel):
    """Represents a file operation result"""
    operation: str
    path: str
    success: bool
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FileManager:
    """
    Manages file operations with safety checks and validation
    
    Features:
    - Path validation and sanitization
    - Whitelist/blacklist support
    - File size limits
    - Permission checks
    - Comprehensive logging
    """
    
    def __init__(
        self,
        allowed_paths: List[str] = None,
        restricted_paths: List[str] = None,
        max_file_size_mb: int = 100
    ):
        """
        Initialize File Manager
        
        Args:
            allowed_paths: List of allowed directory paths (whitelist)
            restricted_paths: List of restricted paths (blacklist)
            max_file_size_mb: Maximum file size in MB for operations
        """
        self.allowed_paths = [Path(p).resolve() for p in (allowed_paths or [])]
        self.restricted_paths = [Path(p).resolve() for p in (restricted_paths or self._default_restricted_paths())]
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        
        logger.info(f"FileManager initialized with {len(self.allowed_paths)} allowed paths")
        logger.debug(f"Restricted paths: {self.restricted_paths}")
    
    @staticmethod
    def _default_restricted_paths() -> List[str]:
        """Get default restricted system paths"""
        if os.name == 'nt':  # Windows
            return [
                r"C:\Windows\System32",
                r"C:\Windows\SysWOW64",
                r"C:\Program Files",
                r"C:\Program Files (x86)",
            ]
        else:  # Unix-like
            return [
                "/bin",
                "/sbin",
                "/usr/bin",
                "/usr/sbin",
                "/etc",
                "/sys",
                "/proc",
            ]
    
    def _validate_path(self, path: str) -> tuple[bool, Optional[str]]:
        """
        Validate if path is safe to access
        
        Args:
            path: Path to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            resolved_path = Path(path).resolve()
        except Exception as e:
            return False, f"Invalid path: {e}"
        
        # Check if path is in restricted directories
        for restricted in self.restricted_paths:
            try:
                resolved_path.relative_to(restricted)
                return False, f"Path is in restricted directory: {restricted}"
            except ValueError:
                continue
        
        # If whitelist is defined, check if path is in allowed directories
        if self.allowed_paths:
            is_allowed = False
            for allowed in self.allowed_paths:
                try:
                    resolved_path.relative_to(allowed)
                    is_allowed = True
                    break
                except ValueError:
                    continue
            
            if not is_allowed:
                return False, "Path is not in allowed directories"
        
        return True, None
    
    def read_file(self, file_path: str, encoding: str = 'utf-8') -> FileOperation:
        """
        Read contents of a file
        
        Args:
            file_path: Path to file to read
            encoding: File encoding (default: utf-8)
            
        Returns:
            FileOperation with file contents in metadata['content']
        """
        logger.info(f"Reading file: {file_path}")
        
        # Validate path
        is_valid, error = self._validate_path(file_path)
        if not is_valid:
            logger.error(f"Path validation failed: {error}")
            return FileOperation(
                operation="read",
                path=file_path,
                success=False,
                error=error
            )
        
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            error = f"File does not exist: {file_path}"
            logger.error(error)
            return FileOperation(
                operation="read",
                path=file_path,
                success=False,
                error=error
            )
        
        # Check if it's a file (not directory)
        if not path.is_file():
            error = f"Path is not a file: {file_path}"
            logger.error(error)
            return FileOperation(
                operation="read",
                path=file_path,
                success=False,
                error=error
            )
        
        # Check file size
        file_size = path.stat().st_size
        if file_size > self.max_file_size_bytes:
            error = f"File too large: {file_size / 1024 / 1024:.2f} MB (max: {self.max_file_size_bytes / 1024 / 1024} MB)"
            logger.error(error)
            return FileOperation(
                operation="read",
                path=file_path,
                success=False,
                error=error
            )
        
        # Read file
        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            
            logger.success(f"Successfully read file: {file_path} ({file_size} bytes)")
            return FileOperation(
                operation="read",
                path=str(path),
                success=True,
                metadata={
                    'content': content,
                    'size_bytes': file_size,
                    'encoding': encoding
                }
            )
        except Exception as e:
            error = f"Error reading file: {e}"
            logger.error(error)
            return FileOperation(
                operation="read",
                path=file_path,
                success=False,
                error=error
            )
    
    def write_file(
        self,
        file_path: str,
        content: str,
        encoding: str = 'utf-8',
        create_dirs: bool = True,
        overwrite: bool = False
    ) -> FileOperation:
        """
        Write content to a file
        
        Args:
            file_path: Path to file to write
            content: Content to write
            encoding: File encoding (default: utf-8)
            create_dirs: Create parent directories if they don't exist
            overwrite: Allow overwriting existing files
            
        Returns:
            FileOperation result
        """
        logger.info(f"Writing file: {file_path} (overwrite={overwrite})")
        
        # Validate path
        is_valid, error = self._validate_path(file_path)
        if not is_valid:
            logger.error(f"Path validation failed: {error}")
            return FileOperation(
                operation="write",
                path=file_path,
                success=False,
                error=error
            )
        
        path = Path(file_path)
        
        # Check if file exists and overwrite is not allowed
        if path.exists() and not overwrite:
            error = f"File already exists and overwrite=False: {file_path}"
            logger.error(error)
            return FileOperation(
                operation="write",
                path=file_path,
                success=False,
                error=error
            )
        
        # Check content size
        content_size = len(content.encode(encoding))
        if content_size > self.max_file_size_bytes:
            error = f"Content too large: {content_size / 1024 / 1024:.2f} MB (max: {self.max_file_size_bytes / 1024 / 1024} MB)"
            logger.error(error)
            return FileOperation(
                operation="write",
                path=file_path,
                success=False,
                error=error
            )
        
        # Create parent directories if needed
        if create_dirs:
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                error = f"Error creating directories: {e}"
                logger.error(error)
                return FileOperation(
                    operation="write",
                    path=file_path,
                    success=False,
                    error=error
                )
        
        # Write file
        try:
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            
            logger.success(f"Successfully wrote file: {file_path} ({content_size} bytes)")
            return FileOperation(
                operation="write",
                path=str(path),
                success=True,
                metadata={
                    'size_bytes': content_size,
                    'encoding': encoding,
                    'overwritten': path.exists()
                }
            )
        except Exception as e:
            error = f"Error writing file: {e}"
            logger.error(error)
            return FileOperation(
                operation="write",
                path=file_path,
                success=False,
                error=error
            )
    
    def delete_file(self, file_path: str, confirm: bool = True) -> FileOperation:
        """
        Delete a file
        
        Args:
            file_path: Path to file to delete
            confirm: Require confirmation (safety check)
            
        Returns:
            FileOperation result
        """
        logger.info(f"Deleting file: {file_path} (confirm={confirm})")
        
        if not confirm:
            error = "Delete operation requires confirmation"
            logger.error(error)
            return FileOperation(
                operation="delete",
                path=file_path,
                success=False,
                error=error
            )
        
        # Validate path
        is_valid, error = self._validate_path(file_path)
        if not is_valid:
            logger.error(f"Path validation failed: {error}")
            return FileOperation(
                operation="delete",
                path=file_path,
                success=False,
                error=error
            )
        
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            error = f"File does not exist: {file_path}"
            logger.error(error)
            return FileOperation(
                operation="delete",
                path=file_path,
                success=False,
                error=error
            )
        
        # Check if it's a file
        if not path.is_file():
            error = f"Path is not a file: {file_path}"
            logger.error(error)
            return FileOperation(
                operation="delete",
                path=file_path,
                success=False,
                error=error
            )
        
        # Delete file
        try:
            file_size = path.stat().st_size
            path.unlink()
            
            logger.success(f"Successfully deleted file: {file_path}")
            return FileOperation(
                operation="delete",
                path=str(path),
                success=True,
                metadata={'size_bytes': file_size}
            )
        except Exception as e:
            error = f"Error deleting file: {e}"
            logger.error(error)
            return FileOperation(
                operation="delete",
                path=file_path,
                success=False,
                error=error
            )
    
    def list_directory(self, dir_path: str, pattern: str = "*") -> FileOperation:
        """
        List contents of a directory
        
        Args:
            dir_path: Path to directory
            pattern: Glob pattern for filtering (default: *)
            
        Returns:
            FileOperation with file list in metadata['files']
        """
        logger.info(f"Listing directory: {dir_path} (pattern={pattern})")
        
        # Validate path
        is_valid, error = self._validate_path(dir_path)
        if not is_valid:
            logger.error(f"Path validation failed: {error}")
            return FileOperation(
                operation="list",
                path=dir_path,
                success=False,
                error=error
            )
        
        path = Path(dir_path)
        
        # Check if directory exists
        if not path.exists():
            error = f"Directory does not exist: {dir_path}"
            logger.error(error)
            return FileOperation(
                operation="list",
                path=dir_path,
                success=False,
                error=error
            )
        
        # Check if it's a directory
        if not path.is_dir():
            error = f"Path is not a directory: {dir_path}"
            logger.error(error)
            return FileOperation(
                operation="list",
                path=dir_path,
                success=False,
                error=error
            )
        
        # List directory
        try:
            files = []
            for item in path.glob(pattern):
                files.append({
                    'name': item.name,
                    'path': str(item),
                    'is_file': item.is_file(),
                    'is_dir': item.is_dir(),
                    'size_bytes': item.stat().st_size if item.is_file() else None,
                    'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
            
            logger.success(f"Successfully listed directory: {dir_path} ({len(files)} items)")
            return FileOperation(
                operation="list",
                path=str(path),
                success=True,
                metadata={
                    'files': files,
                    'count': len(files),
                    'pattern': pattern
                }
            )
        except Exception as e:
            error = f"Error listing directory: {e}"
            logger.error(error)
            return FileOperation(
                operation="list",
                path=dir_path,
                success=False,
                error=error
            )
    
    def get_file_info(self, file_path: str) -> FileOperation:
        """
        Get information about a file
        
        Args:
            file_path: Path to file
            
        Returns:
            FileOperation with file info in metadata
        """
        logger.info(f"Getting file info: {file_path}")
        
        # Validate path
        is_valid, error = self._validate_path(file_path)
        if not is_valid:
            logger.error(f"Path validation failed: {error}")
            return FileOperation(
                operation="info",
                path=file_path,
                success=False,
                error=error
            )
        
        path = Path(file_path)
        
        # Check if path exists
        if not path.exists():
            error = f"Path does not exist: {file_path}"
            logger.error(error)
            return FileOperation(
                operation="info",
                path=file_path,
                success=False,
                error=error
            )
        
        # Get file info
        try:
            stat = path.stat()
            info = {
                'name': path.name,
                'path': str(path.resolve()),
                'is_file': path.is_file(),
                'is_dir': path.is_dir(),
                'size_bytes': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
            }
            
            logger.success(f"Successfully got file info: {file_path}")
            return FileOperation(
                operation="info",
                path=str(path),
                success=True,
                metadata=info
            )
        except Exception as e:
            error = f"Error getting file info: {e}"
            logger.error(error)
            return FileOperation(
                operation="info",
                path=file_path,
                success=False,
                error=error
            )
