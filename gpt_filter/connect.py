import mysql.connector
import pandas as pd
import json

# 数据库连接配置
db_config = {
    'host': 'localhost',  # 数据库主机
    'user': 'media_crawler',  # 数据库用户名
    'password': 'media_crawler',  # 数据库密码
    'database': 'media_crawler',  # 数据库名称
    'port': '3306'
}

# 创建数据库连接
connection = mysql.connector.connect(**db_config)

# 创建游标
cursor = connection.cursor(dictionary=True)

# SQL 查询
with open('../schema/connect_comments.sql', 'r') as file:
    sql_query = file.read()
    
# 执行查询
cursor.execute("""
SELECT 
    ct.comment_id,
    ct.content,
    ct.user_id,
    ct.nickname,
    ct.parent_comment_id,
    ct.create_time,
    aweme.aweme_id,
    aweme.title,
    aweme.desc,
    aweme.aweme_url
FROM 
    douyin_aweme_comment ct
JOIN 
    douyin_aweme aweme ON ct.aweme_id = aweme.aweme_id  -- 连接视频信息
ORDER BY 
    ct.create_time;  -- 按时间排序
""")

# 获取所有结果
comments_data = cursor.fetchall()

# 关闭游标和连接
cursor.close()
connection.close()

# 构建评论树
def build_comment_tree(comments):
    comment_map = {}
    for comment in comments:
        comment_map[comment['comment_id']] = {
            "comment_id": comment['comment_id'],
            "content": comment['content'],
            "user_id": comment['user_id'],
            "user_nickname": comment['nickname'],
            "comments": []
        }
    for comment in comments:
        if comment['parent_comment_id'] != "0":  # 只处理子评论
            comment_map[comment['parent_comment_id']]['comments'].append(comment_map[comment['comment_id']])
    return comment_map

# 创建DataFrame
rows = []
comment_map = build_comment_tree(comments_data)

for comment in comments_data:
    if comment['parent_comment_id'] == '0':  # 只处理父评论
        json_comments = json.dumps({"comments": comment_map[comment['comment_id']]}, ensure_ascii=False)
        row = {
            "视频名": comment['title'],
            "视频id": comment['aweme_id'],
            "用户id": comment['user_id'],
            "用户昵称": comment['nickname'],
            "视频详情页URL": comment['aweme_url'],
            "视频标题": comment['title'],
            "视频描述": comment['desc'],
            "视频评论": json_comments,
            "评论时间": comment['create_time']
        }
        rows.append(row)

# 创建DataFrame
df = pd.DataFrame(rows)
# 筛选时间在两年内的评论,评论时间是13位时间戳
df['评论时间'] = pd.to_datetime(df['评论时间'], unit='s')
df = df[df['评论时间'] > pd.Timestamp.now() - pd.Timedelta(days=730)]
df['评论时间'] = df['评论时间'].dt.strftime('%Y-%m-%d %H:%M:%S')
# 显示DataFrame
print(df)
# 保存为Excel文件
df.to_excel("comments_data.xlsx", index=False)