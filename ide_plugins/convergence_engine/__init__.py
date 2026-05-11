"""
Convergence Engine - Visual, controllable ConvergenceAgent for IDE.
"""
import json
import subprocess
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any, Callable
from pathlib import Path
from enum import Enum
import logging

from core.events import EventBus, Event, EventType
from core.decision_ledger import DecisionLedger


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskType(Enum):
    BUG_FIX = "bug_fix"
    TEST_ENHANCE = "test_enhance"


@dataclass
class ConvergenceTask:
    """A task in the convergence queue."""
    id: str
    type: TaskType
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    iterations: int = 0
    error_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IterationResult:
    """Result of a single convergence iteration."""
    iteration: int
    timestamp: datetime
    build_result: Dict[str, Any] = field(default_factory=dict)
    test_result: Dict[str, Any] = field(default_factory=dict)
    fixes_applied: List[str] = field(default_factory=list)
    tests_added: List[str] = field(default_factory=list)
    convergence_score: float = 0.0
    notes: str = ""


@dataclass
class ArbitrationRequest:
    """Request for human arbitration."""
    id: str
    timestamp: datetime
    issue_type: str  # drift_conflict, unclear_requirement, etc.
    involved_docs: List[str] = field(default_factory=list)
    options: List[Dict[str, str]] = field(default_factory=list)  # [{id, description, impact}]
    selected_option: Optional[str] = None
    status: str = "pending"  # pending, resolved
    resolution: str = ""


