"""
Negative Logger - Runtime visualization of expectation vs reality gap.
"""
import re
import time
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any, Callable, Tuple
from dataclasses import asdict
from enum import Enum
import logging

from core.events import EventBus, Event, EventType


class LogType(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class LogEntry:
    """A single log entry."""
    timestamp: datetime
    type: LogType
    category: str
    message: str
    raw: str
    parsed_data: Dict[str, Any] = field(default_factory=dict)
    source: str = "serial"


@dataclass
class Expectation:
    """An expected event."""
    id: str
    event_name: str
    timeout_seconds: float
    start_time: datetime
    status: str = "pending"  # pending, triggered, timeout, cancelled
    triggered_at: Optional[datetime] = None
    actual_value: Any = None
    expected_value: Any = None
    
    @property
    def elapsed(self) -> float:
        return (datetime.now() - self.start_time).total_seconds()
    
    @property
    def remaining(self) -> float:
        return max(0, self.timeout_seconds - self.elapsed)
    
    @property
    def is_timeout(self) -> bool:
        return self.status == "pending" and self.remaining <= 0


class LogParser:
    """Parse structured logs."""
    
    POSITIVE_PATTERN = re.compile(r'\[POSITIVE\]\[(\w+)\]\s*(.+)')
    NEGATIVE_PATTERN = re.compile(r'\[NEGATIVE\]\[(\w+)\]\s*(.+)')
    EXPECT_PATTERN = re.compile(r'EXPECT_WITHIN\[(\w+)\]\[(\d+(?:\.\d+)?)\]\s*(.+)')
    METRIC_PATTERN = re.compile(r'\[METRIC\]\[(\w+)\]\s*=\s*([\d.]+)')
    
    @classmethod
    def parse_line(cls, line: str) -> Optional[LogEntry]:
        """Parse a single log line."""
        timestamp = datetime.now()
        
        # Check positive log
        match = cls.POSITIVE_PATTERN.search(line)
        if match:
            return LogEntry(
                timestamp=timestamp,
                type=LogType.POSITIVE,
                category=match.group(1),
                message=match.group(2),
                raw=line
            )
        
        # Check negative log
        match = cls.NEGATIVE_PATTERN.search(line)
        if match:
            return LogEntry(
                timestamp=timestamp,
                type=LogType.NEGATIVE,
                category=match.group(1),
                message=match.group(2),
                raw=line
            )
        
        # Check expectation
        match = cls.EXPECT_PATTERN.search(line)
        if match:
            return LogEntry(
                timestamp=timestamp,
                type=LogType.INFO,
                category="EXPECT",
                message=f"Expecting {match.group(1)} within {match.group(2)}s: {match.group(3)}",
                raw=line,
                parsed_data={
                    'event': match.group(1),
                    'timeout': float(match.group(2)),
                    'description': match.group(3)
                }
            )
        
        # Check metric
        match = cls.METRIC_PATTERN.search(line)
        if match:
            return LogEntry(
                timestamp=timestamp,
                type=LogType.INFO,
                category="METRIC",
                message=f"{match.group(1)} = {match.group(2)}",
                raw=line,
                parsed_data={
                    'name': match.group(1),
                    'value': float(match.group(2))
                }
            )
        
        return None


class SerialReader:
    """Read from serial port."""
    
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable[[str], None]] = []
        self._logger = logging.getLogger(__name__)
    
    def start(self) -> bool:
        """Start reading from serial port."""
        try:
            import serial
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self._running = True
            self._thread = threading.Thread(target=self._read_loop, daemon=True)
            self._thread.start()
            self._logger.info(f"Serial reader started on {self.port}")
            return True
        except Exception as e:
            self._logger.error(f"Failed to start serial reader: {e}")
            return False
    
    def stop(self) -> None:
        """Stop reading."""
        self._running = False
        if self.serial:
            self.serial.close()
    
    def add_callback(self, callback: Callable[[str], None]) -> None:
        """Add a callback for received data."""
        self._callbacks.append(callback)
    
    def _read_loop(self) -> None:
        """Background reading loop."""
        while self._running:
            try:
                if self.serial and self.serial.in_waiting:
                    line = self.serial.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        for callback in self._callbacks:
                            callback(line)
            except Exception as e:
                self._logger.error(f"Serial read error: {e}")
    
    def write(self, data: str) -> None:
        """Write to serial port."""
        if self.serial and self.serial.is_open:
            self.serial.write(data.encode('utf-8'))


