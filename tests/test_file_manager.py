"""
Unit tests for File Manager module
"""

import pytest
import tempfile
import os
from pathlib import Path
from agents.child_agent.file_manager import FileManager, FileOperation


class TestFileManager:
    """Test suite for FileManager class"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def file_manager(self, temp_dir):
        """Create a FileManager instance with temp directory allowed"""
        return FileManager(
            allowed_paths=[temp_dir],
            max_file_size_mb=1  # 1 MB for testing
        )
    
    def test_initialization(self, file_manager):
        """Test FileManager initialization"""
        assert file_manager is not None
        assert len(file_manager.restricted_paths) > 0
        assert file_manager.max_file_size_bytes == 1 * 1024 * 1024
    
    def test_read_file_success(self, file_manager, temp_dir):
        """Test successful file read"""
        # Create a test file
        test_file = Path(temp_dir) / "test.txt"
        test_content = "Hello, World!"
        test_file.write_text(test_content)
        
        # Read the file
        result = file_manager.read_file(str(test_file))
        
        assert result.success is True
        assert result.operation == "read"
        assert result.metadata['content'] == test_content
        assert result.error is None
    
    def test_read_file_not_exists(self, file_manager, temp_dir):
        """Test reading non-existent file"""
        test_file = Path(temp_dir) / "nonexistent.txt"
        
        result = file_manager.read_file(str(test_file))
        
        assert result.success is False
        assert "does not exist" in result.error
    
    def test_read_file_restricted_path(self, file_manager):
        """Test reading from restricted path"""
        if os.name == 'nt':
            restricted_file = r"C:\Windows\System32\test.txt"
        else:
            restricted_file = "/etc/passwd"
        
        result = file_manager.read_file(restricted_file)
        
        assert result.success is False
        assert "restricted" in result.error.lower()
    
    def test_write_file_success(self, file_manager, temp_dir):
        """Test successful file write"""
        test_file = Path(temp_dir) / "new_file.txt"
        test_content = "Test content"
        
        result = file_manager.write_file(str(test_file), test_content)
        
        assert result.success is True
        assert result.operation == "write"
        assert test_file.exists()
        assert test_file.read_text() == test_content
    
    def test_write_file_overwrite_false(self, file_manager, temp_dir):
        """Test write with overwrite=False on existing file"""
        test_file = Path(temp_dir) / "existing.txt"
        test_file.write_text("Original content")
        
        result = file_manager.write_file(
            str(test_file),
            "New content",
            overwrite=False
        )
        
        assert result.success is False
        assert "already exists" in result.error
        assert test_file.read_text() == "Original content"
    
    def test_write_file_overwrite_true(self, file_manager, temp_dir):
        """Test write with overwrite=True"""
        test_file = Path(temp_dir) / "existing.txt"
        test_file.write_text("Original content")
        
        result = file_manager.write_file(
            str(test_file),
            "New content",
            overwrite=True
        )
        
        assert result.success is True
        assert test_file.read_text() == "New content"
    
    def test_write_file_create_dirs(self, file_manager, temp_dir):
        """Test write with directory creation"""
        test_file = Path(temp_dir) / "subdir" / "nested" / "file.txt"
        
        result = file_manager.write_file(
            str(test_file),
            "Content",
            create_dirs=True
        )
        
        assert result.success is True
        assert test_file.exists()
    
    def test_write_file_too_large(self, file_manager, temp_dir):
        """Test write with content exceeding size limit"""
        test_file = Path(temp_dir) / "large.txt"
        # Create content larger than 1 MB
        large_content = "x" * (2 * 1024 * 1024)
        
        result = file_manager.write_file(str(test_file), large_content)
        
        assert result.success is False
        assert "too large" in result.error.lower()
    
    def test_delete_file_success(self, file_manager, temp_dir):
        """Test successful file deletion"""
        test_file = Path(temp_dir) / "to_delete.txt"
        test_file.write_text("Delete me")
        
        result = file_manager.delete_file(str(test_file), confirm=True)
        
        assert result.success is True
        assert not test_file.exists()
    
    def test_delete_file_no_confirm(self, file_manager, temp_dir):
        """Test delete without confirmation"""
        test_file = Path(temp_dir) / "to_delete.txt"
        test_file.write_text("Delete me")
        
        result = file_manager.delete_file(str(test_file), confirm=False)
        
        assert result.success is False
        assert "confirmation" in result.error.lower()
        assert test_file.exists()
    
    def test_delete_file_not_exists(self, file_manager, temp_dir):
        """Test deleting non-existent file"""
        test_file = Path(temp_dir) / "nonexistent.txt"
        
        result = file_manager.delete_file(str(test_file), confirm=True)
        
        assert result.success is False
        assert "does not exist" in result.error
    
    def test_list_directory_success(self, file_manager, temp_dir):
        """Test successful directory listing"""
        # Create some test files
        (Path(temp_dir) / "file1.txt").write_text("content1")
        (Path(temp_dir) / "file2.txt").write_text("content2")
        (Path(temp_dir) / "subdir").mkdir()
        
        result = file_manager.list_directory(temp_dir)
        
        assert result.success is True
        assert result.metadata['count'] == 3
        assert len(result.metadata['files']) == 3
    
    def test_list_directory_with_pattern(self, file_manager, temp_dir):
        """Test directory listing with glob pattern"""
        (Path(temp_dir) / "file1.txt").write_text("content1")
        (Path(temp_dir) / "file2.py").write_text("content2")
        (Path(temp_dir) / "file3.txt").write_text("content3")
        
        result = file_manager.list_directory(temp_dir, pattern="*.txt")
        
        assert result.success is True
        assert result.metadata['count'] == 2
    
    def test_list_directory_not_exists(self, file_manager, temp_dir):
        """Test listing non-existent directory"""
        test_dir = Path(temp_dir) / "nonexistent"
        
        result = file_manager.list_directory(str(test_dir))
        
        assert result.success is False
        assert "does not exist" in result.error
    
    def test_get_file_info_success(self, file_manager, temp_dir):
        """Test getting file info"""
        test_file = Path(temp_dir) / "info_test.txt"
        test_file.write_text("Test content")
        
        result = file_manager.get_file_info(str(test_file))
        
        assert result.success is True
        assert result.metadata['name'] == "info_test.txt"
        assert result.metadata['is_file'] is True
        assert result.metadata['size_bytes'] > 0
        assert 'created' in result.metadata
        assert 'modified' in result.metadata
    
    def test_get_file_info_directory(self, file_manager, temp_dir):
        """Test getting info for directory"""
        result = file_manager.get_file_info(temp_dir)
        
        assert result.success is True
        assert result.metadata['is_dir'] is True
        assert result.metadata['is_file'] is False
    
    def test_path_validation_whitelist(self, temp_dir):
        """Test path validation with whitelist"""
        fm = FileManager(allowed_paths=[temp_dir])
        
        # Should succeed - in whitelist
        test_file = Path(temp_dir) / "allowed.txt"
        test_file.write_text("content")
        result = fm.read_file(str(test_file))
        assert result.success is True
        
        # Should fail - not in whitelist
        other_temp = tempfile.mkdtemp()
        try:
            other_file = Path(other_temp) / "not_allowed.txt"
            other_file.write_text("content")
            result = fm.read_file(str(other_file))
            assert result.success is False
            assert "not in allowed" in result.error.lower()
        finally:
            import shutil
            shutil.rmtree(other_temp)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
