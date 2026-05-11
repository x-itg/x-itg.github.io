"""
Knowledge Vitals Dashboard - Real-time document health monitoring.
"""
import os
import time
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Callable
from pathlib import Path
import logging

from core.agents_md import AgentsMD, DocMetadata, DocHealthDetail, HotLevel, HealthStatus
from core.events import EventBus, Event, EventType


@dataclass
class HealthAlert:
    """A health alert."""
    id: str
    doc_id: str
    alert_type: str  # threshold_breach, cold_warning, drift_detected
    severity: str    # critical, warning, info
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False


class Dashboard:
    """Global knowledge vitals overview dashboard."""
    
    def __init__(self):
        self.total_documents: int = 0
        self.healthy_count: int = 0
        self.subhealthy_count: int = 0
        self.warning_count: int = 0
        self.danger_count: int = 0
        
        self.hot_count: int = 0
        self.warm_count: int = 0
        self.cold_count: int = 0
        
        self.recent_alerts: List[HealthAlert] = []
        self.drift_events: List[Dict] = []
    
    def update(self, agents_md: AgentsMD) -> None:
        """Update dashboard from agents.md."""
        self.total_documents = len(agents_md.documents)
        
        self.healthy_count = sum(1 for d in agents_md.documents if d.health_score >= 0.8)
        self.subhealthy_count = sum(1 for d in agents_md.documents if 0.5 <= d.health_score < 0.8)
        self.warning_count = sum(1 for d in agents_md.documents if 0.3 <= d.health_score < 0.5)
        self.danger_count = sum(1 for d in agents_md.documents if d.health_score < 0.3)
        
        self.hot_count = sum(1 for d in agents_md.documents if d.hot_level == HotLevel.HOT.value)
        self.warm_count = sum(1 for d in agents_md.documents if d.hot_level == HotLevel.WARM.value)
        self.cold_count = sum(1 for d in agents_md.documents if d.hot_level == HotLevel.COLD.value)
    
    def get_ring_chart_data(self) -> List[Dict[str, Any]]:
        """Get data for health ring chart."""
        return [
            {'name': '健康', 'value': self.healthy_count, 'color': '#22c55e'},
            {'name': '亚健康', 'value': self.subhealthy_count, 'color': '#f59e0b'},
            {'name': '预警', 'value': self.warning_count, 'color': '#f97316'},
            {'name': '危险', 'value': self.danger_count, 'color': '#ef4444'}
        ]
    
    def get_heatmap_data(self, agents_md: AgentsMD) -> List[Dict[str, Any]]:
        """Get data for activity heatmap."""
        heatmap = []
        
        for doc in agents_md.documents:
            # Calculate activity score (combination of hot_level and reference_count)
            hot_score = {'hot': 3, 'warm': 2, 'cold': 1}.get(doc.hot_level, 0)
            activity = hot_score + min(doc.reference_count / 10, 2)
            
            heatmap.append({
                'doc_id': doc.doc_id,
                'title': doc.title,
                'activity': activity,
                'health': doc.health_score,
                'hot_level': doc.hot_level
            })
        
        return sorted(heatmap, key=lambda x: x['activity'], reverse=True)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get dashboard summary."""
        return {
            'total_documents': self.total_documents,
            'health_distribution': {
                'healthy': self.healthy_count,
                'subhealthy': self.subhealthy_count,
                'warning': self.warning_count,
                'danger': self.danger_count
            },
            'activity_distribution': {
                'hot': self.hot_count,
                'warm': self.warm_count,
                'cold': self.cold_count
            },
            'recent_alerts': len(self.recent_alerts),
            'drift_events': len(self.drift_events)
        }


class DocumentPanel:
    """Detailed view for a single document."""
    
    def __init__(self, doc: DocMetadata):
        self.doc = doc
    
    def get_health_scores(self) -> Dict[str, float]:
        """Get four-dimension health scores."""
        return {
            'code_consistency': self.doc.health_detail.code_consistency,
            'physical_consistency': self.doc.health_detail.physical_consistency,
            'freshness': self.doc.health_detail.freshness,
            'reference_integrity': self.doc.health_detail.reference_integrity
        }
    
    def get_health_bar_data(self) -> List[Dict[str, Any]]:
        """Get health bar chart data."""
        scores = self.get_health_scores()
        return [
            {'dimension': '代码一致性', 'score': scores['code_consistency']},
            {'dimension': '物理一致性', 'score': scores['physical_consistency']},
            {'dimension': '时间新鲜度', 'score': scores['freshness']},
            {'dimension': '引用完整性', 'score': scores['reference_integrity']}
        ]
    
    def get_reference_history(self) -> List[Dict[str, Any]]:
        """Get reference count history (simulated)."""
        # In real implementation, this would query historical data
        history = []
        base_count = max(0, self.doc.reference_count - 10)
        
        for i in range(10):
            history.append({
                'date': (datetime.now() - timedelta(days=9-i)).strftime('%Y-%m-%d'),
                'count': base_count + i
            })
        
        return history
    
    def get_wake_records(self) -> List[Dict[str, Any]]:
        """Get recent wake records."""
        # In real implementation, this would query wake log
        return [
            {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'keyword': kw,
                'triggered': True
            }
            for kw_list in self.doc.wake_keywords.values()
            for kw in kw_list[:3]
        ]
    
    def get_drift_history(self) -> List[Dict[str, Any]]:
        """Get drift history."""
        return self.doc.drift_history


class AlertManager:
    """Manage health alerts."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        thresholds = self.config.get('health_thresholds', {})
        self.healthy_threshold = thresholds.get('healthy', 0.8)
        self.warning_threshold = thresholds.get('warning', 0.5)
        self.danger_threshold = thresholds.get('danger', 0.3)
        self.cold_document_days = self.config.get('cold_document_days', 180)
        
        self.alerts: List[HealthAlert] = []
        self._id_counter = 0
    
    def check_document(self, doc: DocMetadata) -> Optional[HealthAlert]:
        """Check a document and generate alert if needed."""
        alert = None
        
        # Health threshold breach
        if doc.health_score < self.danger_threshold:
            alert = HealthAlert(
                id=self._next_id(),
                doc_id=doc.doc_id,
                alert_type='threshold_breach',
                severity='critical',
                message=f"{doc.title} 健康度骤降至 {doc.health_score:.2f}，建议立即检查"
            )
        elif doc.health_score < self.warning_threshold:
            alert = HealthAlert(
                id=self._next_id(),
                doc_id=doc.doc_id,
                alert_type='threshold_breach',
                severity='warning',
                message=f"{doc.title} 健康度为 {doc.health_score:.2f}，需要注意"
            )
        
        # Cold document warning (hot/warm document not referenced recently)
        if doc.hot_level in ['hot', 'warm']:
            last_ref = self._parse_date(doc.last_referenced)
            if last_ref and (datetime.now() - last_ref).days > self.cold_document_days:
                alert = HealthAlert(
                    id=self._next_id(),
                    doc_id=doc.doc_id,
                    alert_type='cold_warning',
                    severity='info',
                    message=f"{doc.title} 长时间未被引用，可能即将冷却"
                )
        
        if alert:
            self.alerts.append(alert)
            return alert
        
        return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return None
    
    def _next_id(self) -> str:
        """Generate next alert ID."""
        self._id_counter += 1
        return f"ALERT-{self._id_counter:04d}"
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                return True
        return False
    
    def get_active_alerts(self) -> List[HealthAlert]:
        """Get all unacknowledged alerts."""
        return [a for a in self.alerts if not a.acknowledged]
    
    def get_alerts_by_doc(self, doc_id: str) -> List[HealthAlert]:
        """Get all alerts for a document."""
        return [a for a in self.alerts if a.doc_id == doc_id]
    
    def clear_old_alerts(self, days: int = 30) -> int:
        """Clear alerts older than specified days."""
        cutoff = datetime.now() - timedelta(days=days)
        old_count = len([a for a in self.alerts if a.timestamp < cutoff])
        self.alerts = [a for a in self.alerts if a.timestamp >= cutoff]
        return old_count


