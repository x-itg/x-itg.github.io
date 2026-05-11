"""
agents.md parser and management module.
"""
import os
import re
import yaml
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum


class HotLevel(Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


class HealthStatus(Enum):
    HEALTHY = "healthy"
    SUBHEALTHY = "subhealthy"
    WARNING = "warning"
    DANGER = "danger"


@dataclass
class DocHealthDetail:
    code_consistency: float = 1.0
    physical_consistency: float = 1.0
    freshness: float = 1.0
    reference_integrity: float = 1.0
    
    @property
    def overall_score(self) -> float:
        return (
            self.code_consistency * 0.3 +
            self.physical_consistency * 0.2 +
            self.freshness * 0.3 +
            self.reference_integrity * 0.2
        )


@dataclass
class DocMetadata:
    doc_id: str
    title: str
    created: str = ""
    last_modified: str = ""
    modification_count: int = 0
    reference_count: int = 0
    last_referenced: str = ""
    health_score: float = 1.0
    health_detail: DocHealthDetail = field(default_factory=DocHealthDetail)
    status: str = "healthy"
    hot_level: str = "warm"
    wake_keywords: Dict[str, List[str]] = field(default_factory=dict)
    linked_docs: List[str] = field(default_factory=list)
    drift_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def update_reference(self):
        """Update reference count and timestamp."""
        self.reference_count += 1
        self.last_referenced = datetime.now().strftime("%Y-%m-%d")
    
    def update_health(self, new_score: float, detail: Optional[DocHealthDetail] = None):
        """Update health score."""
        self.health_score = new_score
        if detail:
            self.health_detail = detail
        self.last_modified = datetime.now().strftime("%Y-%m-%d")
        self.modification_count += 1
        
        # Update status based on score
        if new_score >= 0.8:
            self.status = "healthy"
        elif new_score >= 0.5:
            self.status = "subhealthy"
        elif new_score >= 0.3:
            self.status = "warning"
        else:
            self.status = "danger"
    
    def add_drift_record(self, drift_type: str, resolution: str, decision_ref: str = ""):
        """Add a drift history record."""
        self.drift_history.append({
            'date': datetime.now().strftime("%Y-%m-%d"),
            'type': drift_type,
            'resolution': resolution,
            'decision_ref': decision_ref
        })
    
    def to_yaml_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        return {
            'doc_id': self.doc_id,
            'title': self.title,
            'created': self.created,
            'last_modified': self.last_modified,
            'modification_count': self.modification_count,
            'reference_count': self.reference_count,
            'last_referenced': self.last_referenced,
            'health_score': round(self.health_score, 2),
            'health_detail': {
                'code_consistency': round(self.health_detail.code_consistency, 2),
                'physical_consistency': round(self.health_detail.physical_consistency, 2),
                'freshness': round(self.health_detail.freshness, 2),
                'reference_integrity': round(self.health_detail.reference_integrity, 2)
            },
            'status': self.status,
            'hot_level': self.hot_level,
            'wake_keywords': self.wake_keywords,
            'linked_docs': self.linked_docs,
            'drift_history': self.drift_history
        }


class AgentsMD:
    """Parser and manager for agents.md files."""
    
    FRONT_MATTER_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    KNOWLEDGE_VITALS_RE = re.compile(r'## 知识库体征.*?(?=##|\Z)', re.DOTALL)
    DOC_HEADER_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    
    def __init__(self, path: str):
        self.path = path
        self.content: str = ""
        self.metadata: Dict[str, Any] = {}
        self.documents: List[DocMetadata] = []
        self.vitals: Dict[str, Any] = {}
        self.risk_alerts: List[Dict[str, str]] = []
        self.fact_index: Dict[str, str] = {}
        self.wake_routes: Dict[str, List[str]] = {}
        
        if os.path.exists(path):
            self.load()
    
    def load(self) -> None:
        """Load and parse agents.md."""
        with open(self.path, 'r', encoding='utf-8') as f:
            self.content = f.read()
        
        self._parse_front_matter()
        self._parse_knowledge_vitals()
    
    def _parse_front_matter(self) -> None:
        """Parse YAML front matter."""
        match = self.FRONT_MATTER_RE.search(self.content)
        if match:
            try:
                self.metadata = yaml.safe_load(match.group(1)) or {}
            except yaml.YAMLError:
                self.metadata = {}
    
    def _parse_knowledge_vitals(self) -> None:
        """Parse knowledge vitals section."""
        match = self.KNOWLEDGE_VITALS_RE.search(self.content)
        if match:
            section = match.group(0)
            self._parse_stats(section)
            self._parse_risks(section)
            self._parse_facts(section)
            self._parse_wake_routes(section)
    
    def _parse_stats(self, section: str) -> None:
        """Parse statistics."""
        self.vitals = {}
        lines = section.split('\n')
        current_subsection = None
        
        for line in lines:
            if line.startswith('### '):
                current_subsection = line.replace('### ', '').strip()
                self.vitals[current_subsection] = {}
            elif current_subsection and ':' in line:
                key_val = line.split(':', 1)
                if len(key_val) == 2:
                    key = key_val[0].strip('- ')
                    val = key_val[1].strip()
                    try:
                        self.vitals[current_subsection][key] = int(val)
                    except ValueError:
                        try:
                            self.vitals[current_subsection][key] = float(val)
                        except ValueError:
                            self.vitals[current_subsection][key] = val
    
    def _parse_risks(self, section: str) -> None:
        """Parse risk alerts."""
        self.risk_alerts = []
        risk_lines = [l for l in section.split('\n') if l.startswith('- ')]
        
        for line in risk_lines:
            if '高危负债' in line:
                self.risk_alerts.append({'type': 'high_risk', 'content': line})
            elif '亚健康' in line:
                self.risk_alerts.append({'type': 'warning', 'content': line})
            elif '漂移告警' in line:
                self.risk_alerts.append({'type': 'drift', 'content': line})
    
    def _parse_facts(self, section: str) -> None:
        """Parse fact index."""
        self.fact_index = {}
        in_fact_section = False
        
        for line in section.split('\n'):
            if '### 事实索引' in line:
                in_fact_section = True
                continue
            if '### ' in line:
                in_fact_section = False
            if in_fact_section and '→' in line:
                parts = line.split('→')
                if len(parts) == 2:
                    fact = parts[0].strip('- ')
                    source = parts[1].strip()
                    self.fact_index[fact] = source
    
    def _parse_wake_routes(self, section: str) -> None:
        """Parse wake routes."""
        self.wake_routes = {}
        in_wake_section = False
        
        for line in section.split('\n'):
            if '### 唤醒路由' in line:
                in_wake_section = True
                continue
            if '### ' in line:
                in_wake_section = False
            if in_wake_section and '→' in line:
                parts = line.split('→')
                if len(parts) == 2:
                    keyword = parts[0].strip('- ')
                    docs = [d.strip() for d in parts[1].split(',')]
                    self.wake_routes[keyword] = docs
    
    def get_document(self, doc_id: str) -> Optional[DocMetadata]:
        """Get document metadata by ID."""
        for doc in self.documents:
            if doc.doc_id == doc_id:
                return doc
        return None
    
    def search_by_keyword(self, keyword: str) -> List[DocMetadata]:
        """Search documents by wake keyword."""
        results = []
        for doc in self.documents:
            for category, keywords in doc.wake_keywords.items():
                if keyword in keywords:
                    results.append(doc)
                    break
        return results
    
    def get_hot_documents(self) -> List[DocMetadata]:
        """Get all hot documents."""
        return [d for d in self.documents if d.hot_level == HotLevel.HOT.value]
    
    def get_unhealthy_documents(self) -> List[DocMetadata]:
        """Get all unhealthy documents."""
        return [d for d in self.documents if d.health_score < 0.5]
    
    def update_vitals(self) -> None:
        """Update knowledge vitals section."""
        total = len(self.documents)
        healthy = sum(1 for d in self.documents if d.health_score >= 0.8)
        subhealthy = sum(1 for d in self.documents if 0.5 <= d.health_score < 0.8)
        warning = sum(1 for d in self.documents if 0.3 <= d.health_score < 0.5)
        danger = sum(1 for d in self.documents if d.health_score < 0.3)
        
        hot = sum(1 for d in self.documents if d.hot_level == HotLevel.HOT.value)
        warm = sum(1 for d in self.documents if d.hot_level == HotLevel.WARM.value)
        cold = sum(1 for d in self.documents if d.hot_level == HotLevel.COLD.value)
        
        self.vitals = {
            '全局统计': {
                '文档总数': total,
                '健康文档': healthy,
                '亚健康文档': subhealthy,
                '预警文档': warning,
                '危险文档': danger,
                '热区文档': hot,
                '温区文档': warm,
                '冷区文档': cold
            }
        }
    
    def save(self) -> None:
        """Save changes back to agents.md."""
        self.update_vitals()
        # In a full implementation, this would reconstruct the file
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(self.content)
    
    def add_document(self, metadata: DocMetadata) -> None:
        """Add a new document metadata."""
        self.documents.append(metadata)
    
    def remove_document(self, doc_id: str) -> bool:
        """Remove document metadata by ID."""
        for i, doc in enumerate(self.documents):
            if doc.doc_id == doc_id:
                self.documents.pop(i)
                return True
        return False
