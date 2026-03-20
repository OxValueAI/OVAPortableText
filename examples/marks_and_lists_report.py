"""
Example for Step 5 text features.
第 5 步文本能力示例。

This example demonstrates:
本示例演示：
1. native decorator marks / 原生装饰 marks
2. link markDefs / link markDefs
3. bullet / numbered lists / 无序与有序列表
"""

from ova_portable_text import (
    create_document,
    em,
    link_def,
    marked,
    section,
    span,
    strong,
    underline,
)


def build_demo():
    report = create_document(title="Marks and Lists Demo", language="en")

    intro = section(id="sec-text", level=1, title="Text Features")

    # ---------------------------------------------------------------
    # 1. A paragraph with native decorator marks.
    # 1. 使用原生 decorator marks 的段落。
    # ---------------------------------------------------------------
    intro.append_paragraph(
        "This paragraph contains ",
        strong("bold"),
        ", ",
        em("italic"),
        ", and ",
        underline("underlined"),
        " text.",
    )

    # ---------------------------------------------------------------
    # 2. A paragraph with a link mark definition.
    # 2. 使用 link mark definition 的段落。
    # ---------------------------------------------------------------
    intro.append_paragraph(
        "Visit ",
        span("OpenAI", marks=["m-link-openai"]),
        " for more information.",
        mark_defs=[
            link_def(
                key="m-link-openai",
                href="https://openai.com",
                title="OpenAI",
                open_in_new_tab=True,
            )
        ],
    )

    # ---------------------------------------------------------------
    # 3. Bullet and numbered lists.
    # 3. 无序列表与有序列表。
    # ---------------------------------------------------------------
    intro.append_subheading("Key points")
    intro.append_bullet_item("Portable Text native decorators can be reused directly.")
    intro.append_bullet_item("Link annotations live in markDefs and are referenced by key.")
    intro.append_number_item("First numbered step")
    intro.append_number_item("Second numbered step", level=1)
    intro.append_number_item("Nested numbered step", level=2)
    intro.append_bullet_item(marked("Mixed", "strong"), " list item is also supported.")

    report.append_section(intro)
    return report


if __name__ == "__main__":
    report = build_demo()
    report.assert_valid()
    print(report.to_json())