class FactSearch:
    """Search fact index for authoritative sources."""
    
    def __init__(self, agents_md: AgentsMD):
        self.agents_md = agents_md
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for facts matching query."""
        results = []
        query_lower = query.lower()
        
        # Search in fact index
        for fact, source in self.agents_md.fact_index.items():
            if query_lower in fact.lower():
                results.append({
                    'fact': fact,
                    'authoritative_source': source,
                    'match_type': 'exact'
                })
        
        # Search in document titles
        for doc in self.agents_md.documents:
            if query_lower in doc.title.lower():
                results.append({
                    'fact': f"{doc.doc_id}: {doc.title}",
                    'authoritative_source': doc.doc_id,
                    'health': doc.health_score,
                    'match_type': 'document'
                })
        
        # Search in wake keywords
        for doc in self.agents_md.documents:
            for category, keywords in doc.wake_keywords.items():
                for kw in keywords:
                    if query_lower in kw.lower():
                        results.append({
                            'fact': kw,
                            'document': doc.doc_id,
                            'category': category,
                            'health': doc.health_score,
                            'match_type': 'keyword'
                        })
        
        return results
    
    def get_authoritative_source(self, fact: str) -> Optional[str]:
        """Get authoritative source for a fact."""
        return self.agents_md.fact_index.get(fact)


class VitalsMonitor:
    """Background monitor for knowledge vitals."""
    
    def __init__(
        self,
        agents_md_path: str,
        config: Optional[Dict] = None,
        check_interval: int = 3600
    ):
        self.agents_md_path = agents_md_path
        self.config = config or {}
        self.check_interval = check_interval
        
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable] = []
        
        self.event_bus = EventBus()
        self._logger = logging.getLogger(__name__)
    
    def add_callback(self, callback: Callable) -> None:
        """Add a callback for vitals updates."""
        self._callbacks.append(callback)
    
    def start(self) -> None:
        """Start monitoring."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        self._logger.info("Vitals monitor started")
    
    def stop(self) -> None:
        """Stop monitoring."""
        self._running = False
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                self._check_vitals()
            except Exception as e:
                self._logger.error(f"Vitals check failed: {e}")
            
            time.sleep(self.check_interval)
    
    def _check_vitals(self) -> None:
        """Perform vitals check."""
        agents_md = AgentsMD(self.agents_md_path)
        
        # Check for alerts
        alert_manager = AlertManager(self.config.get('knowledge_vitals', {}))
        
        for doc in agents_md.documents:
            alert = alert_manager.check_document(doc)
            if alert:
                self.event_bus.publish(Event(
                    type=EventType.HEALTH_ALERT,
                    source="vitals_monitor",
                    data={
                        'doc_id': doc.doc_id,
                        'alert_type': alert.alert_type,
                        'severity': alert.severity,
                        'message': alert.message
                    }
                ))
        
        # Publish update
        self.event_bus.publish(Event(
            type=EventType.VITALS_UPDATED,
            source="vitals_monitor",
            data={'timestamp': datetime.now().isoformat()}
        ))
        
        # Call callbacks
        for callback in self._callbacks:
            try:
                callback(agents_md)
            except Exception as e:
                self._logger.error(f"Callback error: {e}")


