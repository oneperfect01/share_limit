# 根据车牌对share共享会话进行限速。
（每个用户单独根据车牌进行限速）


使用方式：

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

配置：
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

如果没有添加的车牌，默认为base

如果没有添加的模型，默认 20/3h

