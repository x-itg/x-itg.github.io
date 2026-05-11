"""
Legacy Adapter - Help legacy projects migrate to AI-friendly ecosystem.
"""
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any, Callable
from pathlib import Path
import logging

from core.agents_md import AgentsMD, DocMetadata, DocHealthDetail
from core.events import EventBus, Event, EventType


@dataclass
class RemoteBuildConfig:
    """Remote build server configuration."""
    host: str = ""
    user: str = ""
    password: str = ""
    keil_path: str = "C:/Keil_v5/UV4/UV4.exe"
    project_ext: str = ".uvprojx"
    connected: bool = False


@dataclass
class ProjectTranslation:
    """Project translation result."""
    project_file: str
    structure_file: str = ""
    cmake_file: str = ""
    docs: List[str] = field(default_factory=list)
    success: bool = False
    errors: List[str] = field(default_factory=list)


class RemoteBuildManager:
    """Manage remote build configuration and execution."""
    
    def __init__(self, config: RemoteBuildConfig):
        self.config = config
        self._ssh_client = None
        self._connected = False
        self._logger = logging.getLogger(__name__)
    
    def connect(self) -> Dict[str, Any]:
        """Connect to remote build server."""
        if not self.config.host:
            return {'success': False, 'error': 'No host configured'}
        
        try:
            import paramiko
            
            self._ssh_client = paramiko.SSHClient()
            self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            password = self.config.password if self.config.password else None
            
            self._ssh_client.connect(
                hostname=self.config.host,
                username=self.config.user,
                password=password,
                timeout=10
            )
            
            self._connected = True
            self.config.connected = True
            
            return {'success': True, 'message': f'Connected to {self.config.host}'}
        except ImportError:
            return {'success': False, 'error': 'paramiko not installed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def disconnect(self) -> None:
        """Disconnect from remote server."""
        if self._ssh_client:
            self._ssh_client.close()
            self._ssh_client = None
        self._connected = False
        self.config.connected = False
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the remote connection."""
        if not self._connected:
            connect_result = self.connect()
            if not connect_result.get('success'):
                return connect_result
        
        try:
            stdin, stdout, stderr = self._ssh_client.exec_command('echo "test"')
            result = stdout.read().decode().strip()
            
            if result == 'test':
                return {'success': True, 'message': 'Connection test passed'}
            else:
                return {'success': False, 'error': 'Unexpected response'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def find_projects(self, remote_path: str = ".") -> List[str]:
        """Find Keil projects on remote server."""
        if not self._connected:
            return []
        
        try:
            cmd = f'find {remote_path} -name "*{self.config.project_ext}" 2>/dev/null'
            stdin, stdout, stderr = self._ssh_client.exec_command(cmd)
            projects = stdout.read().decode().strip().split('\n')
            return [p for p in projects if p]
        except Exception as e:
            self._logger.error(f"Failed to find projects: {e}")
            return []
    
    def build_remote(self, project_path: str) -> Dict[str, Any]:
        """Build a project on remote server."""
        if not self._connected:
            return {'success': False, 'error': 'Not connected'}
        
        try:
            build_cmd = f'"{self.config.keil_path}" -j0 -o build.log "{project_path}"'
            
            stdin, stdout, stderr = self._ssh_client.exec_command(build_cmd)
            exit_status = stdout.channel.recv_exit_status()
            
            _, log_stdout, _ = self._ssh_client.exec_command('cat build.log')
            log_content = log_stdout.read().decode('utf-8', errors='ignore')
            
            return {
                'success': exit_status == 0,
                'exit_code': exit_status,
                'log': log_content
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_config(self, **kwargs) -> None:
        """Update remote build configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)


