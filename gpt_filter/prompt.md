表结构如下
```sql
DROP TABLE IF EXISTS `douyin_aweme`;
CREATE TABLE `douyin_aweme`
(
    `id`              int         NOT NULL AUTO_INCREMENT COMMENT '自增ID',
    `user_id`         varchar(64)  DEFAULT NULL COMMENT '用户ID',
    `sec_uid`         varchar(128) DEFAULT NULL COMMENT '用户sec_uid',
    `short_user_id`   varchar(64)  DEFAULT NULL COMMENT '用户短ID',
    `user_unique_id`  varchar(64)  DEFAULT NULL COMMENT '用户唯一ID',
    `nickname`        varchar(64)  DEFAULT NULL COMMENT '用户昵称',
    `avatar`          varchar(255) DEFAULT NULL COMMENT '用户头像地址',
    `user_signature`  varchar(500) DEFAULT NULL COMMENT '用户签名',
    `ip_location`     varchar(255) DEFAULT NULL COMMENT '评论时的IP地址',
    `add_ts`          bigint      NOT NULL COMMENT '记录添加时间戳',
    `last_modify_ts`  bigint      NOT NULL COMMENT '记录最后修改时间戳',
    `aweme_id`        varchar(64) NOT NULL COMMENT '视频ID',
    `aweme_type`      varchar(16) NOT NULL COMMENT '视频类型',
    `title`           longtext DEFAULT NULL COMMENT '视频标题',
    `desc`            longtext COMMENT '视频描述',
    `create_time`     bigint      NOT NULL COMMENT '视频发布时间戳',
    `liked_count`     varchar(16)  DEFAULT NULL COMMENT '视频点赞数',
    `comment_count`   varchar(16)  DEFAULT NULL COMMENT '视频评论数',
    `share_count`     varchar(16)  DEFAULT NULL COMMENT '视频分享数',
    `collected_count` varchar(16)  DEFAULT NULL COMMENT '视频收藏数',
    `aweme_url`       varchar(255) DEFAULT NULL COMMENT '视频详情页URL',
    PRIMARY KEY (`id`),
    KEY               `idx_douyin_awem_aweme_i_6f7bc6` (`aweme_id`),
    KEY               `idx_douyin_awem_create__299dfe` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='抖音视频';

-- ----------------------------
-- Table structure for douyin_aweme_comment
-- ----------------------------
DROP TABLE IF EXISTS `douyin_aweme_comment`;
CREATE TABLE `douyin_aweme_comment`
(
    `id`                int         NOT NULL AUTO_INCREMENT COMMENT '自增ID',
    `user_id`           varchar(64)  DEFAULT NULL COMMENT '用户ID',
    `sec_uid`           varchar(128) DEFAULT NULL COMMENT '用户sec_uid',
    `short_user_id`     varchar(64)  DEFAULT NULL COMMENT '用户短ID',
    `user_unique_id`    varchar(64)  DEFAULT NULL COMMENT '用户唯一ID',
    `nickname`          varchar(64)  DEFAULT NULL COMMENT '用户昵称',
    `avatar`            varchar(255) DEFAULT NULL COMMENT '用户头像地址',
    `user_signature`    varchar(500) DEFAULT NULL COMMENT '用户签名',
    `ip_location`       varchar(255) DEFAULT NULL COMMENT '评论时的IP地址',
    `add_ts`            bigint      NOT NULL COMMENT '记录添加时间戳',
    `last_modify_ts`    bigint      NOT NULL COMMENT '记录最后修改时间戳',
    `comment_id`        varchar(64) NOT NULL COMMENT '评论ID',
    `aweme_id`          varchar(64) NOT NULL COMMENT '视频ID',
    `content`           longtext COMMENT '评论内容',
    `create_time`       bigint      NOT NULL COMMENT '评论时间戳',
    `sub_comment_count` varchar(16) NOT NULL COMMENT '评论回复数',
    PRIMARY KEY (`id`),
    KEY                 `idx_douyin_awem_comment_fcd7e4` (`comment_id`),
    KEY                 `idx_douyin_awem_aweme_i_c50049` (`aweme_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='抖音视频评论';
ALTER TABLE `douyin_aweme_comment`
   ADD COLUMN `parent_comment_id` VARCHAR(64) DEFAULT NULL COMMENT '父评论ID';
```
要求以父评论为起点，递归查询出所有子评论，包括子评论的子评论，并按照评论时间排序，最终返回所有评论的评论ID和评论内容以及用户ID和用户昵称，最后返回一个json格式的数据，例子如下：
```json
{
  "comments": [
    {
      "comment_id": "234567890",
      "content": "这是另一条评论",
      "user_id": "123456789",
      "user_nickname": "用户昵称",
      "comments": [
        {
          "comment_id": "345678901",
          "content": "这是第一条子评论",
          "user_id": "123456789",
          "user_nickname": "用户昵称",
          "comments": []
        },
        {
          "comment_id": "456789012",
          "content": "这是第二条子评论",
          "user_id": "987654321",
          "user_nickname": "用户昵称",
          "comments": []
        }
      ]
    }
  ]
}
```

最后返回一个dataframe，表头为视频名，视频id，用户id，用户昵称，视频详情页URL，视频标题，视频描述，视频评论（前面的json字符串）表格如下,注意，每个评论json只包含一个父评论，也就是只有一个根节点
| 视频名 | 视频id | 用户id | 用户昵称 | 视频详情页URL | 视频标题 | 视频描述 | 视频评论 |
| ------ | ------ | ------ | -------- | -------------- | -------- | -------- | -------- |
