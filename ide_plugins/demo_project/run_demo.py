#!/usr/bin/env python3
"""
演示脚本 - 展示 IDE AI Engineering Tools 的使用

使用方法:
    python run_demo.py
"""
import sys
import os

# 添加 ide_plugins 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.agents_md import AgentsMD, DocMetadata, DocHealthDetail, HotLevel, HealthStatus
from convergence_engine import ConvergenceEngine
from knowledge_vitals import KnowledgeVitalsDashboard
from law_manager import LawManager
from schematic_navigator import SchematicNavigator


def demo_knowledge_vitals():
    """演示知识体征仪表盘"""
    print("\n" + "="*60)
    print("📊 知识体征仪表盘演示")
    print("="*60)
    
    # 初始化
    dashboard = KnowledgeVitalsDashboard(
        ".",
        config={
            'agents_md': "docs/agents.md",
            'knowledge_vitals': {
                'health_thresholds': {
                    'healthy': 0.8,
                    'warning': 0.5,
                    'danger': 0.3
                },
                'cold_document_days': 30,
                'check_interval': 60
            }
        }
    )
    
    # 获取概览 (会自动刷新数据)
    overview = dashboard.get_overview()
    
    print(f"\n📈 全局统计:")
    summary = overview['summary']
    print(f"   文档总数: {summary['total_documents']}")
    print(f"   健康分布: 健康={summary['health_distribution']['healthy']}, "
          f"亚健康={summary['health_distribution']['subhealthy']}, "
          f"预警={summary['health_distribution']['warning']}, "
          f"危险={summary['health_distribution']['danger']}")
    print(f"   活跃分布: 热={summary['activity_distribution']['hot']}, "
          f"温={summary['activity_distribution']['warm']}, "
          f"冷={summary['activity_distribution']['cold']}")
    
    # 显示健康度环形图
    print(f"\n🍩 健康度分布:")
    for item in overview['ring_chart']:
        print(f"   {item['name']}: {item['value']} 个")
    
    # 显示告警
    if overview['alerts']:
        print(f"\n🚨 告警列表:")
        for alert in overview['alerts'][:3]:
            print(f"   [{alert['level']}] {alert['message']}")


def demo_convergence_engine():
    """演示收敛引擎"""
    print("\n" + "="*60)
    print("🔧 收敛引擎演示")
    print("="*60)
    
    # 初始化
    engine = ConvergenceEngine(".", config={
        'max_iterations': 10,
        'convergence_threshold': 0.95
    })
    
    # 添加Bug任务
    print("\n📝 添加Bug任务:")
    engine.add_bug_task(
        title="UART通信丢包",
        description="高速传输时出现丢包 | 位置: rs485.c:45 | 优先级: 高"
    )
    engine.add_bug_task(
        title="I2C总线忙",
        description="连续读取失败 | 位置: sht40_driver.c:32 | 优先级: 中"
    )
    
    # 添加测试任务
    print("\n🧪 添加测试任务:")
    engine.add_test_task(
        title="test_modbus_reliability",
        description="测试Modbus通信可靠性 | 路径: tests/test_modbus.c | 优先级: 高"
    )
    engine.add_test_task(
        title="test_i2c_retry",
        description="测试I2C重试机制 | 路径: tests/test_i2c.c | 优先级: 中"
    )
    
    # 显示任务面板
    summary = engine.task_panel.get_summary()
    print(f"\n📊 任务统计:")
    print(f"   Bug任务: 总计={summary['bugs']['total']}, "
          f"待处理={summary['bugs']['pending']}, "
          f"进行中={summary['bugs']['in_progress']}")
    print(f"   测试任务: 总计={summary['tests']['total']}, "
          f"待处理={summary['tests']['pending']}")


def demo_law_manager():
    """演示法则管理器"""
    print("\n" + "="*60)
    print("📜 法则管理器演示")
    print("="*60)
    
    # 初始化
    manager = LawManager(".")
    
    # 构建法则树
    print("\n🌳 构建法则树...")
    manager._build_law_tree()
    tree_json = manager.export_tree_json()
    
    print(f"\n📂 法则结构:")
    print(f"   JSON长度: {len(tree_json)} 字符")
    
    # 获取告警
    print("\n⚠️ 法则验证:")
    violations = manager.validate_code("test.c", "HAL_Delay(100); // 在中断中使用")
    if violations:
        for v in violations[:3]:
            print(f"   [{v.severity}] {v.message}")
    else:
        print("   无告警")


def demo_schematic_navigator():
    """演示电路图导航器"""
    print("\n" + "="*60)
    print("🔌 电路图导航器演示")
    print("="*60)
    
    # 初始化
    nav = SchematicNavigator(".", config={
        'schematic_storage': 'hardware/schematics',
        'ocr_cache': 'hardware/ocr_cache',
        'code_refs': 'docs/code_refs.json'
    })
    
    # 添加组件映射
    print("\n🗺️ 添加组件映射:")
    nav.add_code_link("R1", "rs485.c:45")  # 10K上拉电阻
    nav.add_code_link("U1", "main.c:10")   # STM32F407VG
    nav.add_code_link("U2", "sht40_driver.c:15")  # SHT40传感器
    
    # 显示组件列表
    print(f"\n📦 组件列表:")
    tree = nav.get_component_tree()
    for item in tree[:5]:
        print(f"   {item['reference']}: {item['description']}")
        refs = nav.code_links.get_code_refs(item['reference'])
        if refs:
            print(f"      → 代码: {', '.join(refs)}")


def main():
    """主函数"""
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("\n" + "[DEMO]"*30)
    print("IDE AI Engineering Tools - Demo")
    print("[DEMO]"*30)
    
    try:
        demo_knowledge_vitals()
        demo_convergence_engine()
        demo_law_manager()
        demo_schematic_navigator()
        
        print("\n" + "="*60)
        print("✅ 演示完成！")
        print("="*60)
        print("\n启动Web服务:")
        print("  cd .. && python main.py --all --project demo_project")
        print("\n或在浏览器打开:")
        print("  http://127.0.0.1:8765/")
        
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
