# MySQL数据库设置指南 - ai_syory

## 📋 概述

这个指南将帮你为Writingway项目设置MySQL数据库 `ai_syory`。

## 🗄️ 数据库结构

### 主要表格
- **users** - 用户账户信息
- **projects** - 写作项目
- **documents** - 文档内容（支持层次结构）
- **compendium_entries** - 世界观设定
- **user_settings** - 用户偏好设置
- **ai_conversations** - AI对话历史

### 特性
- ✅ UTF8MB4字符集支持（支持emoji和特殊字符）
- ✅ 外键约束确保数据完整性
- ✅ 索引优化查询性能
- ✅ 示例数据预装
- ✅ 视图和存储过程
- ✅ 层次化文档结构

## 🚀 安装步骤

### 1. 准备MySQL环境

确保你已经安装了MySQL 8.0+：

```bash
# macOS (使用Homebrew)
brew install mysql
brew services start mysql

# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql

# Windows
# 下载并安装MySQL Installer
```

### 2. 创建数据库用户（可选）

```sql
-- 连接到MySQL
mysql -u root -p

-- 创建专用用户
CREATE USER 'writingway_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON ai_syory.* TO 'writingway_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. 执行SQL脚本

```bash
# 方法1: 使用命令行
mysql -u root -p < ai_syory_mysql_schema.sql

# 方法2: 在MySQL客户端中
mysql -u root -p
source /path/to/ai_syory_mysql_schema.sql;

# 方法3: 使用MySQL Workbench
# 打开MySQL Workbench，连接到服务器，然后打开并执行SQL文件
```

### 4. 验证安装

```sql
-- 检查数据库
SHOW DATABASES LIKE 'ai_syory';

-- 检查表
USE ai_syory;
SHOW TABLES;

-- 检查示例数据
SELECT * FROM users;
SELECT * FROM projects;
```

## 🔧 配置Writingway后端

### 更新backend/.env文件

```env
# 将SQLite配置替换为MySQL
DATABASE_URL=mysql+pymysql://writingway_user:your_secure_password@localhost:3306/ai_syory

# 其他配置保持不变
SECRET_KEY=your-secret-key-change-in-production
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### 安装MySQL Python驱动

```bash
cd backend
source venv/bin/activate
pip install pymysql cryptography
```

### 更新SQLAlchemy配置

在 `backend/database/database.py` 中：

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

# MySQL引擎配置
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # 设为True可以看到SQL查询日志
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 📊 默认账户

安装完成后，你可以使用以下账户登录：

### 管理员账户
- **用户名**: `admin`
- **密码**: `admin123`
- **邮箱**: admin@writingway.com

### 演示账户
- **用户名**: `demo`
- **密码**: `demo123`
- **邮箱**: demo@writingway.com

## 🔍 有用的SQL查询

### 查看项目统计
```sql
SELECT * FROM project_statistics;
```

### 获取用户的所有项目
```sql
CALL GetUserProjects(2);  -- 用户ID为2的项目
```

### 获取项目的所有文档
```sql
CALL GetProjectDocuments(1);  -- 项目ID为1的文档
```

### 查看活跃项目
```sql
SELECT * FROM active_projects;
```

## 🛠️ 维护命令

### 备份数据库
```bash
mysqldump -u root -p ai_syory > ai_syory_backup.sql
```

### 恢复数据库
```bash
mysql -u root -p ai_syory < ai_syory_backup.sql
```

### 查看表大小
```sql
SELECT 
    TABLE_NAME as '表名',
    TABLE_ROWS as '行数',
    ROUND(DATA_LENGTH/1024,2) as '数据大小(KB)',
    ROUND(INDEX_LENGTH/1024,2) as '索引大小(KB)'
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'ai_syory' 
ORDER BY DATA_LENGTH DESC;
```

## 🚨 故障排除

### 连接问题
1. 检查MySQL服务是否运行
2. 验证用户名和密码
3. 确认防火墙设置
4. 检查MySQL配置文件中的bind-address

### 字符集问题
确保MySQL配置支持UTF8MB4：
```sql
SHOW VARIABLES LIKE 'character_set%';
SHOW VARIABLES LIKE 'collation%';
```

### 权限问题
```sql
SHOW GRANTS FOR 'writingway_user'@'localhost';
```

## 📞 支持

如果遇到问题：
1. 检查MySQL错误日志
2. 验证SQL脚本执行结果
3. 测试数据库连接
4. 查看Writingway应用日志

---

**注意**: 请确保在生产环境中使用强密码并定期备份数据库！