class ExpectationBoard:
    """Track pending expectations."""
    
    def __init__(self):
        self.expectations: List[Expectation] = []
        self._id_counter = 0
    
    def add_expectation(
        self,
        event_name: str,
        timeout_seconds: float,
        expected_value: Any = None
    ) -> str:
        """Add a new expectation."""
        self._id_counter += 1
        exp_id = f"EXP-{self._id_counter:04d}"
        
        exp = Expectation(
            id=exp_id,
            event_name=event_name,
            timeout_seconds=timeout_seconds,
            start_time=datetime.now(),
            expected_value=expected_value
        )
        self.expectations.append(exp)
        return exp_id
    
    def trigger(self, event_name: str, actual_value: Any = None) -> Optional[Expectation]:
        """Mark an expectation as triggered."""
        for exp in self.expectations:
            if exp.status == "pending" and exp.event_name == event_name:
                exp.status = "triggered"
                exp.triggered_at = datetime.now()
                exp.actual_value = actual_value
                return exp
        return None
    
    def check_timeouts(self) -> List[Expectation]:
        """Check for timed out expectations."""
        timed_out = []
        for exp in self.expectations:
            if exp.is_timeout:
                exp.status = "timeout"
                timed_out.append(exp)
        return timed_out
    
    def cancel(self, exp_id: str) -> bool:
        """Cancel an expectation."""
        for exp in self.expectations:
            if exp.id == exp_id:
                exp.status = "cancelled"
                return True
        return False
    
    def get_pending(self) -> List[Expectation]:
        """Get all pending expectations."""
        return [e for e in self.expectations if e.status == "pending"]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of expectations."""
        total = len(self.expectations)
        pending = len(self.get_pending())
        triggered = len([e for e in self.expectations if e.status == "triggered"])
        timed_out = len([e for e in self.expectations if e.status == "timeout"])
        
        return {
            'total': total,
            'pending': pending,
            'triggered': triggered,
            'timeout': timed_out,
            'cancelled': len([e for e in self.expectations if e.status == "cancelled"]),
            'pending_list': [
                {
                    'id': e.id,
                    'event': e.event_name,
                    'remaining': e.remaining,
                    'progress': e.elapsed / e.timeout_seconds if e.timeout_seconds > 0 else 0
                }
                for e in self.get_pending()
            ]
        }


class LogDiagnosis:
    """One-click diagnosis when negative logs appear."""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.diagnosis_history: List[Dict] = []
    
    def diagnose(
        self,
        negative_logs: List[LogEntry],
        related_code: List[str],
        related_specs: List[str]
    ) -> Dict[str, Any]:
        """Generate a diagnosis report."""
        diagnosis = {
            'timestamp': datetime.now().isoformat(),
            'negative_count': len(negative_logs),
            'negative_logs': [asdict(log) for log in negative_logs],
            'related_code': related_code,
            'related_specs': related_specs,
            'root_causes': self._analyze_causes(negative_logs),
            'ai_prompt': self._generate_ai_prompt(negative_logs, related_code, related_specs)
        }
        
        self.diagnosis_history.append(diagnosis)
        return diagnosis
    
    def _analyze_causes(self, logs: List[LogEntry]) -> List[str]:
        """Analyze potential root causes."""
        causes = []
        
        categories = [log.category for log in logs]
        if 'TIMEOUT' in str(categories):
            causes.append("事件超时: 预期事件未在规定时间内触发")
        if 'HARDWARE' in str(categories):
            causes.append("硬件问题: 硬件状态异常或通信失败")
        if 'ASSERTION' in str(categories):
            causes.append("断言失败: 代码逻辑与预期不符")
        
        return causes
    
    def _generate_ai_prompt(
        self,
        logs: List[LogEntry],
        code: List[str],
        specs: List[str]
    ) -> str:
        """Generate AI prompt for diagnosis."""
        negative_messages = "\n".join([f"- {log.message}" for log in logs])
        
        prompt = f"""## 负日志诊断请求

### 出现的负日志
{negative_messages}

### 相关代码
{chr(10).join([f'```\n{c}\n```' for c in code]) if code else '无'}

### 相关规约
{chr(10).join([f'- {s}' for s in specs]) if specs else '无'}

