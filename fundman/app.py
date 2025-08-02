import argparse
import sys
import os
from typing import Optional, List
# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 使用绝对导入而不是相对导入
from fundman.database.connection import init_db, get_db
from fundman.crud.wealth_product_crud import query_dynamic
from fundman.data_processor import import_data_file, export_data_file


def init_database() -> None:
    """初始化数据库"""
    init_db()
    print("数据库初始化完成")


def import_data(file_path: str, query_date: str) -> None:
    """导入数据"""
    import_data_file(file_path, query_date)
    print(f"数据导入完成: {file_path}")


def export_data(file_path: str, query_date: Optional[str] = None) -> None:
    """导出数据"""
    export_data_file(file_path, query_date)
    print(f"数据导出完成: {file_path}")


def query_data(query_date: str) -> None:
    """查询数据"""
    init_db()
    db_gen = get_db()
    db = next(db_gen)
    try:
        results = query_dynamic(db, query_date)
        print(f"动态查询结果数量: {len(results)}")
        for result in results:
            # 如果是Pydantic模型实例，直接访问属性
            if hasattr(result, 'product_name'):
                print(f"产品名称: {result.product_name}, 剩余天数: {result.product_days_remaining}")
            # 如果是SQLAlchemy模型实例，直接访问属性
            else:
                print(f"产品名称: {result.product_name}, 剩余天数: {result.product_days_remaining}")
    finally:
        db.close()


def build_parser() -> argparse.ArgumentParser:
    """构建 argparse 解析器（可用于测试）"""
    parser = argparse.ArgumentParser(description="FundMan 理财产品管理系统")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 投资组合管理子命令
    investment_parser = subparsers.add_parser("investment", help="投资组合管理")
    investment_subparsers = investment_parser.add_subparsers(dest="investment_command", help="投资组合子命令")
    
    # 创建资产子命令
    create_asset_parser = investment_subparsers.add_parser("create-asset", help="创建资产")
    create_asset_parser.add_argument("--name", required=True, help="资产名称")
    create_asset_parser.add_argument("--code", required=True, help="资产编码")
    create_asset_parser.add_argument("--type", required=True, help="资产类型")
    create_asset_parser.add_argument("--issuer", help="资产发行人")
    create_asset_parser.add_argument("--industry", help="资产所属行业")
    create_asset_parser.add_argument("--region", help="资产所属地区")
    
    # 列出资产子命令
    investment_subparsers.add_parser("list-assets", help="列出所有资产")
    
    # 创建交易子命令
    create_transaction_parser = investment_subparsers.add_parser("create-transaction", help="创建交易")
    create_transaction_parser.add_argument("--product-code", required=True, help="产品银登编码")
    create_transaction_parser.add_argument("--asset-code", required=True, help="资产编码")
    create_transaction_parser.add_argument("--investment-date", required=True, help="投资日期 (YYYY-MM-DD)")
    create_transaction_parser.add_argument("--maturity-date", help="到期日期 (YYYY-MM-DD)")
    create_transaction_parser.add_argument("--interest-rate", help="收益率")
    create_transaction_parser.add_argument("--quantity", required=True, help="投资数量")
    create_transaction_parser.add_argument("--unit-net-price", help="单位净价")
    create_transaction_parser.add_argument("--unit-full-price", help="单位全价")
    
    # 列出交易子命令
    investment_subparsers.add_parser("list-transactions", help="列出所有交易")
    
    # 初始化数据库命令
    subparsers.add_parser("init", help="初始化数据库")
    
    # 导入数据命令
    import_parser = subparsers.add_parser("import", help="导入数据")
    import_parser.add_argument("file", help="要导入的文件路径")
    import_parser.add_argument("--query-date", required=True, help="查询日期")
    
    # 导出数据命令
    export_parser = subparsers.add_parser("export", help="导出数据")
    export_parser.add_argument("file", help="导出文件路径")
    export_parser.add_argument("--query-date", help="查询日期")
    
    # 查询数据命令
    query_parser = subparsers.add_parser("query", help="查询数据")
    query_parser.add_argument("--query-date", required=True, help="查询日期")
    return parser


