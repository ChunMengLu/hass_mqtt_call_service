# home assistant mqtt call_service 插件

## 安装
- 拷贝 `custom_components` 目录下的 `mqtt_call_service` 到 `.homeassistant/custom_components/mqtt_call_service`

## 配置
在 `configuration.yaml` 中添加配置：

```yaml
# mqtt call service
mqtt_call_service:
  # 订阅 mqtt 中的 topic
  subscribe_topic: ha/event/subscribe
```

## 发送 mqtt 消息

**topic:**

`ha/event/subscribe`

**payload:**
```json
{
	"domain": "light",
	"service": "turn_off",
	"service_data": {
		"entity_id": "light.deerma_jsq3_9885_indicator_light"
	}
}
```

## 说明

本项目基于 [mqtt_eventstream](https://github.com/home-assistant/core/tree/dev/homeassistant/components/mqtt_eventstream) 改造，如果遇到不兼容的问题，请按对应的版本代码进行微调。