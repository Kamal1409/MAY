"""
Configuration management for MAY system
"""

import os
from pathlib import Path
from typing import Any, Dict
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """LLM configuration settings"""
    provider: str = Field(default="openai")
    model: str = Field(default="gpt-4-turbo-preview")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, gt=0)
    timeout: int = Field(default=30, gt=0)
    retry_attempts: int = Field(default=3, ge=0)


class AgentConfig(BaseModel):
    """Agent configuration settings"""
    enabled: bool = True
    max_concurrent_tasks: int = Field(default=5, gt=0)
    timeout_seconds: int = Field(default=300, gt=0)


class ResourceThresholds(BaseModel):
    """Resource threshold settings"""
    cpu_percent: int = Field(default=80, ge=0, le=100)
    memory_percent: int = Field(default=75, ge=0, le=100)
    disk_percent: int = Field(default=90, ge=0, le=100)


class Config(BaseModel):
    """Main configuration class"""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    child_agent: AgentConfig = Field(default_factory=AgentConfig)
    parent_agent: AgentConfig = Field(default_factory=AgentConfig)
    resource_agent: AgentConfig = Field(default_factory=AgentConfig)
    resource_thresholds: ResourceThresholds = Field(default_factory=ResourceThresholds)
    log_level: str = Field(default="INFO")
    enable_safety_checks: bool = True


def load_config(config_path: str = None) -> Config:
    """
    Load configuration from YAML file and environment variables
    
    Args:
        config_path: Path to config.yaml file. If None, uses default location.
        
    Returns:
        Config object with loaded settings
    """
    # Load environment variables
    load_dotenv()
    
    # Determine config file path
    if config_path is None:
        project_root = Path(__file__).parent.parent
        config_path = project_root / "config.yaml"
    
    # Load YAML configuration
    config_dict = {}
    if Path(config_path).exists():
        with open(config_path, 'r') as f:
            yaml_config = yaml.safe_load(f)
            
        # Extract relevant sections
        config_dict = {
            'llm': yaml_config.get('llm', {}),
            'child_agent': yaml_config.get('agents', {}).get('child_agent', {}),
            'parent_agent': yaml_config.get('agents', {}).get('parent_agent', {}),
            'resource_agent': yaml_config.get('agents', {}).get('resource_agent', {}),
            'resource_thresholds': yaml_config.get('agents', {}).get('resource_agent', {}).get('thresholds', {}),
            'log_level': yaml_config.get('logging', {}).get('level', 'INFO'),
            'enable_safety_checks': yaml_config.get('security', {}).get('enable_safety_checks', True),
        }
    
    # Override with environment variables
    if os.getenv('LLM_PROVIDER'):
        config_dict.setdefault('llm', {})['provider'] = os.getenv('LLM_PROVIDER')
    if os.getenv('LLM_MODEL'):
        config_dict.setdefault('llm', {})['model'] = os.getenv('LLM_MODEL')
    if os.getenv('LOG_LEVEL'):
        config_dict['log_level'] = os.getenv('LOG_LEVEL')
    
    return Config(**config_dict)


def get_api_key(provider: str) -> str:
    """
    Get API key for specified LLM provider
    
    Args:
        provider: LLM provider name (openai, anthropic, etc.)
        
    Returns:
        API key string
        
    Raises:
        ValueError: If API key not found
    """
    key_map = {
        'openai': 'OPENAI_API_KEY',
        'anthropic': 'ANTHROPIC_API_KEY',
    }
    
    env_var = key_map.get(provider.lower())
    if not env_var:
        raise ValueError(f"Unknown LLM provider: {provider}")
    
    api_key = os.getenv(env_var)
    if not api_key:
        raise ValueError(f"API key not found for {provider}. Please set {env_var} in .env file")
    
    return api_key