class TaskPanel:
    """Dual-track task panel for bugs and tests."""
    
    def __init__(self):
        self.track_1: List[ConvergenceTask] = []  # Bug fixes
        self.track_2: List[ConvergenceTask] = []  # Test enhancements
        self._id_counter = 0
    
    def add_task(
        self,
        task_type: TaskType,
        title: str,
        description: str,
        priority: int = 0,
        **metadata
    ) -> str:
        """Add a new task to the appropriate track."""
        self._id_counter += 1
        task_id = f"{'BUG' if task_type == TaskType.BUG_FIX else 'TEST'}-{self._id_counter:04d}"
        
        task = ConvergenceTask(
            id=task_id,
            type=task_type,
            title=title,
            description=description,
            priority=priority,
            metadata=metadata
        )
        
        if task_type == TaskType.BUG_FIX:
            self.track_1.append(task)
        else:
            self.track_2.append(task)
        
        return task_id
    
    def get_task(self, task_id: str) -> Optional[ConvergenceTask]:
        """Get a task by ID."""
        for task in self.track_1 + self.track_2:
            if task.id == task_id:
                return task
        return None
    
    def start_task(self, task_id: str) -> bool:
        """Mark a task as in progress."""
        task = self.get_task(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now()
            return True
        return False
    
    def complete_task(self, task_id: str) -> bool:
        """Mark a task as completed."""
        task = self.get_task(task_id)
        if task and task.status == TaskStatus.IN_PROGRESS:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            return True
        return False
    
    def fail_task(self, task_id: str, error: str = "") -> bool:
        """Mark a task as failed."""
        task = self.get_task(task_id)
        if task and task.status == TaskStatus.IN_PROGRESS:
            task.status = TaskStatus.FAILED
            task.error_count += 1
            task.metadata['last_error'] = error
            return True
        return False
    
    def block_task(self, task_id: str, reason: str) -> bool:
        """Block a task pending arbitration."""
        task = self.get_task(task_id)
        if task:
            task.status = TaskStatus.BLOCKED
            task.metadata['block_reason'] = reason
            return True
        return False
    
    def unblock_task(self, task_id: str) -> bool:
        """Unblock a blocked task."""
        task = self.get_task(task_id)
        if task and task.status == TaskStatus.BLOCKED:
            task.status = TaskStatus.PENDING
            return True
        return False
    
    def get_pending(self) -> Dict[str, List[ConvergenceTask]]:
        """Get all pending tasks by track."""
        return {
            'bugs': [t for t in self.track_1 if t.status == TaskStatus.PENDING],
            'tests': [t for t in self.track_2 if t.status == TaskStatus.PENDING]
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get task panel summary."""
        return {
            'bugs': {
                'total': len(self.track_1),
                'pending': len([t for t in self.track_1 if t.status == TaskStatus.PENDING]),
                'in_progress': len([t for t in self.track_1 if t.status == TaskStatus.IN_PROGRESS]),
                'completed': len([t for t in self.track_1 if t.status == TaskStatus.COMPLETED]),
                'failed': len([t for t in self.track_1 if t.status == TaskStatus.FAILED]),
                'blocked': len([t for t in self.track_1 if t.status == TaskStatus.BLOCKED])
            },
            'tests': {
                'total': len(self.track_2),
                'pending': len([t for t in self.track_2 if t.status == TaskStatus.PENDING]),
                'in_progress': len([t for t in self.track_2 if t.status == TaskStatus.IN_PROGRESS]),
                'completed': len([t for t in self.track_2 if t.status == TaskStatus.COMPLETED]),
                'failed': len([t for t in self.track_2 if t.status == TaskStatus.FAILED]),
                'blocked': len([t for t in self.track_2 if t.status == TaskStatus.BLOCKED])
            }
        }


class IterationHistory:
    """Track iteration history for convergence."""
    
    def __init__(self):
        self.iterations: List[IterationResult] = []
        self._current_task: Optional[str] = None
    
    def start_task_tracking(self, task_id: str) -> None:
        """Start tracking iterations for a task."""
        self._current_task = task_id
        self.iterations = []
    
    def add_iteration(self, result: IterationResult) -> None:
        """Add an iteration result."""
        self.iterations.append(result)
    
    def get_gantt_data(self) -> List[Dict[str, Any]]:
        """Get data for Gantt chart visualization."""
        return [
            {
                'iteration': i.iteration,
                'timestamp': i.timestamp.isoformat(),
                'fixes': len(i.fixes_applied),
                'tests': len(i.tests_added),
                'score': i.convergence_score
            }
            for i in self.iterations
        ]
    
    def get_timeline(self) -> List[Dict[str, Any]]:
        """Get timeline view of iterations."""
        timeline = []
        
        for i, result in enumerate(self.iterations):
            timeline.append({
                'phase': f"Iteration {result.iteration}",
                'start': result.timestamp.isoformat(),
                'end': result.timestamp.isoformat(),  # Simplified
                'details': {
                    'fixes': result.fixes_applied,
                    'tests': result.tests_added,
                    'build': result.build_result.get('success', False),
                    'test_pass': result.test_result.get('passed', False)
                }
            })
        
        return timeline
    
    def get_score_trend(self) -> List[Dict[str, float]]:
        """Get convergence score trend."""
        return [
            {'iteration': i.iteration, 'score': i.convergence_score}
            for i in self.iterations
        ]


class ConvergenceLauncher:
    """One-click convergence launcher."""
    
    def __init__(
        self,
        project_root: str,
        build_cmd: Optional[str] = None,
        test_cmd: Optional[str] = None
    ):
        self.project_root = project_root
        self.build_cmd = build_cmd or "make"
        self.test_cmd = test_cmd or "make test"
        
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: Dict[str, List[Callable]] = {
            'progress': [],
            'result': [],
            'error': []
        }
        self._logger = logging.getLogger(__name__)
    
    def add_callback(self, event: str, callback: Callable) -> None:
        """Add a callback for events."""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    def _emit(self, event: str, data: Any) -> None:
        """Emit an event."""
        for callback in self._callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                self._logger.error(f"Callback error: {e}")
    
    def execute_full_loop(
        self,
        task: ConvergenceTask,
        max_iterations: int = 10,
        convergence_threshold: float = 0.95
    ) -> Dict[str, Any]:
        """Execute full convergence loop."""
        self._running = True
        results = {
            'task_id': task.id,
            'iterations': [],
            'final_score': 0.0,
            'converged': False,
            'success': True
        }
        
        self._emit('progress', {'status': 'started', 'task_id': task.id})
        
        for i in range(max_iterations):
            if not self._running:
                break
            
            iteration_result = IterationResult(
                iteration=i + 1,
                timestamp=datetime.now()
            )
            
            self._emit('progress', {
                'status': 'iteration',
                'iteration': i + 1,
                'total': max_iterations
            })
            
            # Step 1: Build
            build_ok, build_output = self._run_build()
            iteration_result.build_result = {
                'success': build_ok,
                'output': build_output
            }
            
            if not build_ok:
                self._emit('error', {'step': 'build', 'output': build_output})
                self._emit('progress', {'status': 'build_failed'})
                results['success'] = False
                break
            
            # Step 2: Test
            test_ok, test_output = self._run_tests()
            iteration_result.test_result = {
                'success': test_ok,
                'passed': test_output.get('passed', 0),
                'failed': test_output.get('failed', 0)
            }
            
            # Step 3: Convergence check
            score = self._calculate_convergence_score(iteration_result)
            iteration_result.convergence_score = score
            
            results['iterations'].append(iteration_result)
            
            self._emit('progress', {
                'status': 'iteration_complete',
                'iteration': i + 1,
                'score': score
            })
            
            # Check convergence
            if score >= convergence_threshold:
                results['converged'] = True
                results['final_score'] = score
                self._emit('progress', {'status': 'converged', 'score': score})
                break
            
            # Step 4: AI-driven fix
            fixes = self._request_ai_fix(task, iteration_result)
            iteration_result.fixes_applied = fixes
            
            # Step 5: AI-driven test enhancement
            tests = self._request_ai_test_enhancement(task, iteration_result)
            iteration_result.tests_added = tests
        
        self._running = False
        
        if not results['converged']:
            self._emit('progress', {'status': 'max_iterations_reached'})
        
        self._emit('result', results)
        return results
    
    def _run_build(self) -> Tuple[bool, str]:
        """Run build command."""
        try:
            result = subprocess.run(
                self.build_cmd,
                shell=True,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=180
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Build timeout"
        except Exception as e:
            return False, str(e)
    
    def _run_tests(self) -> Tuple[bool, Dict]:
        """Run test command."""
        try:
            result = subprocess.run(
                self.test_cmd,
                shell=True,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            output = result.stdout + result.stderr
            
            # Parse test results (simplified)
            passed = output.count('PASSED') + output.count('passed')
            failed = output.count('FAILED') + output.count('failed')
            
            return result.returncode == 0, {
                'passed': passed,
                'failed': failed,
                'output': output
            }
        except subprocess.TimeoutExpired:
            return False, {'passed': 0, 'failed': 0, 'output': 'Test timeout'}
        except Exception as e:
            return False, {'passed': 0, 'failed': 0, 'output': str(e)}
    
    def _calculate_convergence_score(self, result: IterationResult) -> float:
        """Calculate convergence score (0-1)."""
        score = 0.0
        weight = 0.0
        
        # Build success contributes 30%
        if result.build_result.get('success'):
            score += 0.3
        weight += 0.3
        
        # Test success contributes 40%
        test_result = result.test_result
        if test_result.get('success'):
            score += 0.4
        elif test_result.get('passed', 0) > 0:
            total = test_result.get('passed', 0) + test_result.get('failed', 0)
            if total > 0:
                score += 0.4 * (test_result.get('passed', 0) / total)
        weight += 0.4
        
        # Improvements contribute 30%
        improvements = len(result.fixes_applied) + len(result.tests_added)
        if improvements == 0:
            score += 0.3
        else:
            score += min(0.3, improvements * 0.1)
        weight += 0.3
        
        return score / weight if weight > 0 else 0.0
    
    def _request_ai_fix(self, task: ConvergenceTask, iteration: IterationResult) -> List[str]:
        """Request AI to fix issues (simplified - real impl would call AI)."""
        # In real implementation, this would interface with AI
        fixes = []
        if not iteration.test_result.get('success'):
            fixes.append(f"Auto-fix for {task.title}")
        return fixes
    
    def _request_ai_test_enhancement(self, task: ConvergenceTask, iteration: IterationResult) -> List[str]:
        """Request AI to add tests (simplified - real impl would call AI)."""
        return []
    
    def stop(self) -> None:
        """Stop the running convergence."""
        self._running = False


class ArbitrationInterface:
    """Human arbitration interface for conflicts."""
    
    def __init__(self, decision_ledger: DecisionLedger):
        self.decision_ledger = decision_ledger
        self.pending_requests: List[ArbitrationRequest] = []
        self._id_counter = 0
    
    def create_request(
        self,
        issue_type: str,
        involved_docs: List[str],
        options: List[Dict[str, str]]
    ) -> str:
        """Create an arbitration request."""
        self._id_counter += 1
        req_id = f"ARB-{self._id_counter:04d}"
        
        request = ArbitrationRequest(
            id=req_id,
            timestamp=datetime.now(),
            issue_type=issue_type,
            involved_docs=involved_docs,
            options=options
        )
        
        self.pending_requests.append(request)
        return req_id
    
    def get_request(self, req_id: str) -> Optional[ArbitrationRequest]:
        """Get an arbitration request."""
        for req in self.pending_requests:
            if req.id == req_id:
                return req
        return None
    
    def resolve(
        self,
        req_id: str,
        selected_option: str,
        resolution: str
    ) -> bool:
        """Resolve an arbitration request."""
        for req in self.pending_requests:
            if req.id == req_id:
                req.selected_option = selected_option
                req.resolution = resolution
                req.status = "resolved"
                
                # Add to decision ledger
                self.decision_ledger.add_decision(
                    conflict_type=req.issue_type,
                    involved_docs=req.involved_docs,
                    conflict_description=f"Arbitration: {req.issue_type}",
                    resolution=resolution,
                    resolution_type=selected_option,
                    decision_basis=resolution,
                    decided_by="human"
                )
                
                return True
        return False
    
    def get_pending(self) -> List[ArbitrationRequest]:
        """Get all pending requests."""
        return [r for r in self.pending_requests if r.status == "pending"]


class ConvergenceEngine:
    """Main Convergence Engine controller."""
    
    def __init__(self, project_root: str, config: Optional[Dict] = None):
        self.project_root = project_root
        self.config = config or {}
        
        self.task_panel = TaskPanel()
        self.iteration_history = IterationHistory()
        self.launcher = ConvergenceLauncher(
            project_root,
            build_cmd=self.config.get('build_cmd'),
            test_cmd=self.config.get('test_cmd')
        )
        self.decision_ledger = DecisionLedger(str(Path(project_root) / "docs" / ".decision_ledger"))
        self.arbitration = ArbitrationInterface(self.decision_ledger)
        
        self.event_bus = EventBus()
        self._logger = logging.getLogger(__name__)
        
        self._setup_callbacks()
    
    def _setup_callbacks(self) -> None:
        """Setup event callbacks."""
        self.launcher.add_callback('progress', self._on_progress)
        self.launcher.add_callback('result', self._on_result)
        self.launcher.add_callback('error', self._on_error)
    
    def _on_progress(self, data: Dict) -> None:
        """Handle progress event."""
        status = data.get('status')
        
        if status == 'started':
            self.event_bus.publish(Event(
                type=EventType.CONVERGENCE_STARTED,
                source="convergence_engine",
                data=data
            ))
        elif 'iteration' in status:
            self.event_bus.publish(Event(
                type=EventType.CONVERGENCE_ITERATION,
                source="convergence_engine",
                data=data
            ))
        elif status == 'converged':
            self.event_bus.publish(Event(
                type=EventType.CONVERGENCE_COMPLETED,
                source="convergence_engine",
                data=data
            ))
    
    def _on_result(self, data: Dict) -> None:
        """Handle result event."""
        self._logger.info(f"Convergence result: {data}")
    
    def _on_error(self, data: Dict) -> None:
        """Handle error event."""
        self.event_bus.publish(Event(
            type=EventType.CONVERGENCE_FAILED,
            source="convergence_engine",
            data=data
        ))
    
    def add_bug_task(self, title: str, description: str, priority: int = 0) -> str:
        """Add a bug fix task."""
        return self.task_panel.add_task(
            TaskType.BUG_FIX,
            title,
            description,
            priority
        )
    
    def add_test_task(self, title: str, description: str, priority: int = 0) -> str:
        """Add a test enhancement task."""
        return self.task_panel.add_task(
            TaskType.TEST_ENHANCE,
            title,
            description,
            priority
        )
    
    def start_convergence(
        self,
        task_id: str,
        max_iterations: Optional[int] = None,
        convergence_threshold: Optional[float] = None
    ) -> Dict:
        """Start convergence for a task."""
        task = self.task_panel.get_task(task_id)
        if not task:
            return {'success': False, 'error': 'Task not found'}
        
        max_iterations = max_iterations or self.config.get('max_iterations', 10)
        convergence_threshold = convergence_threshold or self.config.get('convergence_threshold', 0.95)
        
        self.task_panel.start_task(task_id)
        self.iteration_history.start_task_tracking(task_id)
        
        result = self.launcher.execute_full_loop(
            task,
            max_iterations=max_iterations,
            convergence_threshold=convergence_threshold
        )
        
        if result.get('converged'):
            self.task_panel.complete_task(task_id)
        else:
            self.task_panel.fail_task(task_id)
        
        return result
    
    def request_arbitration(
        self,
        task_id: str,
        issue_type: str,
        involved_docs: List[str],
        options: List[Dict[str, str]]
    ) -> str:
        """Request arbitration for a conflict."""
        req_id = self.arbitration.create_request(issue_type, involved_docs, options)
        
        self.task_panel.block_task(task_id, f"Pending arbitration: {req_id}")
        
        self.event_bus.publish(Event(
            type=EventType.ARBITRATION_REQUIRED,
            source="convergence_engine",
            data={'task_id': task_id, 'request_id': req_id}
        ))
        
        return req_id
    
    def submit_arbitration(
        self,
        req_id: str,
        selected_option: str,
        resolution: str
    ) -> bool:
        """Submit arbitration decision."""
        success = self.arbitration.resolve(req_id, selected_option, resolution)
        
        if success:
            # Find and unblock the related task
            request = self.arbitration.get_request(req_id)
            for task in self.task_panel.track_1 + self.task_panel.track_2:
                if task.status == TaskStatus.BLOCKED:
                    reason = task.metadata.get('block_reason', '')
                    if req_id in reason:
                        self.task_panel.unblock_task(task.id)
                        break
        
        return success
    
    def get_status(self) -> Dict[str, Any]:
        """Get convergence engine status."""
        return {
            'tasks': self.task_panel.get_summary(),
            'iterations': len(self.iteration_history.iterations),
            'pending_arbitrations': len(self.arbitration.get_pending()),
            'score_trend': self.iteration_history.get_score_trend()
        }
    
    def export_report(self) -> Dict[str, Any]:
        """Export convergence report."""
        return {
            'timestamp': datetime.now().isoformat(),
            'tasks': self.task_panel.get_summary(),
            'iterations': self.iteration_history.get_gantt_data(),
            'timeline': self.iteration_history.get_timeline(),
            'score_trend': self.iteration_history.get_score_trend(),
            'arbitrations': [
                {
                    'id': r.id,
                    'type': r.issue_type,
                    'status': r.status,
                    'resolution': r.resolution
                }
                for r in self.arbitration.pending_requests
            ]
        }