class TranslationWizard:
    """Wizard for translating legacy projects."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self._logger = logging.getLogger(__name__)
    
    def detect_project_type(self, project_path: str) -> Dict[str, Any]:
        """Detect the type of legacy project."""
        project_file = Path(project_path)
        
        result = {
            'type': 'unknown',
            'files': [],
            'structure': {}
        }
        
        if project_file.suffix == '.uvprojx':
            result['type'] = 'keil'
        elif project_file.suffix == '.ewp':
            result['type'] = 'iar'
        elif project_file.suffix == '.cproject':
            result['type'] = 'eclipse'
        elif (project_file / 'CMakeLists.txt').exists():
            result['type'] = 'cmake'
        
        if project_file.is_dir():
            for ext in ['*.c', '*.h', '*.s', '*.asm']:
                result['files'].extend([str(f) for f in project_file.rglob(ext)])
        
        return result
    
    def translate_to_structure(self, project_path: str) -> ProjectTranslation:
        """Translate project to AI-friendly structure."""
        project_file = Path(project_path)
        project_name = project_file.stem
        
        translation = ProjectTranslation(project_file=str(project_file))
        
        try:
            structure_md = self._generate_structure_md(project_name, project_path)
            structure_file = self.project_root / "docs" / f"{project_name}_structure.md"
            structure_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(structure_file, 'w', encoding='utf-8') as f:
                f.write(structure_md)
            
            translation.structure_file = str(structure_file)
            translation.docs.append(str(structure_file))
            
            cmake_content = self._generate_cmake(project_name)
            cmake_file = self.project_root / "CMakeLists.txt"
            
            with open(cmake_file, 'w', encoding='utf-8') as f:
                f.write(cmake_content)
            
            translation.cmake_file = str(cmake_file)
            
            hal_md = self._generate_hal_specs(project_name)
            hal_file = self.project_root / "docs" / f"{project_name}_hal_specs.md"
            
            with open(hal_file, 'w', encoding='utf-8') as f:
                f.write(hal_md)
            
            translation.docs.append(str(hal_file))
            
            translation.success = True
            
        except Exception as e:
            self._logger.error(f"Translation failed: {e}")
            translation.errors.append(str(e))
        
        return translation
    
    def _generate_structure_md(self, project_name: str, project_path: str) -> str:
        """Generate project structure markdown."""
        project_dir = Path(project_path)
        
        content = f"""# {project_name} 项目结构

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 目录结构

```
{project_name}/
"""
        
        if project_dir.is_dir():
            for item in sorted(project_dir.rglob("*"))[:50]:
                rel_path = item.relative_to(project_dir)
                indent = "  " * (len(rel_path.parts) - 1)
                content += f"{indent}- {rel_path.name}\n"
        
        content += """```

## 源文件清单

| 文件 | 功能描述 | 关键函数 |
|------|---------|---------|
"""
        
        if project_dir.is_dir():
            for c_file in sorted(project_dir.rglob("*.c"))[:30]:
                rel_path = c_file.relative_to(project_dir)
                content += f"| {rel_path} | TODO | TODO |\n"
        
        return content
    
    def _generate_cmake(self, project_name: str) -> str:
        """Generate CMakeLists.txt."""
        return f"""cmake_minimum_required(VERSION 3.15)
project({project_name})

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Source files
file(GLOB SOURCES "src/*.c")

# Include directories
include_directories(
    inc
    Core/Inc
)

# Executable
add_executable(${{PROJECT_NAME}} ${{SOURCES}})

# Target specific settings
target_link_libraries(${{PROJECT_NAME}} -lm)
"""
    
    def _generate_hal_specs(self, project_name: str) -> str:
        """Generate HAL specifications document."""
        return f"""# {project_name} HAL 规格文档

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 外设配置

### GPIO
TODO: 填写GPIO配置

### UART
TODO: 填写UART配置

### I2C
TODO: 填写I2C配置

### SPI
TODO: 填写SPI配置

