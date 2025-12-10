"""
Path manipulation utilities for AI Code Editor

Provides centralized, secure path operations to prevent code duplication
and security vulnerabilities like path traversal attacks.
"""

import pathlib
import re
from typing import Optional


class PathUtils:
    """
    Centralized path operations with security features.
    
    Consolidates path manipulation logic that was previously duplicated
    across multiple tool files.
    """
    
    @staticmethod
    def sanitize_path(path: str, allow_parent: bool = False) -> str:
        """
        Sanitize file path to prevent traversal attacks.
        
        Args:
            path: Path to sanitize
            allow_parent: If True, allows .. in path (use with caution)
        
        Returns:
            Sanitized absolute path
        
        Raises:
            ValueError: If path traversal detected and not allowed
        
        Example:
            >>> PathUtils.sanitize_path("./demo/src/app/page.tsx")
            '/absolute/path/demo/src/app/page.tsx'
            
            >>> PathUtils.sanitize_path("../../etc/passwd")
            ValueError: Path traversal not allowed
        """
        if not allow_parent and '..' in path:
            raise ValueError("Path traversal not allowed")
        
        return str(pathlib.Path(path).resolve())
    
    @staticmethod
    def calculate_relative_path(from_path: str, to_path: str) -> str:
        """
        Calculate relative path between two files.
        
        Useful for generating correct import statements in generated code.
        
        Args:
            from_path: Source file path
            to_path: Target file path
        
        Returns:
            Relative path from source to target
        
        Example:
            >>> PathUtils.calculate_relative_path(
            ...     "./demo/src/app/page.tsx",
            ...     "./demo/src/components/Header.tsx"
            ... )
            '../components/Header'
        """
        from_file = pathlib.Path(from_path).resolve()
        to_file = pathlib.Path(to_path).resolve()
        
        # Get directory of from_file
        from_dir = from_file.parent
        
        # Calculate relative path
        try:
            relative = to_file.relative_to(from_dir)
            # Convert to string with forward slashes and add ./
            rel_str = str(relative).replace('\\', '/')
            if not rel_str.startswith('.'):
                rel_str = './' + rel_str
            # Remove file extension for imports
            rel_str = PathUtils._remove_extension(rel_str)
            return rel_str
        except ValueError:
            # Files are on different drives or can't be made relative
            # Use absolute path from project root
            abs_path = str(to_file).replace('\\', '/')
            return PathUtils._remove_extension(abs_path)
    
    @staticmethod
    def ensure_extension(path: str, extension: str) -> str:
        """
        Ensure path has the correct file extension.
        
        Args:
            path: File path
            extension: Desired extension (with or without leading dot)
        
        Returns:
            Path with correct extension
        
        Example:
            >>> PathUtils.ensure_extension("component", ".tsx")
            'component.tsx'
            
            >>> PathUtils.ensure_extension("component.jsx", ".tsx")
            'component.tsx'
        """
        # Ensure extension starts with dot
        if not extension.startswith('.'):
            extension = '.' + extension
        
        p = pathlib.Path(path)
        if p.suffix != extension:
            return str(p.with_suffix(extension))
        return path
    
    @staticmethod
    def _remove_extension(path: str) -> str:
        """
        Remove common file extensions from path.
        
        Used internally for import statement generation.
        
        Args:
            path: File path
        
        Returns:
            Path without extension
        """
        return re.sub(r'\.(tsx|jsx|ts|js)$', '', path)
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """
        Normalize path separators and resolve relative components.
        
        Args:
            path: Path to normalize
        
        Returns:
            Normalized path with forward slashes
        
        Example:
            >>> PathUtils.normalize_path("demo\\\\src\\\\app\\\\page.tsx")
            'demo/src/app/page.tsx'
        """
        return str(pathlib.Path(path)).replace('\\', '/')
    
    @staticmethod
    def get_component_path(
        component_name: str,
        output_dir: str = "./src/components",
        use_typescript: bool = True
    ) -> str:
        """
        Generate standard component file path.
        
        Args:
            component_name: Name of component (PascalCase)
            output_dir: Output directory
            use_typescript: Use .tsx extension (vs .jsx)
        
        Returns:
            Full component file path
        
        Example:
            >>> PathUtils.get_component_path("Header", "./src/components")
            './src/components/Header.tsx'
        """
        extension = '.tsx' if use_typescript else '.jsx'
        return str(pathlib.Path(output_dir) / f"{component_name}{extension}")
    
    @staticmethod
    def ensure_dir_exists(path: str) -> pathlib.Path:
        """
        Ensure directory exists, creating if necessary.
        
        Args:
            path: Directory path
        
        Returns:
            Path object for the directory
        
        Example:
            >>> PathUtils.ensure_dir_exists("./demo/src/components")
            PosixPath('demo/src/components')
        """
        dir_path = pathlib.Path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
    
    @staticmethod
    def get_file_size(path: str) -> int:
        """
        Get file size in bytes.
        
        Args:
            path: File path
        
        Returns:
            File size in bytes
        
        Raises:
            FileNotFoundError: If file doesn't exist
        
        Example:
            >>> PathUtils.get_file_size("./README.md")
            12345
        """
        return pathlib.Path(path).stat().st_size
    
    @staticmethod
    def file_exists(path: str) -> bool:
        """
        Check if file exists and has content.
        
        Args:
            path: File path
        
        Returns:
            True if file exists and is not empty
        
        Example:
            >>> PathUtils.file_exists("./README.md")
            True
        """
        try:
            file_path = pathlib.Path(path)
            if not file_path.exists():
                return False
            if not file_path.is_file():
                return False
            # Verify file has content (not empty)
            return file_path.stat().st_size > 0
        except Exception:
            return False
