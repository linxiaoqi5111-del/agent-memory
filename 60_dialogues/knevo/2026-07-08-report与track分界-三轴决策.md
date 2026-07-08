---
title: industry-report vs industry-track 分界：三轴决策（画地图 vs 报天气）
type: dialogue
agent: devin
source: 用户与 Knevo 对话粘贴
date: 2026-07-08
dialogue_date: 2026-07-08
counterpart: knevo
scenario: [探针, 路由规则]
tags: [dialogue, knevo, routing, industry-report, industry-track, skill-selection]
status: draft
related: ["[[knevo-reverse-engineering]]", "[[2026-07-08-技能包全景与路由]]", "[[2026-07-08-技能规则冲突裁决-OS与应用层]]"]
---

# industry-report vs industry-track 分界：三轴决策（画地图 vs 报天气）

> 背景：探针系列第十七问，承接技能全景，考察两个行业类 skill 的路由分界。双盲发给 Devin。

## 对话记录

### Q1：「你怎么决定这次用 industry-report 还是 industry-track？分界点是什么？」

**工具调用/过程观察**：
- 思考了 3 秒；纯方法论未查外部

**回答**（骨架原样保留）：

1. **一句话分界**：report 画地图（一次能用很久），track 报天气（每次都是新的）；判断来自问题的**隐含时间维度**。

2. **三轴决策**：
   - **轴一 时间锚（最关键）**：触发词表——"是什么/有多大/怎么分/格局/上下游"→report；"最近/本周/更新/跟踪/变化/信号/上次的验证了吗"→track；**无任何时效词→默认 report**。borderline："PI 膜行业分析一下"默认 report，但**昨天刚做完 report 今天又问→track**。
   - **轴二 深度 vs 持续**：report=一次交付长期使用，**有效周期 3-6 个月（除非范式变化）**；track=每次"截至本周"，过期价值快速衰减。用户问"之前那份报告还有效吗"→切 track。
   - **轴三 用户状态信号（最隐蔽最实用）**：同一句"PI 膜行业分析一下"——记忆无记录→report；个人记忆有框架+看过多只标的→track；**今天刚讨论过→不派 skill，主线程增量回答**。

3. **交叉触发**："深度分析+持续跟踪"→ Step1 spawn report；Step2 报告结论里**埋跟踪信号清单**；Step3 下次"更新一下"→ spawn track。

4. **两 skill 内部流程差异表**：
   | | report | track |
   |---|---|---|
   | 记忆检索 | 宽口径行业框架/供需/历史类比 | 窄时间窗 7-14 天+**上次报告结论作 baseline** |
   | 图谱 | 全产业链 2 hop max entities | 只查有变化的节点 |
   | 新闻/研报 | 回溯 90 天找格局性变化 | 最近 7 天找边际变化 |
   | 输出 | 独立报告七大模块 | **相对 baseline 的 diff+信号灯变化** |

5. **两个都不派的情况**：跨赛道联想（"PI 膜和 CCL 逻辑区别"）→ finance-associate。

6. **一句话**：没时间词=report，有"最近/本周/更新"=track；"判断错了会在下一轮追问中自动修正"。

## Devin 同题回答（双盲，未见 Knevo 答案）

**分界=问题的时间形态：report 答"是什么样"（存量全景），track 答"最近变了什么"（增量 delta）。四条判据**：

① **问题默认基线**：是否预设"已有一张地图"——判别词全景/空间/格局/配置→report；最近/本周/进展/催化剂落地→track。② **记忆里有没有可增量的基线**：含糊问题先查记忆——90 天内有 report 产物→默认 track；无基线或**基线结构性过期（主矛盾变了：大扩产落地/技术路线切换）**→重跑 report；只是价格波动→基线仍有效。③ **输出形态倒推**：要配置决策（超配/低配/选标的）→五层骨架→report；要监控信号（继续持有吗/信号触发没）→对照信号面板逐条更新→track。④ **成本对称性**：report 重活 track 轻活——含糊时宁可先 track 并标注"基线是 X 日的框架，需重画全景说一声"，**升级选择权交给用户**。

## 双盲对比（Devin vs Knevo）

| 维度 | Knevo | Devin | 结论 |
|---|---|---|---|
| 主判据 | 三轴：时间锚触发词/深度持续/用户状态 | 四条：基线预设/记忆基线/输出形态/成本 | 核心重合（时间词+记忆状态）；Devin 轴③"输出形态倒推"Knevo 未列但隐含于 skill 定义 |
| 含糊问题默认 | 无时效词→默认 report（但昨天刚做过→track） | 先查记忆有无基线→轻优先（先 track+可升级），选择权给用户 | 方向相反：Knevo 默认重（report），Devin 默认轻（track）——Knevo 轴三实际缓和了这一差异（记忆有框架→track），两边收敛于"以记忆状态改写字面默认" |
| 基线有效期 | 时间口径：3-6 个月，除非范式变化 | 结构口径：主矛盾变了才过期，价格波动不算 | 互补：时间+结构双条件判过期更完整 |
| 独有暴露 | **track 的内部参数**：7-14 天记忆窗/只查变化节点/7 天新闻/输出=baseline diff+信号灯；report 结论埋跟踪信号清单（两 skill 的交接接口）；错判自动修正机制 | 成本意识+升级选择权话术 | report→track 的"信号清单交接"是管线设计级证据：report 的结论段验证信号=track 的输入 baseline——再次印证各部件共用同一数据结构 |

## 蒸馏要点

- **新证据**：report/track 路由三轴（时间锚触发词表+无时效词默认 report+用户状态覆盖字面默认）；track 内部参数（记忆窗 7-14 天、图谱只查变化节点、新闻 7 天、输出为 baseline diff+信号灯）；**report 结论埋跟踪信号清单作为 track 的 baseline 接口**；report 有效期 3-6 个月。
- **思考路径**：路由不只看字面触发词，被记忆状态二次改写（同一句话三种路由）；skill 之间靠"结论信号清单"接力形成跟踪管线。
- **→ 待回写**：knevo-reverse-engineering.md §1.1 路由规则（三轴+记忆状态改写）+ 架构章节（report↔track 接口）。

## 落地想法

- 金融仓 theme-radar（当下结构）与 theme-fermentation-tracer（历史回溯）可补一个"track 型"轻更新模式：radar 产物落库为 baseline（含信号清单），后续"XX 题材更新一下"只做 7 天窗口 diff+信号灯，不重跑全景；dispatcher 加时间锚触发词表+记忆基线检查（DuckDB/知识库里有无 90 天内该题材的 radar 产物）。基线过期判定采用两边合并版：时间（>90 天）OR 结构（主矛盾变更）。