class KnowledgeVitalsDashboard:
    """Main Knowledge Vitals Dashboard controller."""
    
    def __init__(self, project_root: str, config: Optional[Dict] = None):
        self.project_root = Path(project_root)
        self.config = config or {}
        
        agents_md_path = self.project_root / self.config.get('agents_md', 'docs/agents.md')
        self.agents_md = AgentsMD(str(agents_md_path)) if agents_md_path.exists() else None
        
        self.dashboard = Dashboard()
        self.alert_manager = AlertManager(self.config.get('knowledge_vitals', {}))
        self.fact_search = FactSearch(self.agents_md) if self.agents_md else None
        
        vitals_config = self.config.get('knowledge_vitals', {})
        self.monitor = VitalsMonitor(
            str(agents_md_path),
            self.config,
            check_interval=vitals_config.get('check_interval', 3600)
        )
        
        self.event_bus = EventBus()
        self._logger = logging.getLogger(__name__)
        
        if self.agents_md:
            self._refresh()
    
    def _refresh(self) -> None:
        """Refresh dashboard data."""
        if self.agents_md:
            self.agents_md.load()
            self.dashboard.update(self.agents_md)
            self.fact_search = FactSearch(self.agents_md)
    
    def get_overview(self) -> Dict[str, Any]:
        """Get dashboard overview."""
        self._refresh()
        
        return {
            'summary': self.dashboard.get_summary(),
            'ring_chart': self.dashboard.get_ring_chart_data(),
            'heatmap': self.dashboard.get_heatmap_data(self.agents_md) if self.agents_md else [],
            'alerts': [
                {
                    'id': a.id,
                    'doc_id': a.doc_id,
                    'type': a.alert_type,
                    'severity': a.severity,
                    'message': a.message,
                    'timestamp': a.timestamp.isoformat()
                }
                for a in self.alert_manager.get_active_alerts()
            ]
        }
    
    def get_document_details(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a document."""
        self._refresh()
        
        if not self.agents_md:
            return None
        
        doc = self.agents_md.get_document(doc_id)
        if not doc:
            return None
        
        panel = DocumentPanel(doc)
        
        return {
            'metadata': {
                'doc_id': doc.doc_id,
                'title': doc.title,
                'created': doc.created,
                'last_modified': doc.last_modified,
                'reference_count': doc.reference_count,
                'modification_count': doc.modification_count,
                'status': doc.status,
                'hot_level': doc.hot_level
            },
            'health_scores': panel.get_health_bar_data(),
            'reference_history': panel.get_reference_history(),
            'wake_records': panel.get_wake_records(),
            'drift_history': panel.get_drift_history(),
            'alerts': [
                {
                    'id': a.id,
                    'severity': a.severity,
                    'message': a.message,
                    'acknowledged': a.acknowledged
                }
                for a in self.alert_manager.get_alerts_by_doc(doc_id)
            ]
        }
    
    def search_facts(self, query: str) -> List[Dict[str, Any]]:
        """Search for facts."""
        if self.fact_search:
            return self.fact_search.search(query)
        return []
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        return self.alert_manager.acknowledge_alert(alert_id)
    
    def start_monitoring(self) -> None:
        """Start background monitoring."""
        self.monitor.add_callback(lambda md: self._refresh())
        self.monitor.start()
    
    def stop_monitoring(self) -> None:
        """Stop background monitoring."""
        self.monitor.stop()
    
    def get_unhealthy_hot_documents(self) -> List[Dict[str, Any]]:
        """Get documents that are hot but unhealthy (high risk)."""
        self._refresh()
        
        if not self.agents_md:
            return []
        
        results = []
        
        for doc in self.agents_md.documents:
            if doc.hot_level == HotLevel.HOT.value and doc.health_score < 0.5:
                results.append({
                    'doc_id': doc.doc_id,
                    'title': doc.title,
                    'health_score': doc.health_score,
                    'risk': 'high_risk'
                })
        
        return sorted(results, key=lambda x: x['health_score'])
