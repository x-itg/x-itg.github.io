"""
Schematic Navigator - PDF schematic to clickable hardware map.
"""
import os
import json
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any, Callable, Tuple
from pathlib import Path
import logging

from core.events import EventBus, Event, EventType


@dataclass
class Component:
    """A component in the schematic."""
    id: str
    reference: str  # e.g., "R1", "U2"
    name: str       # e.g., "10k Resistor", "STM32F103"
    type: str       # resistor, capacitor, ic, connector, etc.
    x: float = 0
    y: float = 0
    pins: List[Dict[str, Any]] = field(default_factory=list)
    linked_code: List[str] = field(default_factory=list)  # file:line references
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SchematicPage:
    """A page in the schematic PDF."""
    page_num: int
    title: str
    width: float = 0
    height: float = 0
    components: List[Component] = field(default_factory=list)


class PDFViewer:
    """PDF schematic viewer with component navigation."""
    
    def __init__(self, storage_dir: str = "docs/schematics/"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_pdf: Optional[str] = None
        self.pages: List[SchematicPage] = []
        self.components: Dict[str, Component] = {}
        self._logger = logging.getLogger(__name__)
    
    def load_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Load a PDF schematic."""
        self.current_pdf = pdf_path
        
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(pdf_path)
            self.pages = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                schematic_page = SchematicPage(
                    page_num=page_num,
                    title=f"Page {page_num + 1}",
                    width=page.rect.width,
                    height=page.rect.height
                )
                
                # In real implementation, this would use OCR/AI to detect components
                # For now, return metadata
                self.pages.append(schematic_page)
            
            doc.close()
            
            return {
                'success': True,
                'pages': len(self.pages),
                'path': pdf_path
            }
        except ImportError:
            self._logger.warning("PyMuPDF not installed, using basic loading")
            return {
                'success': True,
                'pages': 1,
                'path': pdf_path
            }
        except Exception as e:
            self._logger.error(f"Failed to load PDF: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_component(self, component_id: str) -> Optional[Component]:
        """Get component by ID."""
        return self.components.get(component_id)
    
    def search_components(self, query: str) -> List[Component]:
        """Search components by name or reference."""
        query_lower = query.lower()
        results = []
        
        for comp in self.components.values():
            if (query_lower in comp.reference.lower() or
                query_lower in comp.name.lower() or
                query_lower in comp.type.lower()):
                results.append(comp)
        
        return results
    
    def highlight_component(self, component_id: str) -> Dict[str, Any]:
        """Get highlight info for a component."""
        comp = self.get_component(component_id)
        if not comp:
            return {'success': False, 'error': 'Component not found'}
        
        return {
            'success': True,
            'component': {
                'id': comp.id,
                'reference': comp.reference,
                'name': comp.name,
                'x': comp.x,
                'y': comp.y,
                'pins': comp.pins
            }
        }
    
    def add_component(self, component: Component) -> None:
        """Add a component manually or from OCR."""
        self.components[component.id] = component


class CodeLinkManager:
    """Manage bidirectional links between components and code."""
    
    def __init__(self, refs_file: str = ".code_refs.json"):
        self.refs_file = Path(refs_file)
        self.links: Dict[str, List[str]] = {}  # component_id -> [code_refs]
        self.reverse_links: Dict[str, str] = {}  # code_ref -> component_id
        self._load()
    
    def _load(self) -> None:
        """Load links from file."""
        if self.refs_file.exists():
            try:
                with open(self.refs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.links = data.get('links', {})
                    self.reverse_links = data.get('reverse_links', {})
            except json.JSONDecodeError:
                self.links = {}
                self.reverse_links = {}
    
    def _save(self) -> None:
        """Save links to file."""
        data = {
            'links': self.links,
            'reverse_links': self.reverse_links
        }
        with open(self.refs_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_link(self, component_id: str, code_ref: str) -> None:
        """Add a link between component and code."""
        # component_id -> code_ref
        if component_id not in self.links:
            self.links[component_id] = []
        if code_ref not in self.links[component_id]:
            self.links[component_id].append(code_ref)
        
        # code_ref -> component_id (reverse)
        self.reverse_links[code_ref] = component_id
        
        self._save()
    
    def remove_link(self, component_id: str, code_ref: str) -> bool:
        """Remove a link."""
        if component_id in self.links and code_ref in self.links[component_id]:
            self.links[component_id].remove(code_ref)
            if not self.links[component_id]:
                del self.links[component_id]
            
            if code_ref in self.reverse_links:
                del self.reverse_links[code_ref]
            
            self._save()
            return True
        return False
    
    def get_code_refs(self, component_id: str) -> List[str]:
        """Get all code references for a component."""
        return self.links.get(component_id, [])
    
    def get_component(self, code_ref: str) -> Optional[str]:
        """Get component ID for a code reference."""
        return self.reverse_links.get(code_ref)
    
    def link_to_position(self, code_ref: str) -> Optional[Dict[str, Any]]:
        """Parse code reference to file and line."""
        # Format: "filename:line" or "filename:function"
        if ':' in code_ref:
            parts = code_ref.rsplit(':', 1)
            if len(parts) == 2:
                try:
                    line_num = int(parts[1])
                    return {'file': parts[0], 'line': line_num}
                except ValueError:
                    return {'file': parts[0], 'function': parts[1]}
        
        return {'file': code_ref}
    
    def auto_scan(self, code_dir: str) -> Dict[str, List[str]]:
        """Auto-scan code for component references."""
        import re
        
        found_links: Dict[str, List[str]] = {}
        patterns = {
            'pin': r'(GPIO[A-Z]\d+)',
            'peripheral': r'(UART\d|I2C\d|SPI\d|TIM\d)',
            'module': r'(rs485|i2c|spi|uart)_\w+\.c'
        }
        
        code_path = Path(code_dir)
        if not code_path.exists():
            return found_links
        
        for file_path in code_path.rglob("*.c"):
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            for category, pattern in patterns.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if match not in found_links:
                        found_links[match] = []
                    
                    ref = f"{file_path.name}:1"  # Simplified
                    if ref not in found_links[match]:
                        found_links[match].append(ref)
        
        # Update links
        for component_id, refs in found_links.items():
            self.links[component_id] = refs
        
        self._save()
        return found_links


class OCRProcessor:
    """OCR processing for PDF schematics."""
    
    def __init__(self, cache_dir: str = ".cache/ocr/"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._logger = logging.getLogger(__name__)
    
    def extract_text(self, pdf_path: str, page_num: int = 0) -> str:
        """Extract text from a PDF page."""
        try:
            import fitz
            
            doc = fitz.open(pdf_path)
            page = doc[page_num]
            text = page.get_text()
            doc.close()
            
            return text
        except ImportError:
            self._logger.warning("PyMuPDF not installed")
            return ""
        except Exception as e:
            self._logger.error(f"Text extraction failed: {e}")
            return ""
    
    def extract_with_ocr(self, pdf_path: str, page_num: int = 0) -> Dict[str, Any]:
        """Extract text with OCR for better accuracy."""
        try:
            import fitz
            from PIL import Image
            import pytesseract
            
            doc = fitz.open(pdf_path)
            page = doc[page_num]
            
            # Render page to image
            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Save to cache
            cache_file = self.cache_dir / f"{Path(pdf_path).stem}_page{page_num}.png"
            img.save(cache_file)
            
            # OCR
            text = pytesseract.image_to_string(img, lang='eng')
            
            doc.close()
            
            return {
                'success': True,
                'text': text,
                'cache_file': str(cache_file)
            }
        except ImportError as e:
            self._logger.warning(f"OCR dependencies not installed: {e}")
            return {
                'success': False,
                'error': f"Missing dependency: {e}"
            }
        except Exception as e:
            self._logger.error(f"OCR failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def parse_components(self, text: str) -> List[Component]:
        """Parse components from OCR text."""
        import re
        
        components = []
        
        # Common patterns for schematics
        patterns = {
            'resistor': r'R(\d+)\s+(\d+[\dKKM]Ω)',
            'capacitor': r'C(\d+)\s+(\d+[\dµpn]F)',
            'ic': r'(U\d+)\s+([A-Z0-9-]+)',
            'connector': r'(J\d+|CN\d+)\s+(.*)',
            'diode': r'D(\d+)\s+(.*)',
            'transistor': r'Q(\d+)\s+(.*)'
        }
        
        for comp_type, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for i, match in enumerate(matches):
                comp_id = f"{comp_type.upper()[:2]}-{i+1:03d}"
                
                component = Component(
                    id=comp_id,
                    reference=match[0] if isinstance(match[0], str) else f"{comp_type.upper()[0]}{i+1}",
                    name=match[1] if len(match) > 1 else match[0],
                    type=comp_type
                )
                components.append(component)
        
        return components
    
    def save_markdown(self, components: List[Component], output_path: str) -> str:
        """Save extracted components as Markdown."""
        content = "# 原理图组件清单\n\n"
        content += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Group by type
        by_type: Dict[str, List[Component]] = {}
        for comp in components:
            if comp.type not in by_type:
                by_type[comp.type] = []
            by_type[comp.type].append(comp)
        
        for comp_type, comps in by_type.items():
            content += f"## {comp_type.upper()}\n\n"
            content += "| ID | 参考 | 名称 | 引脚 |\n"
            content += "|---|------|------|-----|\n"
            
            for comp in comps:
                pins = len(comp.pins)
                content += f"| {comp.id} | {comp.reference} | {comp.name} | {pins} |\n"
            
            content += "\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return content
    
    def save_json(self, components: List[Component], output_path: str) -> str:
        """Save extracted components as JSON."""
        data = [
            {
                'id': c.id,
                'reference': c.reference,
                'name': c.name,
                'type': c.type,
                'x': c.x,
                'y': c.y,
                'pins': c.pins,
                'linked_code': c.linked_code
            }
            for c in components
        ]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return output_path


class SchematicNavigator:
    """Main Schematic Navigator controller."""
    
    def __init__(self, project_root: str, config: Optional[Dict] = None):
        self.project_root = Path(project_root)
        self.config = config or {}
        
        storage_dir = self.config.get('schematic_storage', 'docs/schematics/')
        cache_dir = self.config.get('ocr_cache', '.cache/ocr/')
        refs_file = self.config.get('code_refs', '.code_refs.json')
        
        self.viewer = PDFViewer(str(self.project_root / storage_dir))
        self.code_links = CodeLinkManager(str(self.project_root / refs_file))
        self.ocr = OCRProcessor(str(self.project_root / cache_dir))
        
        self.event_bus = EventBus()
        self._logger = logging.getLogger(__name__)
        
        self._setup_callbacks()
    
    def _setup_callbacks(self) -> None:
        """Setup event callbacks."""
        pass
    
    def load_schematic(self, pdf_path: str) -> Dict[str, Any]:
        """Load a schematic PDF."""
        full_path = self.project_root / pdf_path
        result = self.viewer.load_pdf(str(full_path))
        
        if result.get('success'):
            self.event_bus.publish(Event(
                type=EventType.SCHEMATIC_LOADED,
                source="schematic_navigator",
                data={'path': str(full_path), 'pages': result.get('pages')}
            ))
        
        return result
    
    def navigate_to_component(self, component_id: str) -> Dict[str, Any]:
        """Navigate to a component and get code links."""
        highlight = self.viewer.highlight_component(component_id)
        code_refs = self.code_links.get_code_refs(component_id)
        
        result = {
            'component': highlight.get('component'),
            'code_refs': code_refs,
            'code_positions': [
                self.code_links.link_to_position(ref)
                for ref in code_refs
            ]
        }
        
        if result['component']:
            self.event_bus.publish(Event(
                type=EventType.COMPONENT_CLICKED,
                source="schematic_navigator",
                data={'component_id': component_id}
            ))
        
        return result
    
    def navigate_to_code(self, code_ref: str) -> Dict[str, Any]:
        """Navigate from code to component."""
        position = self.code_links.link_to_position(code_ref)
        component_id = self.code_links.get_component(code_ref)
        
        result = {
            'position': position,
            'component_id': component_id
        }
        
        if component_id:
            self.event_bus.publish(Event(
                type=EventType.CODE_LINK_CLICKED,
                source="schematic_navigator",
                data={'code_ref': code_ref, 'component_id': component_id}
            ))
        
        return result
    
    def ocr_page(self, pdf_path: str, page_num: int = 0) -> Dict[str, Any]:
        """OCR a schematic page."""
        full_path = self.project_root / pdf_path
        result = self.ocr.extract_with_ocr(str(full_path), page_num)
        
        if result.get('success'):
            # Parse components
            text = result.get('text', '')
            components = self.ocr.parse_components(text)
            
            # Add to viewer
            for comp in components:
                self.viewer.add_component(comp)
            
            result['components'] = len(components)
            
            # Save outputs
            stem = Path(pdf_path).stem
            self.ocr.save_markdown(components, str(self.project_root / "docs" / f"{stem}_components.md"))
            self.ocr.save_json(components, str(self.project_root / "docs" / f"{stem}_components.json"))
            
            self.event_bus.publish(Event(
                type=EventType.OCR_COMPLETED,
                source="schematic_navigator",
                data={'pdf': pdf_path, 'page': page_num, 'components': len(components)}
            ))
        
        return result
    
    def add_code_link(self, component_id: str, code_ref: str) -> bool:
        """Add a code link for a component."""
        self.code_links.add_link(component_id, code_ref)
        return True
    
    def auto_scan_links(self) -> Dict[str, List[str]]:
        """Auto-scan code directory for component references."""
        return self.code_links.auto_scan(str(self.project_root / "src"))
    
    def get_component_tree(self) -> List[Dict[str, Any]]:
        """Get component tree for tree view."""
        by_type: Dict[str, List[Dict]] = {}
        
        for comp in self.viewer.components.values():
            if comp.type not in by_type:
                by_type[comp.type] = []
            
            by_type[comp.type].append({
                'id': comp.id,
                'reference': comp.reference,
                'name': comp.name,
                'has_code_links': len(self.code_links.get_code_refs(comp.id)) > 0
            })
        
        return [
            {
                'type': type_name,
                'children': components
            }
            for type_name, components in by_type.items()
        ]
