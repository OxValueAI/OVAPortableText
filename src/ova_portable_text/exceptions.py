from __future__ import annotations

"""
Validation-related exception and report models for OVAPortableText.
OVAPortableText 的校验异常与报告模型。

This file is intentionally part of the public API.
本文件刻意作为公开 API 的一部分。

Why?
为什么？
Because validation is not only an internal implementation detail.
因为校验并不只是内部实现细节。
For this package, validation is one of the core user-facing workflows:
对本包而言，校验本身就是核心对外工作流之一：
- build a document / 构建文档
- inspect a structured validation report / 查看结构化校验报告
- optionally fail fast / 必要时快速抛错中止

Step 8 extends the report so issues carry more maintenance-friendly context,
which is especially useful when the user later debugs large report documents.
第 8 步进一步扩展了报告结构，让 issue 带有更多便于维护的上下文；
当后续调试大型报告文档时，这会非常有帮助。
"""

from collections import Counter
from typing import Literal

from pydantic import Field

from .base import OvaBaseModel


class ValidationIssue(OvaBaseModel):
    """
    One validation issue found in the document.
    文档中发现的一条校验问题。

    Besides the basic code / message / path fields,
    Step 8 also carries optional context that helps users quickly locate the
    problematic semantic object.
    除了基础的 code / message / path 字段外，
    第 8 步还补充了若干可选上下文字段，便于用户快速定位出问题的语义对象。

    Common examples / 常见示例：
    - which section the issue belongs to / 属于哪个 section
    - which object id or anchor is involved / 涉及哪个对象 id 或 anchor
    - what kind of object it is / 它属于哪种对象类型
    - what to try next / 建议下一步怎么修
    """

    code: str
    message: str
    path: str | None = None
    severity: Literal["error", "warning"] = "error"

    # Maintenance-oriented context fields.
    # 面向维护与调试的上下文字段。
    location: str | None = None
    contextType: str | None = None
    contextId: str | None = None
    contextAnchor: str | None = None
    sectionId: str | None = None
    sectionTitle: str | None = None
    suggestion: str | None = None

    def to_text(self) -> str:
        """
        Render one issue as a compact human-readable line.
        将单条 issue 渲染为便于人工阅读的简洁文本。
        """
        pieces: list[str] = [f"[{self.severity.upper()}] [{self.code}] {self.message}"]
        if self.path:
            pieces.append(f"path={self.path}")
        if self.sectionId:
            section_text = self.sectionId
            if self.sectionTitle:
                section_text += f" ({self.sectionTitle})"
            pieces.append(f"section={section_text}")
        if self.contextType:
            pieces.append(f"contextType={self.contextType}")
        if self.contextId:
            pieces.append(f"contextId={self.contextId}")
        if self.contextAnchor:
            pieces.append(f"contextAnchor={self.contextAnchor}")
        if self.suggestion:
            pieces.append(f"suggestion={self.suggestion}")
        return " | ".join(pieces)


class ValidationReport(OvaBaseModel):
    """
    Structured validation report for an entire document.
    整份文档的结构化校验报告。

    Design intent / 设计意图：
    - keep the raw issue list machine-friendly / 保持 issue 列表机器可读
    - but also offer direct summary helpers / 同时提供直接可用的摘要 helper
    - so the report can be used in tests, logs, CLI output, or notebooks
      从而既可用于测试，也可用于日志、CLI 输出或 notebook 调试
    """

    isValid: bool = True
    issues: list[ValidationIssue] = Field(default_factory=list)

    def add_issue(
        self,
        *,
        code: str,
        message: str,
        path: str | None = None,
        severity: Literal["error", "warning"] = "error",
        location: str | None = None,
        contextType: str | None = None,
        contextId: str | None = None,
        contextAnchor: str | None = None,
        sectionId: str | None = None,
        sectionTitle: str | None = None,
        suggestion: str | None = None,
    ) -> "ValidationReport":
        """
        Append one issue into the report.
        向报告中追加一条问题记录。

        `location` defaults to `path` when omitted.
        若未显式提供 `location`，则默认回退到 `path`。
        """
        self.issues.append(
            ValidationIssue(
                code=code,
                message=message,
                path=path,
                severity=severity,
                location=location or path,
                contextType=contextType,
                contextId=contextId,
                contextAnchor=contextAnchor,
                sectionId=sectionId,
                sectionTitle=sectionTitle,
                suggestion=suggestion,
            )
        )
        if severity == "error":
            self.isValid = False
        return self

    @property
    def is_valid(self) -> bool:
        """
        Python-friendly alias for `isValid`.
        提供一个更符合 Python 命名习惯的 `isValid` 别名。

        Why keep both names?
        为什么同时保留两个名字？
        - `isValid` matches the JSON-facing protocol field shape.
          `isValid` 对齐 JSON / 协议输出字段风格。
        - `is_valid` feels more natural when the report is used as a Python object.
          当把报告当作 Python 对象使用时，`is_valid` 更顺手。
        """
        return self.isValid

    @property
    def error_count(self) -> int:
        """
        Number of issues with severity = error.
        严重级别为 error 的问题数量。
        """
        return sum(1 for issue in self.issues if issue.severity == "error")

    @property
    def warning_count(self) -> int:
        """
        Number of issues with severity = warning.
        严重级别为 warning 的问题数量。
        """
        return sum(1 for issue in self.issues if issue.severity == "warning")

    def codes(self) -> list[str]:
        """
        Return issue codes in order.
        按原顺序返回全部 issue code。
        """
        return [issue.code for issue in self.issues]

    def counts_by_code(self) -> dict[str, int]:
        """
        Return a frequency mapping grouped by code.
        返回按 code 聚合的出现次数映射。
        """
        return dict(Counter(self.codes()))

    def to_text(self, *, include_warnings: bool = True) -> str:
        """
        Render the whole report into a readable multi-line string.
        将整份报告渲染为便于阅读的多行文本。
        """
        lines = [
            "OVAPortableText validation report:",
            f"isValid={self.isValid}",
            f"errors={self.error_count}",
            f"warnings={self.warning_count}",
        ]
        for idx, issue in enumerate(self.issues, start=1):
            if issue.severity == "warning" and not include_warnings:
                continue
            lines.append(f"{idx}. {issue.to_text()}")
        return "\n".join(lines)

    def raise_for_errors(self) -> "ValidationReport":
        """
        Raise `DocumentValidationError` if the report is invalid.
        若报告包含错误，则抛出 `DocumentValidationError`。
        """
        if not self.isValid:
            raise DocumentValidationError(self)
        return self


class DocumentValidationError(ValueError):
    """
    Exception raised when document validation fails.
    当文档校验失败时抛出的异常。
    """

    def __init__(self, report_or_issues: ValidationReport | list[ValidationIssue]):
        if isinstance(report_or_issues, ValidationReport):
            self.report = report_or_issues
            self.issues = report_or_issues.issues
            message = report_or_issues.to_text(include_warnings=True)
        else:
            self.issues = report_or_issues
            self.report = ValidationReport(isValid=False, issues=report_or_issues)
            message = self.report.to_text(include_warnings=True)
        super().__init__(message)
