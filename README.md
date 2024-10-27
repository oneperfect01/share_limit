# 根据车牌对share共享会话进行限速。
（每个用户单独根据车牌进行限速）


## 使用方式：
一、 与share一起部署
```
cd  你的share docker-compose的路径
wget https://raw.githubusercontent.com/oneperfect01/share_limit/main/config.json
```
修改docker-compose文件

1、把原来的auditlimit镜像地址修改了，在映射一个文件路径
```
  auditlimit:
    image: opaochat/shar_list:latest
    restart: always
    volumes:
      - ./config.json:/app/config.json
    labels:
      - "com.centurylinklabs.watchtower.scope=xyhelper-chatgpt-share-server"
```
2、把chatgpt-share-server环境变量的限速url修改一下
```
AUDIT_LIMIT_URL: "http://auditlimit:41758/limit"
```

二、单独部署
### docker compose
```
git clone https://github.com/oneperfect01/share_limit.git
cd share_limit
docker compose pull && docker compose  up  -d
```
###  docker
```
git clone https://github.com/oneperfect01/share_limit.git
cd share_limit
docker run -d  --name share_limit -v ./config.json:/app/config.json -p 41758:41758  opaochat/shar_list:latest
```


接口地址：
```
http://你的ip:41758/limit
```
参见
https://github.com/cockroachai/auditlimit

## 配置：
config.json
```
{
    "base": {
      "auto": "5/10m",
      "gpt-4o": "5/30m",
      "gpt-4o-canmore": "20/3h",
      "o1-preview": "7/7d",
      "o1-mini": "7/24h",
      "gpt-4o-mini": "3/3m",
      "gpt-4": "20/3h"
    },
    "plus": {
      "auto": "200/3h",
      "gpt-4o": "40/3h",
      "gpt-4o-canmore": "20/3h",
      "o1-preview": "7/7d",
      "o1-mini": "7/24h",
      "gpt-4o-mini": "100/3h",
      "gpt-4": "20/3h"
    }
  }
```
plus/base   代表你车牌的前四位字符。后面是模型



后面可以自行增加。
也就是说根据车牌的前四位字符进行统一限速。共用一个限速器

如果车牌没有添加，则默认使用base

如果模型没有添加，默认限速 20/3h

