import json
from datetime import datetime, timedelta

import pandas as pd
import asyncio

from joblib import Parallel, delayed
from openai import AsyncOpenAI

def process_chunk(df_chunk):
    async def async_process():
        try:
            oai_client = AsyncOpenAI(
                api_key="sk-e884df8670e544a8b7d0c765760f2c19",  # 需替换为实际的 API 密钥
                base_url="https://api.deepseek.com/beta/v1",
            )
            # 从 Excel 文件中读取数据
            async def load_comments(df:pd.DataFrame):
                video_info = df[["视频标题", "视频描述"]].drop_duplicates().to_dict(orient="records")
                # 判断是否和生信或者科学作图有关
                prompt = """请判断以下视频的标题和详情是否和生信或者科学作图有关，如果是，请输出如下json对象:
                {
                    "index": 0,
                    "is_relevant": true
                }
                如果不是，请输出:
                {
                    "index": 0,
                    "is_relevant": false
                }
                """
                results = set()
                def handle_video_info(video_info,index):
                    return f"<video_info>index: {index}\n标题: {video_info['视频标题']}\n描述: {video_info['视频描述']} </video_info>"
                # 使用 asyncio.gather 并发处理视频信息
                tasks = [
                    asyncio.create_task(
                        deepseek_chat(prompt, video_info=handle_video_info(video_info=video_info[i],index=i))
                    )
                    for i in range(len(video_info))
                ]
                await asyncio.gather(*tasks)
                for task in tasks:
                    response = task.result()
                    response = json.loads(response)
                    if response["is_relevant"]:
                        results.add(video_info[response["index"]]["视频标题"])

                print(f"共找到 {len(results)} 个相关视频")
                return df[df["视频标题"].isin(results)]


            async def filter_comments(prompt, comment_data):
                results = []

                # 使用 thread_map 创建一个并发的进度条
                tasks = [
                    asyncio.create_task(filter_comment(prompt, row))
                    for _, row in comment_data.iterrows()
                ]
                # 等待所有任务完成
                await asyncio.gather(*tasks)

                # 将结果合并到大列表中
                for task in tasks:
                    if task.result():
                        results.extend(task.result())

                return results


            async def filter_comment(prompt, row):
                video_info = f"<video_info>标题: {row['视频标题']} \n id: {row['视频id']} \n 描述: {row['视频描述']} </video_info>"
                comments = f"<comments> {row['视频评论']} </comments>"
                response = await deepseek_chat(
                    prompt, comment=comments, video_info=video_info
                )
                related_comments = json.loads(response)["related_comments"]

                return related_comments


            # 调用 deepseek-chat API
            async def deepseek_chat(prompt, video_info, comment=""):
                try:
                    response = await oai_client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": prompt},
                            {"role": "user", "content": video_info + "\n" + comment},
                        ],
                        response_format={"type": "json_object"},
                        temperature=0.0,
                    )
                    if response:
                        return response.choices[0].message.content
                    else:
                        return json.dumps({"error": "Empty response"})
                except Exception as e:
                    return json.dumps({"error": str(e)})


            # 主函数
            async def main(df):
                prompt = """对于json格式的评论树中的每个评论节点，根据视频信息和节点中的content判断是否和生物信息的求助有关，如果有关把评论节点相关信息添加到返回的列表中:
                Example:
                有相关评论，请输出如下json对象：
                {
                    related_comments:[
                        {
                            '视频id': '123456',
                            '用户昵称': '张三',
                            '评论ID':  '7890',
                            '视频评论content':'请问如何进行基因表达量的分析？'
                        },
                        {
                            '视频id': '123456',
                            '用户昵称': '李四',
                            '评论ID':  '7891',
                            '视频评论content': '呜呜呜，大佬能帮我看看这个代码哪里错了吗？'
                        }
                    ]
                }
                没有相关评论：
                {
                    related_comments:[]
                }
                """
                comment_data = await load_comments(df=df)
                filtered_comments = await filter_comments(prompt, comment_data)
                # 保存到csv文件
                import pandas as pd

                df = pd.DataFrame(filtered_comments)
                return df
            result = await main(df_chunk)
            return result.to_dict('records')
        except Exception as e:
            return {"error": str(e)}
    return asyncio.run(async_process())
# 运行主程序
if __name__ == "__main__":
    df = pd.read_excel("comments_data.xlsx")
    # 根据"视频标题", "视频描述"进行分组,然后以组为单位进行累加，每次累加到25%，用一个新的list保存
    # 初始化一个新的dataframe，用于存储累加后的数据
    dfs = []
    grouped_data = df.groupby(["视频标题", "视频描述"])
    new_df = pd.DataFrame()
    limit = int(0.25 * len(df))
    # 遍历分组后的数据
    for name, group in grouped_data:
        # 计算当前组的大小
        group_size = len(group)

        # 如果当前组的大小超过25%，将其添加到dfs中
        if len(new_df)+group_size > limit:
            dfs.append(new_df)
            new_df = pd.DataFrame()
        # 将当前组添加到新的dataframe中
        new_df = pd.concat([new_df, group])

    with Parallel(n_jobs=-1) as pool:
        results = pool(delayed(process_chunk)(df_chunk) for df_chunk in dfs)

    # 处理结果，过滤掉错误
    valid_results = []
    for result in results:
        if isinstance(result, list):
            valid_results.extend(result)
        elif isinstance(result, dict) and 'error' in result:
            print(f"Error in chunk processing: {result['error']}")

    # 将所有有效结果合并成一个DataFrame
    merged_result = pd.DataFrame(valid_results)
    
    # 连接总表，根据视频id查询视频详情页URL
    # merged_result = pd.read_csv("merged_filtered_comments2.csv")
    merged_result = pd.merge(merged_result, df[["视频id", "视频详情页URL","评论时间"]], on="视频id", how="left").drop_duplicates(subset=['评论ID'])
    merged_result['评论时间'] = pd.to_datetime(merged_result['评论时间'])
    # 筛选两年以内的评论
    merged_result = merged_result[merged_result['评论时间'] > datetime.now() - timedelta(days=730)]
    # 保存到CSV文件
    merged_result.to_csv("merged_filtered_comments2.csv", index=False, header=True)
    
