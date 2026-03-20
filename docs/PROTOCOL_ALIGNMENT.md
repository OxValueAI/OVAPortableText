# Protocol Alignment Notes

This file explains the current alignment between the package and Report Profile v1.0.
本文档说明当前包实现与 Report Profile v1.0 协议的对齐边界。

## Currently aligned

- top-level `schemaVersion / meta / theme / assets / datasets / bibliography / footnotes / glossary / sections`
- section-tree-first structure
- text blocks and spans
- approved v1 text styles
- inline refs and block objects
- registry-first references for images / tables / charts
- pie chart as the currently formalized chart dataset type
- validation and resolver base layer

## Intentionally not expanded yet

- non-pie chart detailed schemas
- Java renderer style contracts
- PDF pagination / page-level layout fields
- theme visual details