### 请分析
1. 最可能的根本原因是什么？
2. 需要检查哪些代码位置？
3. 建议的修复方向？
"""
        return prompt


class LogReplay:
    """Offline log replay for post-mortem analysis."""
    
    def __init__(self):
        self.log_entries: List[LogEntry] = []
        self.current_index = 0
    
    def load_file(self, filepath: str) -> int:
        """Load logs from a file."""
        self.log_entries = []
        self.current_index = 0
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                entry = LogParser.parse_line(line.strip())
                if entry:
                    self.log_entries.append(entry)
        
        return len(self.log_entries)
    
    def replay(
        self,
        callback: Callable[[LogEntry], None],
        step_by_step: bool = False,
        delay: float = 0.1
    ) -> None:
        """Replay loaded logs."""
        for entry in self.log_entries[self.current_index:]:
            callback(entry)
            self.current_index += 1
            
            if step_by_step:
                input("Press Enter for next log...")
            else:
                time.sleep(delay)
    
    def seek(self, index: int) -> None:
        """Seek to a specific index."""
        if 0 <= index < len(self.log_entries):
            self.current_index = index
    
    def get_state_at(self, index: int) -> Tuple[List[LogEntry], Dict]:
        """Get log state at a specific index."""
        entries = self.log_entries[:index]
        
        state = {
            'positive_count': len([e for e in entries if e.type == LogType.POSITIVE]),
            'negative_count': len([e for e in entries if e.type == LogType.NEGATIVE]),
            'categories': list(set([e.category for e in entries]))
        }
        
        return entries, state


class NegativeLogger:
    """Main Negative Logger controller."""
    
    def __init__(self, project_root: str, serial_config: Optional[Dict] = None):
        self.project_root = project_root
        self.serial_config = serial_config or {}
        
        self.parser = LogParser()
        self.serial_reader: Optional[SerialReader] = None
        self.expectation_board = ExpectationBoard()
        self.diagnosis = LogDiagnosis(project_root)
        self.replay = LogReplay()
        
        self.log_buffer: List[LogEntry] = []
        self.max_buffer_size = 10000
        
        self.event_bus = EventBus()
        self._logger = logging.getLogger(__name__)
        
        self._setup_callbacks()
    
    def _setup_callbacks(self) -> None:
        """Setup event callbacks."""
        self.event_bus.subscribe(EventType.LOG_RECEIVED, self._on_log_received)
    
    def _on_log_received(self, event: Event) -> None:
        """Handle received log."""
        line = event.data.get('line', '')
        entry = self.parser.parse_line(line)
        
        if entry:
            self._process_entry(entry)
    
    def _process_entry(self, entry: LogEntry) -> None:
        """Process a log entry."""
        self.log_buffer.append(entry)
        
        # Trim buffer if needed
        if len(self.log_buffer) > self.max_buffer_size:
            self.log_buffer = self.log_buffer[-self.max_buffer_size:]
        
        # Publish appropriate event
        if entry.type == LogType.POSITIVE:
            self.event_bus.publish(Event(
                type=EventType.POSITIVE_LOG,
                source="negative_logger",
                data={'entry': asdict(entry)}
            ))
            # Trigger any matching expectations
            self.expectation_board.trigger(entry.category, entry.parsed_data)
        elif entry.type == LogType.NEGATIVE:
            self.event_bus.publish(Event(
                type=EventType.NEGATIVE_LOG,
                source="negative_logger",
                data={'entry': asdict(entry)}
            ))
        
        # Check expectations
        timed_out = self.expectation_board.check_timeouts()
        for exp in timed_out:
            self.event_bus.publish(Event(
                type=EventType.EXPECTATION_TIMEOUT,
                source="negative_logger",
                data={'expectation': asdict(exp)}
            ))
    
    def start_serial(self) -> bool:
        """Start reading from serial port."""
        if not self.serial_config:
            self._logger.warning("No serial config provided")
            return False
        
        self.serial_reader = SerialReader(
            port=self.serial_config.get('port', 'COM3'),
            baudrate=self.serial_config.get('baudrate', 115200),
            timeout=self.serial_config.get('timeout', 1.0)
        )
        
        self.serial_reader.add_callback(self._on_serial_line)
        return self.serial_reader.start()
    
    def stop_serial(self) -> None:
        """Stop serial reading."""
        if self.serial_reader:
            self.serial_reader.stop()
    
    def _on_serial_line(self, line: str) -> None:
        """Handle serial line received."""
        self.event_bus.publish(Event(
            type=EventType.LOG_RECEIVED,
            source="serial",
            data={'line': line}
        ))
    
    def expect(
        self,
        event_name: str,
        timeout_seconds: float,
        expected_value: Any = None
    ) -> str:
        """Register an expectation."""
        return self.expectation_board.add_expectation(event_name, timeout_seconds, expected_value)
    
    def get_logs(
        self,
        log_type: Optional[LogType] = None,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get filtered logs."""
        logs = self.log_buffer
        
        if log_type:
            logs = [l for l in logs if l.type == log_type]
        if category:
            logs = [l for l in logs if l.category == category]
        
        return [asdict(l) for l in logs[-limit:]]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get log summary."""
        logs = self.log_buffer
        
        return {
            'total': len(logs),
            'by_type': {
                'positive': len([l for l in logs if l.type == LogType.POSITIVE]),
                'negative': len([l for l in logs if l.type == LogType.NEGATIVE]),
                'info': len([l for l in logs if l.type == LogType.INFO]),
                'warning': len([l for l in logs if l.type == LogType.WARNING]),
                'error': len([l for l in logs if l.type == LogType.ERROR])
            },
            'categories': list(set([l.category for l in logs])),
            'expectations': self.expectation_board.get_summary()
        }
