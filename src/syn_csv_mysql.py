import csv
import mysql.connector
from mysql.connector import Error


# 数据库连接配置
db_config = {
    'host': 'localhost',      # MySQL 服务器地址
    'port': 3306,              # 端口
    'user': 'root',            # 用户名
    'password': 'supersonic', # 密码 (请替换)
    'database': 'biz_db', # 数据库名 (请替换)
    'charset': 'utf8mb4'       # 字符集
}

# CSV 文件路径
csv_file_path = 'C:/Users/86193/Desktop/data/天猫.csv'


# 数据库表列名 (fact_trade)，顺序必须与下方INSERT语句中的顺序完全一致
db_columns = [
    'user_id', 'user_name', 'product_id', 'product_name',
    'product_category', 'product_price', 'order_time', 'order_quantity',
    'order_amount', 'user_city', 'user_gender', 'user_age'
]

try:
    # 1. 建立数据库连接
    print("正在连接数据库...")
    conn = mysql.connector.connect(**db_config)
    if conn.is_connected():
        print("数据库连接成功！")
        cursor = conn.cursor()

        # 2. 读取并处理CSV文件 (使用 'utf-8-sig' 编码自动处理BOM)
        print(f"正在读取CSV文件: {csv_file_path}")
        with open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
            csv_reader = csv.reader(csvfile)
            header = next(csv_reader)  # 读取第一行作为表头
            print(f"检测到表头: {header}")

            # 3. 构建SQL插入语句
            columns = ", ".join(db_columns)
            placeholders = ", ".join(["%s"] * len(db_columns))
            insert_query = f"INSERT INTO fact_trade ({columns}) VALUES ({placeholders})"
            print("构建的插入SQL已准备就绪。")

            # 4. 批量执行插入
            print("开始执行批量插入...")
            batch_size = 1000  # 每1000条提交一次
            batch = []
            count = 0

            for row in csv_reader:
                # 跳过空行
                if not any(row):
                    continue
                # 确保CSV行的长度与数据库列数匹配
                if len(row) != len(db_columns):
                    print(f"警告: 跳过不匹配的行 (列数: {len(row)} vs {len(db_columns)}): {row}")
                    continue
                batch.append(row)
                if len(batch) >= batch_size:
                    cursor.executemany(insert_query, batch)
                    conn.commit()
                    count += len(batch)
                    print(f"已成功插入 {count} 条记录 (批量提交)")
                    batch = []

            # 插入剩余的记录
            if batch:
                cursor.executemany(insert_query, batch)
                conn.commit()
                count += len(batch)
                print(f"已成功插入剩余的 {len(batch)} 条记录")

            print(f"数据导入完成！总计成功插入 {count} 条记录。")

except Error as e:
    print(f"数据库操作发生错误: {e}")
finally:
    # 5. 关闭连接
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
        print("数据库连接已关闭。")