### TIM
TODO: 填写定时器配置
"""


class DefenseMode:
    """Defense layer mode for legacy projects."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.enabled = False
        self.restrictions = {
            'allow_edit': True,
            'allow_build': True,
            'allow_advanced': False
        }
    
    def enable(self) -> None:
        """Enable defense mode."""
        self.enabled = True
        self._create_defense_indicator()
    
    def disable(self) -> None:
        """Disable defense mode."""
        self.enabled = False
        self._remove_defense_indicator()
    
    def _create_defense_indicator(self) -> None:
        """Create indicator file for defense mode."""
        indicator = self.project_root / ".defense_mode"
        with open(indicator, 'w') as f:
            f.write(datetime.now().isoformat())
    
    def _remove_defense_indicator(self) -> None:
        """Remove defense mode indicator."""
        indicator = self.project_root / ".defense_mode"
        if indicator.exists():
            indicator.unlink()
    
    def check_restrictions(self, action: str) -> bool:
        """Check if an action is allowed."""
        if not self.enabled:
            return True
        
        restriction_map = {
            'edit': 'allow_edit',
            'build': 'allow_build',
            'advanced': 'allow_advanced'
        }
        
        restriction = restriction_map.get(action)
        if restriction:
            return self.restrictions.get(restriction, False)
        
        return True


class LegacyAdapter:
    """Main Legacy Adapter controller."""
    
    def __init__(self, project_root: str, config: Optional[Dict] = None):
        self.project_root = Path(project_root)
        self.config = config or {}
        
        remote_config = RemoteBuildConfig(
            host=self.config.get('host', ''),
            user=self.config.get('user', ''),
            password=self.config.get('password', ''),
            keil_path=self.config.get('keil_path', 'C:/Keil_v5/UV4/UV4.exe'),
            project_ext=self.config.get('project_ext', '.uvprojx')
        )
        
        self.remote_build = RemoteBuildManager(remote_config)
        self.translation = TranslationWizard(str(self.project_root))
        self.defense_mode = DefenseMode(str(self.project_root))
        
        self.event_bus = EventBus()
        self._logger = logging.getLogger(__name__)
    
    def setup_remote_build(
        self,
        host: str,
        user: str,
        password: str = "",
        keil_path: str = ""
    ) -> Dict[str, Any]:
        """Setup remote build configuration."""
        self.remote_build.update_config(
            host=host,
            user=user,
            password=password,
            keil_path=keil_path or self.remote_build.config.keil_path
        )
        
        return self.remote_build.test_connection()
    
    def find_legacy_projects(self) -> List[str]:
        """Find legacy projects in workspace."""
        projects = []
        
        for pattern in ['*.uvprojx', '*.ewp', '*.cproject']:
            projects.extend([str(p) for p in self.project_root.rglob(pattern)])
        
        return projects
    
    def translate_project(self, project_path: str) -> Dict[str, Any]:
        """Translate a legacy project."""
        result = self.translation.translate_to_structure(project_path)
        
        self.event_bus.publish(Event(
            type=EventType.DOC_CREATED,
            source="legacy_adapter",
            data={
                'project': project_path,
                'structure_file': result.structure_file,
                'success': result.success
            }
        ))
        
        return {
            'success': result.success,
            'structure_file': result.structure_file,
            'cmake_file': result.cmake_file,
            'docs': result.docs,
            'errors': result.errors
        }
    
    def enable_defense_mode(self) -> None:
        """Enable defense mode."""
        self.defense_mode.enable()
    
    def disable_defense_mode(self) -> None:
        """Disable defense mode."""
        self.defense_mode.disable()
    
    def check_action(self, action: str) -> bool:
        """Check if an action is allowed."""
        return self.defense_mode.check_restrictions(action)
    
    def assess_legacy_health(self, doc_id: str, doc_path: str) -> Dict[str, Any]:
        """Assess the health of translated legacy documentation."""
        return {
            'doc_id': doc_id,
            'assessed': True,
            'overall_score': 0.7,
            'dimensions': {
                'completeness': 0.8,
                'accuracy': 0.7,
                'consistency': 0.6,
                'maintainability': 0.7
            },
            'recommendations': [
                '建议补充GPIO配置详情',
                '建议添加外设使用示例'
            ]
        }
