"""
Law Manager - Interactive Law Network for agents.md and specifications.
"""
import os
import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from pathlib import Path
from datetime import datetime

from core.agents_md import AgentsMD, DocMetadata
from core.decision_ledger import DecisionLedger
from core.events import EventBus, Event, EventType


@dataclass
class LawNode:
    """A node in the law tree."""
    id: str
    title: str
    type: str  # law, spec, decision, folder
    path: str = ""
    parent_id: str = ""
    children: List['LawNode'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    violations: List[Dict] = field(default_factory=list)
    linked_code: List[str] = field(default_factory=list)
    decision_refs: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'path': self.path,
            'parent_id': self.parent_id,
            'children': [c.to_dict() for c in self.children],
            'metadata': self.metadata,
            'violations': self.violations,
            'linked_code': self.linked_code,
            'decision_refs': self.decision_refs
        }


@dataclass
class Violation:
    """A rule violation."""
    law_id: str
    file_path: str
    line_number: int
    severity: str  # error, warning, info
    message: str
    code_snippet: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    auto_fixed: bool = False


class LawValidator:
    """Automatic rule validation engine."""
    
    def __init__(self):
        self.rules: List[Dict[str, Any]] = []
        self._load_default_rules()
    
    def _load_default_rules(self):
        """Load default validation rules."""
        self.rules = [
            {
                'id': 'R001',
                'name': 'ISR No Blocking',
                'pattern': r'HAL_Delay|delay_ms|osDelay',
                'in_context': r'^(void\s+\w*ISR|void\s+\w*_Handler)\(',
                'severity': 'error',
                'message': 'Blocking calls are not allowed in ISR context'
            },
            {
                'id': 'R002',
                'name': 'Thread Safety',
                'pattern': r'global_\w+|shared_\w+',
                'check': 'mutex_usage',
                'severity': 'warning',
                'message': 'Global/shared variable accessed, ensure thread safety'
            }
        ]
    
    def add_rule(self, rule: Dict[str, Any]) -> None:
        """Add a new validation rule."""
        self.rules.append(rule)
    
    def validate_file(self, file_path: str, content: str) -> List[Violation]:
        """Validate a file against all rules."""
        violations = []
        lines = content.split('\n')
        
        for rule in self.rules:
            if 'pattern' not in rule:
                continue
            
            pattern = re.compile(rule['pattern'])
            
            for i, line in enumerate(lines, 1):
                if pattern.search(line):
                    # Check context if specified
                    if 'in_context' in rule:
                        context_pattern = re.compile(rule['in_context'])
                        # Look at surrounding lines
                        context_start = max(0, i - 10)
                        context = '\n'.join(lines[context_start:i])
                        if context_pattern.search(context):
                            violations.append(Violation(
                                law_id=rule['id'],
                                file_path=file_path,
                                line_number=i,
                                severity=rule['severity'],
                                message=rule['message'],
                                code_snippet=line.strip()
                            ))
                    else:
                        violations.append(Violation(
                            law_id=rule['id'],
                            file_path=file_path,
                            line_number=i,
                            severity=rule['severity'],
                            message=rule['message'],
                            code_snippet=line.strip()
                        ))
        
        return violations


class LawCreator:
    """Wizard for creating new laws/specifications."""
    
    def __init__(self, agents_md_path: str):
        self.agents_md_path = agents_md_path
        self.templates: Dict[str, str] = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load law creation templates."""
        return {
            'hardware_constraint': """---
doc_id: {doc_id}
title: "{title}"
created: {date}
last_modified: {date}
health_score: 1.0
status: healthy
hot_level: warm
wake_keywords:
  hardware: [{keywords}]
linked_docs: []
drift_history: []
---

# {title}

## 约束描述
{description}

## 适用场景
{applicability}

## 验证方法
{validation_method}

## 相关文档
- 
""",
            'coding_standard': """---
doc_id: {doc_id}
title: "{title}"
created: {date}
last_modified: {date}
health_score: 1.0
status: healthy
hot_level: hot
wake_keywords:
  modules: [{keywords}]
linked_docs: []
drift_history: []
---

# {title}

## 规则描述
{rule_description}

## 代码示例

### ✅ 合规示例
```c
// 
```

### ❌ 不合规示例
```c
// 
```

## 检查脚本
```bash
# 
```
""",
            'design_decision': """---
doc_id: {doc_id}
title: "{title}"
created: {date}
last_modified: {date}
health_score: 1.0
status: healthy
hot_level: warm
wake_keywords:
  modules: [{keywords}]
linked_docs: [{linked_docs}]
drift_history: []
---

# {title}

## 决策背景
{background}

## 决策选项
### 选项A
{description_a}

### 选项B
{description_b}

## 最终决策
{final_decision}

