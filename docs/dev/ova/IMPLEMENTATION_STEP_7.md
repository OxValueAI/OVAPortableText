# OVAPortableText Step 7

## 本步目标

本步按前一阶段计划，重点完成两类工作：

1. **validator / resolver 再增强一轮**
2. **把顶层占位字段再补一点强类型模型**

同时继续保持：

- 中英文双语注释
- 每次改动后跑测试
- 对照正式协议做自查

---

## 本步新增能力概览

### 1. 顶层 registry 强类型扩展

之前主要强类型覆盖：

- `assets.images`
- `datasets.tables`
- `datasets.charts`（pie）
- `bibliography`
- `footnotes`
- `glossary`

本步新增轻量强类型覆盖：

- `assets.logos`
- `assets.backgrounds`
- `assets.icons`
- `assets.attachments`
- `datasets.metrics`

新增模型：

- `StaticAssetBase`
- `LogoAsset`
- `BackgroundAsset`
- `IconAsset`
- `AttachmentAsset`
- `MetricValue`
- `MetricDataset`

这样与协议中已冻结的顶层 bucket 设计更一致。

---

### 2. Document 顶层 append API 扩充

`Document` 现在新增：

- `add_logo_asset(...)`
- `add_background_asset(...)`
- `add_icon_asset(...)`
- `add_attachment_asset(...)`
- `add_metric_dataset(...)`

这样使用体验继续保持“创建对象 -> append 到 document”的统一风格。

---

### 3. 新增 helper 工厂函数

新增对外 helper：

- `logo_asset(...)`
- `background_asset(...)`
- `icon_asset(...)`
- `attachment_asset(...)`
- `metric_value(...)`
- `metric_dataset(...)`

这些 helper 与现有的：

- `image_asset(...)`
- `table_dataset(...)`
- `pie_chart_dataset(...)`

保持同一风格。

---

### 4. Resolver 增强

`DocumentResolver` 本步增强了：

#### 4.1 索引更多 registry 类型

新增可解析目标：

- `logo_asset`
- `background_asset`
- `icon_asset`
- `attachment_asset`
- `metric_dataset`

#### 4.2 增加 anchor 索引

新增：

- `targetsByAnchor`
- `duplicateAnchors`
- `get_by_anchor(anchor_value)`

这为后续：

- 页内跳转
- 目录 / 图表目录
- PDF 书签
- anchor 冲突检测

提供更稳的底层支持。

#### 4.3 targetType 支持表统一集中维护

新增：

- `is_supported_target_type(...)`
- `supported_target_types()`

并将 target type alias 表统一收敛到 resolver 内部。

#### 4.4 继续保持语义 alias

继续支持协议要求的语义引用：

- `image` / `chart` -> `figure`
- `math_block` -> `equation`

---

### 5. Validator 增强

本步 validator 新增或增强了以下规则：

#### 5.1 duplicate anchor 检测

- 若全局 anchor 冲突，记录 `duplicate_anchor`
- 当前作为 **warning**，不直接把文档判为 invalid

这样既能提示潜在渲染跳转风险，又不会过早把文档判死。

#### 5.2 unsupported xref target type 检测

新增：

- `unsupported_xref_target_type`

如果 `xref.targetType` 不在当前 resolver 支持范围内，会直接报错，而不是仅仅给出“解析不到”。

#### 5.3 footnotes 结构增强校验

新增：

- `empty_footnote_blocks`

符合协议中“`footnotes[].blocks` 不应为空”的建议。

#### 5.4 bibliography 协议建议提示

新增 warning：

- `empty_bibliography_authors`
- `missing_bibliography_year`

注意：这两项当前是 **warning**，不是硬错误。
原因是：

- 协议建议 `authors` 不应为空、`year` 建议提供
- 但当前已有较多最简 demo / legacy helper 输入只传 `text`
- 若立即升级成 error，会让已有示例和开发体验过于生硬

因此当前采用：

- **协议方向对齐**
- **暂时保持向后兼容**

---

## 与协议的对齐情况

本步重点对齐了这些协议点：

1. 顶层 `assets` bucket：
   - `images`
   - `logos`
   - `backgrounds`
   - `icons`
   - `attachments`

2. 顶层 `datasets` bucket：
   - `charts`
   - `tables`
   - `metrics`

3. 所有可被引用对象应具备统一可解析入口

4. `xref.targetType` 属于语义层 / resolver 统一别名层，而不是简单等于对象 `_type`

5. `footnotes[].blocks` 不应为空

6. `bibliography` 条目建议带 `authors` 与 `year`

---

## 本步新增测试

新增测试文件：

- `tests/test_extended_registries_and_resolver.py`
- `tests/test_validator_extended_rules.py`

覆盖点包括：

1. 扩展 registry 能否正确序列化
2. resolver 能否解析新增 registry 类型
3. duplicate anchor 是否作为 warning 返回
4. 空 footnote blocks 是否报错
5. unsupported xref target type 是否报错

---

## 本步新增示例

新增示例：

- `examples/extended_registries_demo.py`

演示：

- logo
- background
- icon
- attachment
- metric dataset

的创建与导出。

---

## 测试结果

本步最终测试结果：

```bash
22 passed
```

---

## 下一步建议

下一步建议进入：

1. **继续增强 validator / resolver 的上下文报错能力**
2. **开始逐步准备 README / 用法文档 / 完整样例矩阵**
3. **补一轮更系统的测试矩阵**

这样就会逐渐进入你计划里的后半程：

- 文档
- 用法样例
- 测试矩阵
- 你回测
- 修 bug
- 打包发布
