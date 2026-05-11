"""
Decision ledger module for tracking knowledge conflicts and resolutions.
"""
import os
import json
import yaml
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path


@dataclass
class DecisionRecord:
    """A single decision record in the ledger."""
    decision_id: str
    date: str
    conflict_type: str  # code_drift, physical_drift, fact_drift
    involved_docs: List[str] = field(default_factory=list)
    conflict_description: str = ""
    resolution: str = ""
    resolution_type: str = ""  # accept_doc_a, merge, create_new
    decision_basis: str = ""
    decided_by: str = ""  # human, ai, auto
    status: str = "active"  # active, superseded
    superseded_by: str = ""
    drift_history_refs: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DecisionRecord':
        """Create from dictionary."""
        return cls(**data)
    
    def is_superseded(self) -> bool:
        """Check if this decision has been superseded."""
        return self.status == "superseded" and self.superseded_by


class DecisionLedger:
    """Manages the decision ledger for tracking knowledge conflicts."""
    
    def __init__(self, ledger_dir: str = "docs/.decision_ledger/"):
        self.ledger_dir = Path(ledger_dir)
        self.ledger_dir.mkdir(parents=True, exist_ok=True)
        self.ledger_file = self.ledger_dir / "decisions.json"
        self.decisions: List[DecisionRecord] = []
        self._load()
    
    def _load(self) -> None:
        """Load decisions from file."""
        if self.ledger_file.exists():
            try:
                with open(self.ledger_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.decisions = [DecisionRecord.from_dict(d) for d in data]
            except (json.JSONDecodeError, TypeError):
                self.decisions = []
    
    def _save(self) -> None:
        """Save decisions to file."""
        data = [d.to_dict() for d in self.decisions]
        with open(self.ledger_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _generate_id(self) -> str:
        """Generate a unique decision ID."""
        year = datetime.now().year
        count = len([d for d in self.decisions if d.decision_id.startswith(f"DECISION-{year}")]) + 1
        return f"DECISION-{year}-{count:03d}"
    
    def add_decision(
        self,
        conflict_type: str,
        involved_docs: List[str],
        conflict_description: str,
        resolution: str,
        resolution_type: str = "",
        decision_basis: str = "",
        decided_by: str = "human"
    ) -> DecisionRecord:
        """Add a new decision record."""
        record = DecisionRecord(
            decision_id=self._generate_id(),
            date=datetime.now().strftime("%Y-%m-%d"),
            conflict_type=conflict_type,
            involved_docs=involved_docs,
            conflict_description=conflict_description,
            resolution=resolution,
            resolution_type=resolution_type,
            decision_basis=decision_basis,
            decided_by=decided_by
        )
        self.decisions.append(record)
        self._save()
        return record
    
    def get_decision(self, decision_id: str) -> Optional[DecisionRecord]:
        """Get a specific decision by ID."""
        for decision in self.decisions:
            if decision.decision_id == decision_id:
                return decision
        return None
    
    def get_decisions_for_doc(self, doc_id: str) -> List[DecisionRecord]:
        """Get all decisions involving a specific document."""
        return [
            d for d in self.decisions
            if doc_id in d.involved_docs
        ]
    
    def get_decisions_by_type(self, conflict_type: str) -> List[DecisionRecord]:
        """Get all decisions of a specific type."""
        return [d for d in self.decisions if d.conflict_type == conflict_type]
    
    def get_active_decisions(self) -> List[DecisionRecord]:
        """Get all active (non-superseded) decisions."""
        return [d for d in self.decisions if not d.is_superseded()]
    
    def supersede_decision(self, decision_id: str, superseded_by_id: str) -> bool:
        """Mark a decision as superseded by another."""
        for decision in self.decisions:
            if decision.decision_id == decision_id:
                decision.status = "superseded"
                decision.superseded_by = superseded_by_id
                self._save()
                return True
        return False
    
    def search_decisions(self, query: str) -> List[DecisionRecord]:
        """Search decisions by keyword."""
        results = []
        query_lower = query.lower()
        
        for decision in self.decisions:
            if (query_lower in decision.conflict_description.lower() or
                query_lower in decision.resolution.lower() or
                any(query_lower in doc.lower() for doc in decision.involved_docs)):
                results.append(decision)
        
        return results
    
    def get_conflict_patterns(self) -> Dict[str, int]:
        """Analyze and count conflict patterns."""
        patterns = {}
        for decision in self.decisions:
            pattern = decision.conflict_type
            patterns[pattern] = patterns.get(pattern, 0) + 1
        return patterns
    
    def get_immunity_learned(self, doc_id: str) -> List[Dict[str, Any]]:
        """Get learned immunity patterns for a document."""
        immunity = []
        for decision in self.decisions:
            if doc_id in decision.involved_docs:
                immunity.append({
                    'pattern': decision.conflict_type,
                    'resolution': decision.resolution,
                    'basis': decision.decision_basis,
                    'date': decision.date
                })
        return immunity
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a summary report of all decisions."""
        return {
            'total_decisions': len(self.decisions),
            'active_decisions': len(self.get_active_decisions()),
            'superseded_decisions': len([d for d in self.decisions if d.is_superseded()]),
            'by_type': self.get_conflict_patterns(),
            'by_decider': {
                'human': len([d for d in self.decisions if d.decided_by == 'human']),
                'ai': len([d for d in self.decisions if d.decided_by == 'ai']),
                'auto': len([d for d in self.decisions if d.decided_by == 'auto'])
            },
            'recent_decisions': [
                asdict(d) for d in sorted(
                    self.decisions,
                    key=lambda x: x.date,
                    reverse=True
                )[:10]
            ]
        }
    
    def export_yaml(self, output_path: str) -> None:
        """Export decisions to YAML format."""
        data = [d.to_dict() for d in self.decisions]
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
