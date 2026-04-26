# 实时状态面板

维护一个可自动刷新的 HTML 状态面板，展示角色扮演的实时状态（HP/MP/EXP、时间、天气、位置、周围人物等）。

## 工作原理

```
Claude 每轮编辑 status.html 中的 STATE 对象
       ↓
浏览器每3秒自动刷新 (meta refresh)
       ↓
用户看到实时更新的游戏状态面板
```

## 文件

| 文件 | 说明 |
|------|------|
| `skills/styles/status.html` | 状态面板 HTML，嵌入 STATE 数据 + 渲染逻辑 |

## 操作流程

### 1. 启动面板

在浏览器中打开 `skills/styles/status.html`（可直接拖入浏览器，或用 `open` 命令）。

### 2. 每轮更新

Claude 在每次回复后，从 HTML 中找到 `const STATE = {` 区域，Edit 更新数据。

更新示例：场景推进到入学仪式后：
```javascript
const STATE = {
  world: "无职转生 - 六面世界",
  chapter: "第48章 - 入学第一天",
  time: "甲龙历421年4月15日 上午10时",
  weather: "🌬️ 微风",
  temp: "14℃",
  location: "拉诺亚魔法大学 · 校园广场",
  env: "新生聚集在广场，校长在讲台上压着假发",
  player: "鲁迪乌斯·格雷拉特",
  hp: 100, hpMax: 100,
  mp: 95, mpMax: 100,
  exp: 5, expMax: 100,
  ed: true,
  npcs: [
    { name: "艾莉娜丽洁", important: true },
    { name: "爱丽儿公主", important: true },
    { name: "菲兹", important: true },
    { name: "路克", important: false },
    { name: "札诺巴", important: false },
  ],
  quest: "参加入学仪式，认识新同学"
};
// ═══════════════
```

### 3. 更新原则

- 时间随剧情推进递增
- 天气可因剧情变化（下雨、起风、降温）
- HP/MP/EXP 仅在战斗中或明确消耗时变动
- npcs 列表：当前场景中的人物，「重要」标记当前剧情关键人物
- quest：当前角色的短期目标

## CSS 自定义

状态面板使用暗色主题，CSS 变量集中在 `:root`：
```css
:root {
  --bg: #0f0f1a;      /* 背景色 */
  --card: #1a1a2e;    /* 卡片色 */
  --accent: #6c63ff;  /* 强调色 */
  --text: #e0e0e0;    /* 文字色 */
}
```

## 适用场景

- 带数值系统的角色扮演（RPG、冒险、战斗）
- 需要追踪多角色状态的复杂剧情
- 长时间连载，需要回顾前情