## 决策依据
{basis}
"""
        }
    
    def create_law(
        self,
        law_type: str,
        title: str,
        **kwargs
    ) -> str:
        """Create a new law/specification document."""
        if law_type not in self.templates:
            raise ValueError(f"Unknown law type: {law_type}")
        
        template = self.templates[law_type]
        doc_id = kwargs.get('doc_id', self._generate_doc_id())
        
        content = template.format(
            doc_id=doc_id,
            title=title,
            date=datetime.now().strftime("%Y-%m-%d"),
            keywords=kwargs.get('keywords', ''),
            description=kwargs.get('description', ''),
            applicability=kwargs.get('applicability', ''),
            validation_method=kwargs.get('validation_method', ''),
            rule_description=kwargs.get('rule_description', ''),
            background=kwargs.get('background', ''),
            description_a=kwargs.get('description_a', ''),
            description_b=kwargs.get('description_b', ''),
            final_decision=kwargs.get('final_decision', ''),
            basis=kwargs.get('basis', ''),
            linked_docs=kwargs.get('linked_docs', '')
        )
        
        # Save to file
        filename = f"{doc_id}.md"
        filepath = os.path.join(os.path.dirname(self.agents_md_path), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def _generate_doc_id(self) -> str:
        """Generate a unique document ID."""
        import random
        import string
        prefix = datetime.now().strftime("%Y%m%d")
        suffix = ''.join(random.choices(string.ascii_uppercase, k=3))
        return f"SPEC-{prefix}-{suffix}"
    
    def generate_check_script(self, law_id: str, rule_content: str) -> str:
        """Generate a check script for a law."""
        script = f"""#!/bin/bash
# Auto-generated check script for {law_id}

echo "Checking {law_id}..."

# Add your validation logic here
# Return non-zero if violation found

exit 0
"""
        return script


class LawManager:
    """Main Law Manager controller."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.agents_md_path = self.project_root / "docs" / "agents.md"
        self.agents_md = AgentsMD(str(self.agents_md_path)) if self.agents_md_path.exists() else None
        self.decision_ledger = DecisionLedger(str(self.project_root / "docs" / ".decision_ledger"))
        self.validator = LawValidator()
        self.creator = LawCreator(str(self.agents_md_path)) if self.agents_md_path.exists() else None
        self.event_bus = EventBus()
        
        self.law_tree: List[LawNode] = []
        self.current_violations: List[Violation] = []
        
        if self.agents_md:
            self._build_law_tree()
    
    def _build_law_tree(self) -> None:
        """Build the law tree from agents.md and specs directory."""
        self.law_tree = []
        
        # Root node
        root = LawNode(
            id="root",
            title="法则网络",
            type="folder"
        )
        
        # Add agents.md as central hub
        agents_node = LawNode(
            id="agents_md",
            title="中央索引",
            type="folder",
            path=str(self.agents_md_path),
            parent_id="root"
        )
        root.children.append(agents_node)
        
        # Add specifications
        specs_dir = self.project_root / "docs" / "specs"
        if specs_dir.exists():
            specs_node = LawNode(
                id="specs",
                title="规约文档",
                type="folder",
                parent_id="root"
            )
            
            for spec_file in specs_dir.glob("*.md"):
                spec_node = LawNode(
                    id=spec_file.stem,
                    title=spec_file.stem,
                    type="spec",
                    path=str(spec_file),
                    parent_id="specs"
                )
                specs_node.children.append(spec_node)
            
            root.children.append(specs_node)
        
        # Add decision ledger
        decisions_node = LawNode(
            id="decisions",
            title="决策账本",
            type="folder",
            parent_id="root"
        )
        
        for decision in self.decision_ledger.get_active_decisions()[:20]:
            decision_node = LawNode(
                id=decision.decision_id,
                title=f"{decision.decision_id}: {decision.conflict_type}",
                type="decision",
                metadata={'date': decision.date, 'status': decision.status}
            )
            decisions_node.children.append(decision_node)
        
        root.children.append(decisions_node)
        self.law_tree.append(root)
    
    def validate_code(self, file_path: str, content: str) -> List[Violation]:
        """Validate code against all rules."""
        violations = self.validator.validate_file(file_path, content)
        self.current_violations = violations
        
        # Publish events
        for v in violations:
            self.event_bus.publish(Event(
                type=EventType.RISK_DETECTED,
                source="law_manager",
                data={
                    'law_id': v.law_id,
                    'file': v.file_path,
                    'line': v.line_number,
                    'severity': v.severity,
                    'message': v.message
                }
            ))
        
        return violations
    
    def create_spec(
        self,
        spec_type: str,
        title: str,
        **kwargs
    ) -> Optional[str]:
        """Create a new specification via wizard."""
        if not self.creator:
            return None
        
        filepath = self.creator.create_law(spec_type, title, **kwargs)
        
        # Rebuild tree
        self._build_law_tree()
        
        # Publish event
        self.event_bus.publish(Event(
            type=EventType.DOC_CREATED,
            source="law_manager",
            data={'path': filepath, 'title': title}
        ))
        
        return filepath
    
    def get_law_context(self, law_id: str) -> Dict[str, Any]:
        """Get full context for a law including linked code and decisions."""
        context = {
            'law': None,
            'linked_code': [],
            'decisions': [],
            'violations': []
        }
        
        # Find the law
        for node in self._flatten_tree(self.law_tree):
            if node.id == law_id:
                context['law'] = node.to_dict()
                break
        
        # Get violations
        context['violations'] = [
            v.__dict__ for v in self.current_violations
            if v.law_id == law_id
        ]
        
        # Get related decisions
        context['decisions'] = [
            d.to_dict() for d in self.decision_ledger.get_decisions_for_doc(law_id)
        ]
        
        return context
    
    def _flatten_tree(self, nodes: List[LawNode]) -> List[LawNode]:
        """Flatten tree to list."""
        result = []
        for node in nodes:
            result.append(node)
            result.extend(self._flatten_tree(node.children))
        return result
    
    def export_tree_json(self) -> str:
        """Export law tree as JSON."""
        return json.dumps([n.to_dict() for n in self.law_tree], ensure_ascii=False, indent=2)
