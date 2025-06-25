#!/usr/bin/env python3
"""
创建MySQL数据库用户 - 使用正确的密码哈希
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pymysql
from core.security import get_password_hash

def create_users():
    """创建用户账户"""
    try:
        # 连接到MySQL数据库
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='20010709',
            database='ai_syory',
            charset='utf8mb4'
        )
        
        print("✅ 连接到MySQL数据库成功")
        
        with connection.cursor() as cursor:
            # 删除现有用户
            cursor.execute("DELETE FROM user_settings")
            cursor.execute("DELETE FROM users")
            print("🗑️  清除现有用户数据")
            
            # 创建管理员用户
            admin_password_hash = get_password_hash("admin123")
            cursor.execute("""
                INSERT INTO users (username, email, hashed_password, full_name, is_active) 
                VALUES (%s, %s, %s, %s, %s)
            """, ('admin', 'admin@writingway.com', admin_password_hash, 'Administrator', True))
            
            admin_id = cursor.lastrowid
            print(f"👤 创建管理员用户: admin (ID: {admin_id})")
            
            # 创建演示用户
            demo_password_hash = get_password_hash("demo123")
            cursor.execute("""
                INSERT INTO users (username, email, hashed_password, full_name, is_active) 
                VALUES (%s, %s, %s, %s, %s)
            """, ('demo', 'demo@writingway.com', demo_password_hash, 'Demo User', True))
            
            demo_id = cursor.lastrowid
            print(f"👤 创建演示用户: demo (ID: {demo_id})")
            
            # 创建用户设置
            cursor.execute("""
                INSERT INTO user_settings (user_id, theme, language, font_size, auto_save, ai_settings) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (admin_id, 'light', 'en', 14, True, '{}'))
            
            cursor.execute("""
                INSERT INTO user_settings (user_id, theme, language, font_size, auto_save, ai_settings) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (demo_id, 'light', 'en', 14, True, '{}'))
            
            print("⚙️  创建用户设置完成")
            
            # 提交更改
            connection.commit()
            print("💾 数据保存成功")
            
            # 验证用户创建
            cursor.execute("SELECT id, username, email FROM users")
            users = cursor.fetchall()
            print("\n📝 创建的用户:")
            for user in users:
                print(f"   ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}")
                
    except Exception as e:
        print(f"❌ 创建用户时出错: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()
            print("🔌 MySQL连接已关闭")
    
    return True

if __name__ == "__main__":
    print("👥 创建MySQL数据库用户...")
    print("=" * 50)
    
    if create_users():
        print("\n🎉 用户创建完成！")
        print("\n🔑 登录信息:")
        print("管理员 - 用户名: admin, 密码: admin123")
        print("演示用户 - 用户名: demo, 密码: demo123")
    else:
        print("\n❌ 用户创建失败")
