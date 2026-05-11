#!/usr/bin/env python3
"""
IDE AI Engineering Tools - Main Entry Point
嵌入式AI工程化体系的IDE插件后端服务
"""
import os
import sys
import argparse
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import Config, get_config
from core.events import EventBus, get_event_bus

# Import all modules
from law_manager import LawManager
from negative_logger import NegativeLogger
from convergence_engine import ConvergenceEngine
from schematic_navigator import SchematicNavigator
from knowledge_vitals import KnowledgeVitalsDashboard
from skills_launcher import SkillsLauncher
from legacy_adapter import LegacyAdapter


def setup_logging(config: Config) -> None:
    """Setup logging configuration."""
    log_dir = Path(config.logging.file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, config.logging.level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.logging.file),
            logging.StreamHandler()
        ]
    )


class PluginManager:
    """Manages all plugin modules."""
    
    def __init__(self, project_root: str, config: Config):
        self.project_root = project_root
        self.config = config
        self.event_bus = get_event_bus()
        
        self.law_manager: Optional[LawManager] = None
        self.negative_logger: Optional[NegativeLogger] = None
        self.convergence_engine: Optional[ConvergenceEngine] = None
        self.schematic_navigator: Optional[SchematicNavigator] = None
        self.knowledge_vitals: Optional[KnowledgeVitalsDashboard] = None
        self.skills_launcher: Optional[SkillsLauncher] = None
        self.legacy_adapter: Optional[LegacyAdapter] = None
    
    def init_all(self) -> None:
        """Initialize all modules."""
        logging.info("Initializing all modules...")
        
        self.law_manager = LawManager(self.project_root)
        logging.info("Law Manager initialized")
        
        self.negative_logger = NegativeLogger(
            self.project_root,
            serial_config={
                'port': self.config.serial.port,
                'baudrate': self.config.serial.baudrate,
                'timeout': self.config.serial.timeout
            }
        )
        logging.info("Negative Logger initialized")
        
        self.convergence_engine = ConvergenceEngine(
            self.project_root,
            config={
                'max_iterations': self.config.convergence.max_iterations,
                'convergence_threshold': self.config.convergence.convergence_threshold
            }
        )
        logging.info("Convergence Engine initialized")
        
        self.schematic_navigator = SchematicNavigator(
            self.project_root,
            config={
                'schematic_storage': self.config.schematic.pdf_storage,
                'ocr_cache': self.config.schematic.ocr_cache,
                'code_refs': self.config.schematic.code_refs
            }
        )
        logging.info("Schematic Navigator initialized")
        
        self.knowledge_vitals = KnowledgeVitalsDashboard(
            self.project_root,
            config={
                'agents_md': self.config.project.agents_md,
                'knowledge_vitals': {
                    'health_thresholds': {
                        'healthy': self.config.knowledge_vitals.health_thresholds.healthy,
                        'warning': self.config.knowledge_vitals.health_thresholds.warning,
                        'danger': self.config.knowledge_vitals.health_thresholds.danger
                    },
                    'cold_document_days': self.config.knowledge_vitals.cold_document_days,
                    'check_interval': self.config.knowledge_vitals.check_interval
                }
            }
        )
        logging.info("Knowledge Vitals Dashboard initialized")
        
        self.skills_launcher = SkillsLauncher(
            self.project_root,
            config={'skills_dir': self.config.project.skills_dir}
        )
        logging.info("Skills Launcher initialized")
        
        self.legacy_adapter = LegacyAdapter(
            self.project_root,
            config={
                'host': self.config.remote_build.host,
                'user': self.config.remote_build.user,
                'password': self.config.remote_build.password,
                'keil_path': self.config.remote_build.keil_path,
                'project_ext': self.config.remote_build.project_ext
            }
        )
        logging.info("Legacy Adapter initialized")
        
        logging.info("All modules initialized successfully")
    
    def get_status(self) -> dict:
        """Get status of all modules."""
        return {
            'law_manager': {
                'initialized': self.law_manager is not None,
                'documents': len(self.law_manager.agents_md.documents) if self.law_manager and self.law_manager.agents_md else 0
            },
            'negative_logger': {
                'initialized': self.negative_logger is not None,
                'log_buffer_size': len(self.negative_logger.log_buffer) if self.negative_logger else 0
            },
            'convergence_engine': {
                'initialized': self.convergence_engine is not None,
                'tasks': self.convergence_engine.task_panel.get_summary() if self.convergence_engine else {}
            },
            'schematic_navigator': {
                'initialized': self.schematic_navigator is not None,
                'components': len(self.schematic_navigator.viewer.components) if self.schematic_navigator else 0
            },
            'knowledge_vitals': {
                'initialized': self.knowledge_vitals is not None,
                'overview': self.knowledge_vitals.get_overview() if self.knowledge_vitals else {}
            },
            'skills_launcher': {
                'initialized': self.skills_launcher is not None,
                'skills': len(self.skills_launcher.sidebar.skills) if self.skills_launcher else 0
            },
            'legacy_adapter': {
                'initialized': self.legacy_adapter is not None
            }
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='IDE AI Engineering Tools',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --all                    Start all modules
  %(prog)s --module law_manager     Start only Law Manager
  %(prog)s --status                 Show status of all modules
  %(prog)s --config custom.yaml      Use custom config file
        """
    )
    
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Start all modules'
    )
    
    parser.add_argument(
        '--module', '-m',
        choices=[
            'law_manager',
            'negative_logger',
            'convergence_engine',
            'schematic_navigator',
            'knowledge_vitals',
            'skills_launcher',
            'legacy_adapter'
        ],
        help='Start specific module'
    )
    
    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help='Show status of all modules'
    )
    
    parser.add_argument(
        '--config', '-c',
        default=None,
        help='Configuration file path (default: <project>/config.yaml)'
    )
    
    parser.add_argument(
        '--project', '-p',
        default='.',
        help='Project root directory (default: current directory)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=None,
        help='Server port (default: from config)'
    )
    
    args = parser.parse_args()
    
    # Load configuration - use project/config.yaml if not specified
    if args.config:
        config_path = os.path.join(args.project, args.config)
    else:
        config_path = os.path.join(args.project, 'config.yaml')
    
    config = Config.from_yaml(config_path)
    
    # Override port if specified
    if args.port:
        config.server.port = args.port
    
    # Setup logging
    setup_logging(config)
    
    logger = logging.getLogger(__name__)
    logger.info(f"IDE AI Engineering Tools starting...")
    logger.info(f"Project root: {args.project}")
    logger.info(f"Config: {config_path}")
    
    # Initialize plugin manager
    manager = PluginManager(args.project, config)
    
    # Handle commands
    if args.status:
        manager.init_all()
        import json
        print(json.dumps(manager.get_status(), indent=2, default=str))
        return
    
    if args.all or args.module:
        modules_to_start = []
        
        if args.all:
            manager.init_all()
            logger.info("All modules started")
        else:
            manager.init_all()
            logger.info(f"Module '{args.module}' started")
        
        # Start the web server
        from flask import Flask, jsonify, send_from_directory
        from flask_cors import CORS
        
        app = Flask(__name__, static_folder=None)
        CORS(app)
        
        # Get web directory
        web_dir = os.path.join(os.path.dirname(__file__), 'web')
        
        @app.route('/')
        @app.route('/index.html')
        def serve_index():
            return send_from_directory(web_dir, 'index.html')
        
        @app.route('/<path:filename>')
        def serve_static(filename):
            return send_from_directory(web_dir, filename)
        
        @app.route('/api/status')
        def api_status():
            return jsonify(manager.get_status())
        
        @app.route('/api/health')
        def api_health():
            return jsonify({'status': 'healthy'})
        
        logger.info(f"Starting server on {config.server.host}:{config.server.port}")
        app.run(
            host=config.server.host,
            port=config.server.port,
            debug=config.server.debug
        )
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
