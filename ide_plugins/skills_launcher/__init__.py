"""
Skills Launcher - Clickable high-frequency operations with context.
"""
import os
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any, Callable
from pathlib import Path
import logging

from core.events import EventBus, Event, EventType


@dataclass
class SkillParameter:
    """A parameter for a skill."""
    name: str
    label: str
    type: str  # string, number, boolean, select, multiselect
    required: bool = False
    default: Any = None
    options: List[Any] = field(default_factory=list)
    description: str = ""


@dataclass
class Skill:
    """A skill definition."""
    id: str
    name: str
    description: str
    category: str
    icon: str = ""
    parameters: List[SkillParameter] = field(default_factory=list)
    intent_template: str = ""
    convergence_enabled: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillInvocation:
    """A skill invocation record."""
    id: str
    skill_id: str
    skill_name: str
    timestamp: datetime
    parameters: Dict[str, Any]
    status: str = "pending"  # pending, running, completed, failed
    result: Any = None
    error: str = ""
    duration_ms: int = 0


class SidebarList:
    """Sidebar list of available skills."""
    
    def __init__(self, skills_dir: str):
        self.skills_dir = Path(skills_dir)
        self.skills: List[Skill] = []
        self._load_skills()
    
    def _load_skills(self) -> None:
        """Load skill definitions from directory."""
        self.skills = []
        
        if not self.skills_dir.exists():
            return
        
        for skill_file in self.skills_dir.glob("*.json"):
            try:
                with open(skill_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    skill = Skill(
                        id=data.get('id', skill_file.stem),
                        name=data.get('name', skill_file.stem),
                        description=data.get('description', ''),
                        category=data.get('category', 'General'),
                        icon=data.get('icon', ''),
                        parameters=[
                            SkillParameter(**p) for p in data.get('parameters', [])
                        ],
                        intent_template=data.get('intent_template', ''),
                        convergence_enabled=data.get('convergence_enabled', False),
                        metadata=data.get('metadata', {})
                    )
                    
                    self.skills.append(skill)
            except Exception as e:
                logging.warning(f"Failed to load skill {skill_file}: {e}")
    
    def reload(self) -> None:
        """Reload skills from disk."""
        self._load_skills()
    
    def get_by_category(self) -> Dict[str, List[Skill]]:
        """Get skills grouped by category."""
        categories: Dict[str, List[Skill]] = {}
        
        for skill in self.skills:
            if skill.category not in categories:
                categories[skill.category] = []
            categories[skill.category].append(skill)
        
        return categories
    
    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Get a skill by ID."""
        for skill in self.skills:
            if skill.id == skill_id:
                return skill
        return None
    
    def search(self, query: str) -> List[Skill]:
        """Search skills by name or description."""
        query_lower = query.lower()
        results = []
        
        for skill in self.skills:
            if (query_lower in skill.name.lower() or
                query_lower in skill.description.lower() or
                query_lower in skill.category.lower()):
                results.append(skill)
        
        return results


class ParameterGuide:
    """Guided parameter input for skill invocation."""
    
    def __init__(self):
        self.current_skill: Optional[Skill] = None
        self.parameter_values: Dict[str, Any] = {}
    
    def start(self, skill: Skill) -> Dict[str, Any]:
        """Start parameter collection for a skill."""
        self.current_skill = skill
        self.parameter_values = {}
        
        for param in skill.parameters:
            if param.default is not None:
                self.parameter_values[param.name] = param.default
        
        return self._get_form()
    
    def set_value(self, param_name: str, value: Any) -> bool:
        """Set a parameter value."""
        if not self.current_skill:
            return False
        
        for param in self.current_skill.parameters:
            if param.name == param_name:
                self.parameter_values[param.name] = value
                return True
        
        return False
    
    def validate(self) -> Dict[str, Any]:
        """Validate current parameters."""
        if not self.current_skill:
            return {'valid': False, 'errors': ['No skill selected']}
        
        errors = []
        
        for param in self.current_skill.parameters:
            if param.required and param.name not in self.parameter_values:
                errors.append(f"{param.label} is required")
            elif param.name in self.parameter_values:
                value = self.parameter_values[param.name]
                if param.type == 'number' and not isinstance(value, (int, float)):
                    errors.append(f"{param.label} must be a number")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'values': self.parameter_values
        }
    
    def generate_intent(self) -> str:
        """Generate intent file content from parameters."""
        if not self.current_skill:
            return ""
        
        template = self.current_skill.intent_template
        
        for key, value in self.parameter_values.items():
            placeholder = f"{{{key}}}"
            if placeholder in template:
                template = template.replace(placeholder, str(value))
            else:
                template += f"\n{key}: {value}"
        
        return template
    
    def _get_form(self) -> Dict[str, Any]:
        """Get form definition."""
        if not self.current_skill:
            return {}
        
        return {
            'skill_id': self.current_skill.id,
            'skill_name': self.current_skill.name,
            'parameters': [
                {
                    'name': p.name,
                    'label': p.label,
                    'type': p.type,
                    'required': p.required,
                    'default': p.default,
                    'options': p.options,
                    'description': p.description
                }
                for p in self.current_skill.parameters
            ]
        }


class ConvergenceLink:
    """Link skills to convergence engine."""
    
    def __init__(self, convergence_engine=None):
        self.convergence_engine = convergence_engine
        self.invocation_history: List[SkillInvocation] = []
    
    def submit_to_convergence(
        self,
        invocation: SkillInvocation,
        task_panel
    ) -> str:
        """Submit skill result to convergence queue."""
        if not self.convergence_engine:
            return ""
        
        task_id = task_panel.add_task(
            task_type='TEST_ENHANCE' if 'test' in invocation.skill_id else 'BUG_FIX',
            title=f"Skill: {invocation.skill_name}",
            description=invocation.result or str(invocation.parameters),
            priority=5
        )
        
        return task_id
    
    def get_invocation_impact(self, invocation_id: str) -> Dict[str, Any]:
        """Get impact analysis of an invocation."""
        for inv in self.invocation_history:
            if inv.id == invocation_id:
                return {
                    'skill': inv.skill_name,
                    'status': inv.status,
                    'result': inv.result,
                    'convergence_tasks': []
                }
        
        return {}


class SkillsLauncher:
    """Main Skills Launcher controller."""
    
    def __init__(self, project_root: str, config: Optional[Dict] = None):
        self.project_root = Path(project_root)
        self.config = config or {}
        
        skills_dir = self.config.get('skills_dir', '.skills/')
        
        self.sidebar = SidebarList(str(self.project_root / skills_dir))
        self.param_guide = ParameterGuide()
        self.convergence_link = ConvergenceLink()
        self.invocations: List[SkillInvocation] = []
        
        self.event_bus = EventBus()
        self._logger = logging.getLogger(__name__)
        self._invocation_counter = 0
    
    def get_skills_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get skills grouped by category for sidebar display."""
        categories = self.sidebar.get_by_category()
        
        return {
            cat: [
                {
                    'id': s.id,
                    'name': s.name,
                    'description': s.description,
                    'icon': s.icon,
                    'has_parameters': len(s.parameters) > 0,
                    'convergence_enabled': s.convergence_enabled
                }
                for s in skills
            ]
            for cat, skills in categories.items()
        }
    
    def start_invocation(self, skill_id: str) -> Dict[str, Any]:
        """Start invoking a skill, returns parameter form if needed."""
        skill = self.sidebar.get_skill(skill_id)
        if not skill:
            return {'error': 'Skill not found'}
        
        if skill.parameters:
            return self.param_guide.start(skill)
        else:
            return self.invoke_skill(skill_id, {})
    
    def set_parameter(self, param_name: str, value: Any) -> Dict[str, Any]:
        """Set a parameter value."""
        self.param_guide.set_value(param_name, value)
        return self.param_guide.validate()
    
    def invoke_skill(
        self,
        skill_id: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Invoke a skill with parameters."""
        skill = self.sidebar.get_skill(skill_id)
        if not skill:
            return {'error': 'Skill not found'}
        
        self._invocation_counter += 1
        invocation_id = f"INV-{datetime.now().strftime('%Y%m%d')}-{self._invocation_counter:04d}"
        
        invocation = SkillInvocation(
            id=invocation_id,
            skill_id=skill_id,
            skill_name=skill.name,
            timestamp=datetime.now(),
            parameters=parameters,
            status="running"
        )
        
        self.invocations.append(invocation)
        
        self.event_bus.publish(Event(
            type=EventType.SKILL_INVOKED,
            source="skills_launcher",
            data={
                'invocation_id': invocation_id,
                'skill_id': skill_id,
                'skill_name': skill.name
            }
        ))
        
        # Generate intent file (simplified - real impl would trigger AI)
        intent = self.param_guide.generate_intent() if parameters else ""
        
        # In real implementation, this would:
        # 1. Write intent file to .intent/
        # 2. Trigger AI with the intent
        # 3. Generate code/tests
        # 4. Return results
        
        result = {
            'invocation_id': invocation_id,
            'skill_id': skill_id,
            'skill_name': skill.name,
            'intent_generated': bool(intent),
            'status': 'ready_for_ai'
        }
        
        invocation.result = result
        invocation.status = "completed"
        
        self.event_bus.publish(Event(
            type=EventType.SKILL_COMPLETED,
            source="skills_launcher",
            data={'invocation_id': invocation_id, 'result': result}
        ))
        
        return result
    
    def get_invocation(self, invocation_id: str) -> Optional[SkillInvocation]:
        """Get an invocation by ID."""
        for inv in self.invocations:
            if inv.id == invocation_id:
                return inv
        return None
    
    def get_recent_invocations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent invocations."""
        return [
            {
                'id': inv.id,
                'skill_id': inv.skill_id,
                'skill_name': inv.skill_name,
                'timestamp': inv.timestamp.isoformat(),
                'status': inv.status,
                'result': inv.result
            }
            for inv in sorted(self.invocations, key=lambda x: x.timestamp, reverse=True)[:limit]
        ]
    
    def search_skills(self, query: str) -> List[Dict[str, Any]]:
        """Search skills."""
        results = self.sidebar.search(query)
        
        return [
            {
                'id': s.id,
                'name': s.name,
                'description': s.description,
                'category': s.category
            }
            for s in results
        ]
