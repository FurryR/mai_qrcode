# Maimai QR Code

> 启发自 [QRmai](https://github.com/SodaCodeSave/QRmai)，基于 Docker + Linux Wechat 的舞萌二维码获取器

## 优点

- 隔离 / 完全容器化，不需要使用宿主机的微信
- 并发 / 基于 FastAPI + asyncio 的异步 API，在高并发情况下也工作正常
- 极简 / 无任何额外接口，直接返回字符串，且不需要根据机器类型配置文件

## 注意事项

- 不直接兼容 MaimaiHelper (为什么服务器要负责二维码生成?)
- 不应当将 5900 端口映射到外网。无论如何也需要这样做的情况，请考虑设置防火墙规则，并修改 entrypoint.sh 以使用 VNC 密码认证
- 由于微信的限制，登录可能会在一段时间后失效，需要手动检修
- 仅支持 x86_64 / aarch64 架构的机器
- 公众号聊天窗口需以独立窗口打开

## 使用方法

1. `docker compose up -d`
2. 使用 VNC 访问 `localhost:5900`，无密码
3. 登录微信（若出现闪退请多试几次，进程将自动重启）
4. 点击联系人，找到 `公众号 -> 舞萌|中二`，右键点击“发消息”（无需调整窗口，你也无法调整）
5. 使用 `localhost:8000` 访问 API
6. 将 `8000` 端口映射到外网即可在其它设备中使用。

端口可以在 `compose.yml` 中自由调整。
可以在 `app/.env` 中修改 token。修正后，需要重启容器。

## 接口说明

### GET `/v1/request?token={token}`

- token 和 `app/.env` 中的 `TOKEN` 相同。
- 返回值如下：

| 键      | 类型    | 描述                            |
| ------- | ------- | ------------------------------- |
| code    | number  | 状态码，200 表示成功            |
| message | string  | 状态信息，200 的情况下为空      |
| data    | string? | 二维码字符串，未成功时为 `null` |

- 可能的错误信息：

| 错误信息                    | 描述                           | 解决方案      |
| --------------------------- | ------------------------------ | ------------- |
| Forbidden                   | token 错误                     | N/A           |
| Window not found            | 微信未按“使用说明”配置或掉登录 | 登录 VNC 检修 |
| Internal Server Error       | X11 session 错误               | 重启容器      |
| Timeout waiting for QR code | 华立服务器超时或微信异常       | 登录 VNC 检修 |

## 开源协议

MIT License.
