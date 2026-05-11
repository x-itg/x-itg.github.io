"""
Configuration management module.
"""
import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ProjectConfig:
    root: str = "./workspace"
    agents_md: str = "docs/agents.md"
    decision_ledger: str = "docs/.decision_ledger/"
    specs_dir: str = "docs/specs/"
    history_dir: str = "docs/history/"
    skills_dir: str = ".skills/"


@dataclass
class SerialConfig:
    port: str = "COM3"
    baudrate: int = 115200
    timeout: float = 1.0


@dataclass
class RemoteBuildConfig:
    enabled: bool = False
    host: str = ""
    user: str = ""
    password: str = ""
    keil_path: str = "C:/Keil_v5/UV4/UV4.exe"
    project_ext: str = ".uvprojx"


@dataclass
class ConvergenceConfig:
    max_iterations: int = 10
    convergence_threshold: float = 0.95
    test_timeout: int = 300
    build_timeout: int = 180


@dataclass
class HealthThresholds:
    healthy: float = 0.8
    warning: float = 0.5
    danger: float = 0.3


@dataclass
class KnowledgeVitalsConfig:
    health_thresholds: HealthThresholds = field(default_factory=HealthThresholds)
    cold_document_days: int = 180
    check_interval: int = 3600


@dataclass
class SchematicConfig:
    pdf_storage: str = "docs/schematics/"
    ocr_cache: str = ".cache/ocr/"
    code_refs: str = ".code_refs.json"


@dataclass
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 8765
    debug: bool = False


@dataclass
class LoggingConfig:
    level: str = "INFO"
    file: str = "logs/ide_plugins.log"


@dataclass
class Config:
    project: ProjectConfig = field(default_factory=ProjectConfig)
    serial: SerialConfig = field(default_factory=SerialConfig)
    remote_build: RemoteBuildConfig = field(default_factory=RemoteBuildConfig)
    convergence: ConvergenceConfig = field(default_factory=ConvergenceConfig)
    knowledge_vitals: KnowledgeVitalsConfig = field(default_factory=KnowledgeVitalsConfig)
    schematic: SchematicConfig = field(default_factory=SchematicConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @classmethod
    def from_yaml(cls, path: str) -> 'Config':
        """Load configuration from YAML file."""
        if not os.path.exists(path):
            return cls()
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        
        config = cls()
        
        if 'project' in data:
            config.project = ProjectConfig(**data['project'])
        if 'serial' in data:
            config.serial = SerialConfig(**data['serial'])
        if 'remote_build' in data:
            config.remote_build = RemoteBuildConfig(**data['remote_build'])
        if 'convergence' in data:
            config.convergence = ConvergenceConfig(**data['convergence'])
        if 'knowledge_vitals' in data:
            thresholds_data = data['knowledge_vitals'].pop('health_thresholds', {})
            config.knowledge_vitals = KnowledgeVitalsConfig(
                health_thresholds=HealthThresholds(**thresholds_data),
                **{k: v for k, v in data['knowledge_vitals'].items() if k != 'health_thresholds'}
            )
        if 'schematic' in data:
            config.schematic = SchematicConfig(**data['schematic'])
        if 'server' in data:
            config.server = ServerConfig(**data['server'])
        if 'logging' in data:
            config.logging = LoggingConfig(**data['logging'])
        
        return config

    def to_yaml(self, path: str) -> None:
        """Save configuration to YAML file."""
        data = {
            'project': vars(self.project),
            'serial': vars(self.serial),
            'remote_build': vars(self.remote_build),
            'convergence': vars(self.convergence),
            'knowledge_vitals': {
                'health_thresholds': vars(self.knowledge_vitals.health_thresholds),
                'cold_document_days': self.knowledge_vitals.cold_document_days,
                'check_interval': self.knowledge_vitals.check_interval
            },
            'schematic': vars(self.schematic),
            'server': vars(self.server),
            'logging': vars(self.logging)
        }
        
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


# Global config instance
_config: Optional[Config] = None


def get_config(config_path: str = "config.yaml") -> Config:
    """Get the global config instance."""
    global _config
    if _config is None:
        _config = Config.from_yaml(config_path)
    return _config


def reload_config(config_path: str = "config.yaml") -> Config:
    """Reload configuration from file."""
    global _config
    _config = Config.from_yaml(config_path)
    return _config