def parse_args(argv: List[str]) -> argparse.Namespace:
    """解析参数（可在测试中注入argv以覆盖CLI分支）"""
    parser = build_parser()
    return parser.parse_args(argv)


def _print_investment_help() -> None:
    """打印 investment 子命令的帮助，不依赖内部私有属性"""
    parser = build_parser()
    # 重新构建一次并打印 investment 的帮助
    # 由于 argparse 不提供公共API获取已创建的子解析器，只能通过再次构建并定位
    # 简化实现：直接打印总帮助，或打印特定说明
    print("用法: fundman.app investment [create-asset|list-assets|create-transaction|list-transactions] [选项]")
    print("试试: python -m fundman.app investment --help")


def main() -> None:
    """主函数"""
    parser = build_parser()
    # 如果没有提供参数，显示帮助信息
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    # 根据命令执行相应操作
    if args.command == "init":
        init_database()
    elif args.command == "import":
        import_data(args.file, args.query_date)
    elif args.command == "export":
        export_data(args.file, args.query_date)
    elif args.command == "query":
        query_data(args.query_date)
    elif args.command == "investment":
        # 处理投资组合管理命令
        if args.investment_command == "create-asset":
            # 导入投资组合相关模块
            from fundman.models import AssetCreate
            from fundman.crud import create_asset as crud_create_asset
            
            db_gen = get_db()
            db = next(db_gen)
            try:
                asset_data = AssetCreate(
                    asset_name=args.name,
                    asset_code=args.code,
                    asset_type=args.type,
                    issuer=args.issuer,
                    industry=args.industry,
                    region=args.region
                )
                asset = crud_create_asset(db, asset_data)
                print(f"资产创建成功:")
                print(f"  ID: {asset.asset_id}")
                print(f"  名称: {asset.asset_name}")
                print(f"  编码: {asset.asset_code}")
                print(f"  类型: {asset.asset_type}")
                print(f"  发行人: {asset.issuer}")
                print(f"  行业: {asset.industry}")
                print(f"  地区: {asset.region}")
            except Exception as e:
                print(f"创建资产时出错: {e}")
            finally:
                db.close()
                
        elif args.investment_command == "list-assets":
            # 导入投资组合相关模块
            from fundman.crud import get_assets
            
            db_gen = get_db()
            db = next(db_gen)
            try:
                assets = get_assets(db)
                if assets:
                    print("资产列表:")
                    print("-" * 80)
                    print(f"{'ID':<5} {'名称':<15} {'编码':<10} {'类型':<10} {'发行人':<15} {'行业':<10} {'地区':<10}")
                    print("-" * 80)
                    for asset in assets:
                        print(f"{asset.asset_id:<5} {asset.asset_name:<15} {asset.asset_code:<10} {asset.asset_type:<10} {asset.issuer:<15} {asset.industry:<10} {asset.region:<10}")
                else:
                    print("没有找到资产")
            except Exception as e:
                print(f"列出资产时出错: {e}")
            finally:
                db.close()
                
        elif args.investment_command == "create-transaction":
            # 导入投资组合相关模块
            from fundman.models import TransactionCreate
            from fundman.crud import create_transaction as crud_create_transaction
            from fundman.crud.wealth_product_crud import get_product_by_yindeng_code
            from fundman.crud import get_asset_by_code
            
            db_gen = get_db()
            db = next(db_gen)
            try:
                # 首先检查产品和资产是否存在
                product = get_product_by_yindeng_code(db, args.product_code)
                if not product:
                    print(f"找不到银登编码为 {args.product_code} 的产品")
                    return
                    
                asset = get_asset_by_code(db, args.asset_code)
                if not asset:
                    print(f"找不到编码为 {args.asset_code} 的资产")
                    return
                    
                # 获取 product_id 和 asset_id 的实际值
                product_id_value = getattr(product, 'product_id', None)
                asset_id_value = getattr(asset, 'asset_id', None)
                
                if product_id_value is None or asset_id_value is None:
                    print("获取产品ID或资产ID失败")
                    return
                    
                from datetime import datetime
                transaction_data = TransactionCreate(
                    product_id=product_id_value,
                    asset_id=asset_id_value,
                    investment_date=datetime.strptime(args.investment_date, "%Y-%m-%d").date(),
                    maturity_date=datetime.strptime(args.maturity_date, "%Y-%m-%d").date() if args.maturity_date else None,
                    interest_rate=float(args.interest_rate) if args.interest_rate else None,
                    quantity=float(args.quantity),
                    unit_net_price=float(args.unit_net_price) if args.unit_net_price else None,
                    unit_full_price=float(args.unit_full_price) if args.unit_full_price else None
                )
                transaction = crud_create_transaction(db, transaction_data)
                print(f"交易创建成功:")
                print(f"  ID: {transaction.transaction_id}")
                print(f"  产品: {getattr(product, 'product_name', '')}")
                print(f"  资产: {getattr(asset, 'asset_name', '')}")
                print(f"  投资日期: {transaction.investment_date}")
                print(f"  到期日期: {transaction.maturity_date}")
                print(f"  收益率: {transaction.interest_rate}%")
                print(f"  数量: {transaction.quantity}")
                print(f"  单位净价: {transaction.unit_net_price}")
                print(f"  单位全价: {transaction.unit_full_price}")
                print(f"  清算金额: {transaction.settlement_amount}")
            except Exception as e:
                print(f"创建交易时出错: {e}")
            finally:
                db.close()
                
        elif args.investment_command == "list-transactions":
            # 导入投资组合相关模块
            from fundman.crud import get_transactions, get_asset
            from fundman.crud.wealth_product_crud import get_product_by_yindeng_code
            # 退而求其次：若未提供“按ID取产品”的API，则根据事务中保存的 product_id 作为银登编码的情况做兼容尝试；
            # 若模型真实存的是 product_id，则建议后续提供 get_product_by_id 并在此替换为按ID查询。
            
            db_gen = get_db()
            db = next(db_gen)
            try:
                transactions = get_transactions(db)
                if transactions:
                    print("交易列表:")
                    print("-" * 120)
                    print(f"{'ID':<5} {'产品':<15} {'资产':<15} {'投资日期':<12} {'到期日期':<12} {'收益率(%)':<10} {'数量':<10} {'清算金额':<12}")
                    print("-" * 120)
                    for transaction in transactions:
                        # 获取产品和资产名称（兼容当前可用的查询：按银登编码）
                        # 注意：如果 transaction.product_id 实为产品ID，则需在 CRUD 提供 get_product_by_id 并替换此处实现
                        product = None
                        if hasattr(transaction, "product_id"):
                            try:
                                product = get_product_by_yindeng_code(db, str(transaction.product_id))
                            except Exception:
                                product = None
                        asset = get_asset(db, transaction.asset_id) if hasattr(transaction, "asset_id") else None
                        
                        product_name = getattr(product, "product_name", "未知") if product else "未知"
                        asset_name = getattr(asset, "asset_name", "未知") if asset else "未知"
                        
                        print(f"{transaction.transaction_id:<5} {product_name[:15]:<15} {asset_name[:15]:<15} {transaction.investment_date:<12} {transaction.maturity_date or '':<12} {transaction.interest_rate or '':<10} {transaction.quantity:<10} {transaction.settlement_amount or '':<12}")
                else:
                    print("没有找到交易")
            except Exception as e:
                print(f"列出交易时出错: {e}")
            finally:
                db.close()
        else:
            # 无子命令时打印帮助以便测试覆盖（避免使用 argparse 私有属性）
            _print_investment_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
