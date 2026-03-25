#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate a protocol-oriented sample JSON from 样例1.docx content,
using OVAPortableText as the primary construction layer.

生成基于《样例1.docx》的协议样例 JSON。
主结构尽可能使用 OVAPortableText 构建；对于当前包尚未提供正式 helper 的部分
（例如 grid table 与少量协议演示块），在最终导出阶段做轻量后处理。

Usage / 用法:
    python generate_sample1_protocol_demo.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Optional local-source fallback for development.
# 本地开发时可通过环境变量指向源码目录。
OVAPT_SRC = None
if OVAPT_SRC and Path(OVAPT_SRC).exists():
    sys.path.insert(0, str(Path(OVAPT_SRC)))

from ova_portable_text import (
    create_document,
    paragraph,
    image_asset_url,
    image_asset_embedded,
    image_block,
    chart_block,
    table_block,
    math_block,
    callout,
    footnote_entry,
    glossary_entry,
    bibliography_entry,
    pie_slice,
    pie_chart_dataset,
    table_column,
    table_dataset,
    metric_dataset,
    metric_value,
)

TINY_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jrR0AAAAASUVORK5CYII="


def make_grid_table(id_: str, label: str, column_count: int, rows: list[dict], anchor: str | None = None, meta: dict | None = None) -> dict:
    return {
        "id": id_,
        "anchor": anchor or id_,
        "label": label,
        "meta": meta or {},
        "tableType": "grid",
        "columnCount": column_count,
        "rows": rows,
    }


def find_section(node_list: list[dict], target_id: str) -> dict | None:
    for sec in node_list:
        if sec["id"] == target_id:
            return sec
        for item in sec.get("body", []):
            if item.get("itemType") == "subsection":
                found = find_section([item["section"]], target_id)
                if found:
                    return found
    return None


def build_document():
    doc = create_document(
        title="专利估值分析报告（协议样例）",
        subtitle="基于样例1.docx 改写，并补充协议能力展示区",
        language="zh-CN",
        strict_ids=True,
        documentType="report",
        author="OVAPortableText Sample Generator",
        reportNumber="SAMPLE-2026-02-09",
        generatedAt="2026-02-09T12:00:00Z",
        generatedBy="OVAPortableText v0.1.3 demo script",
        clientName="斑马智行网络(香港)有限公司",
        projectId="demo-patent-report-sample1",
        confidentiality="internal",
        reportType="valuation",
        locale="zh-CN",
        source="样例1.docx",
    )
    doc.schemaVersion = "report.v1.0"

    # theme
    doc.theme.name = "oxvalue-report"
    doc.theme.styleTemplate = "formal-report"
    doc.theme.pageTemplateFamily = "valuation-report"
    doc.theme.brandAssetRefs = ["logo-primary", "icon-accent"]
    doc.theme.coverTemplateRef = "bg-cover"

    # images
    doc.add_image_asset(
        image_asset_url(
            id="img-model-system",
            url="assets/images/model-system.png",
            alt="牛津智能专利价值评估系统示意图",
            label="Valuation system diagram",
            mimeType="image/png",
            width=1200,
            height=675,
            checksum="sha256:demo-model-system",
        )
    )
    doc.add_image_asset(
        image_asset_embedded(
            id="img-company-qr",
            data_base64=TINY_PNG_B64,
            mime_type="image/png",
            alt="公司公众号二维码占位图",
            label="Company QR placeholder",
            width=128,
            height=128,
            checksum="sha256:demo-qr-placeholder",
        )
    )

    # bibliography
    bib_entries = [
        dict(id="cite-fu-2026", type="article", title="Digitalization of International Trade in Intellectual Properties: A Perspective Based on a Utility Theory of Technology Value", authors=["Fu, X.", "Zhang, J.", "Ai, C.", "Fu, X."], year=2026, journal="World Economy", displayText="Fu et al. (2026). Digitalization of International Trade in Intellectual Properties. World Economy, forthcoming."),
        dict(id="cite-bessen-2008", type="article", title="The Value of U.S. Patents by Owner and Patent Characteristics", authors=["Bessen, J."], year=2008, journal="Research Policy", volume="37", issue="5", pages="932-945", displayText="Bessen, J. (2008). The Value of U.S. Patents by Owner and Patent Characteristics. Research Policy, 37(5), 932-945."),
        dict(id="cite-gb-42728-2023", type="report", title="专利评估指引（GB/T 42728-2023）", authors=["国家市场监督管理总局", "国家标准化管理委员会"], year=2023, institution="中国国家标准", displayText="《专利评估指引》（GB/T 42728-2023）。"),
        dict(id="cite-wipo-dataset", type="dataset", title="WIPO Patent Data Collections", authors=["WIPO"], year=2026, url="https://www.wipo.int", displayText="WIPO Patent Data Collections."),
        dict(id="cite-oxvalue-site", type="webpage", title="OxValue.AI Official Website", authors=["OxValue.AI"], year=2026, url="https://www.oxvalue.ai/", accessedAt="2026-02-09T12:00:00Z", displayText="OxValue.AI Official Website."),
        dict(id="cite-tech-valuation-book", type="book", title="Assessing the Value of Your Technology", authors=["Tipping, J. W.", "Zeffren, E.", "Fusfeld, A. R."], year=1995, publisher="Research-Technology Management", displayText="Tipping, Zeffren & Fusfeld (1995). Assessing the Value of Your Technology."),
        dict(id="cite-other-demo", type="other", title="Internal modeling note", authors=["OVAPortableText Demo"], year=2026, displayText="OVAPortableText Demo (2026). Internal modeling note."),
    ]
    for b in bib_entries:
        doc.add_bibliography_entry(bibliography_entry(**b))

    # footnotes & glossary
    doc.add_footnote(
        footnote_entry(
            id="fn-report-scope",
            blocks=[
                paragraph("本样例中的数值、图表与表格内容仅用于协议演示，不构成真实估值结论。"),
                paragraph("表格中的 grid / record 双模式用于展示协议能力边界。", style="smallprint"),
            ],
            label="Footnote 1",
        )
    )
    doc.add_footnote(
        footnote_entry(
            id="fn-caption-policy",
            blocks=[
                paragraph("当前协议推荐图题注、表题注、公式题注作为相邻文本块表达，而不是内嵌到对象字段中。")
            ],
            label="Footnote 2",
        )
    )
    doc.add_glossary_entry(glossary_entry(id="term-dcf", term="DCF", definition="Discounted Cash Flow", aliases=["Discounted Cash Flow"], label="DCF"))
    doc.add_glossary_entry(glossary_entry(id="term-pct", term="PCT", definition="Patent Cooperation Treaty", aliases=["专利合作条约"], label="PCT"))

    # charts
    doc.add_chart_dataset(
        pie_chart_dataset(
            id="chart-factor-overall",
            label="专利价值驱动因素总体特征",
            value_unit="percent",
            slices=[
                pie_slice(key="novelty", zh="技术新颖性", en="Technical novelty", value=34, description_zh="整体贡献最高", description_en="Highest contribution"),
                pie_slice(key="lifecycle", zh="技术生命周期", en="Technology lifecycle", value=27, description_zh="贡献次高", description_en="Second highest"),
                pie_slice(key="market", zh="市场与团队", en="Market and team", value=22, description_zh="中等贡献", description_en="Medium contribution"),
                pie_slice(key="legal", zh="法律价值与风险", en="Legal value and risk", value=17, description_zh="相对较低", description_en="Relatively lower contribution"),
            ],
        )
    )
    doc.add_chart_dataset(
        pie_chart_dataset(
            id="chart-overview-driver",
            label="估值概要中的价值驱动因素",
            value_unit="percent",
            slices=[
                pie_slice(key="novelty", zh="技术新颖性", en="Technical novelty", value=38, description_zh="核心贡献来源", description_en="Core driver"),
                pie_slice(key="lifecycle", zh="技术生命周期", en="Technology lifecycle", value=24, description_zh="重要辅助因素", description_en="Important secondary factor"),
                pie_slice(key="market", zh="市场与团队", en="Market and team", value=21, description_zh="与商业落地相关", description_en="Commercialization related"),
                pie_slice(key="legal", zh="法律价值与风险", en="Legal value and risk", value=17, description_zh="风险调节项", description_en="Risk adjustment"),
            ],
        )
    )

    # record tables
    doc.add_table_dataset(
        table_dataset(
            id="table-legal-status",
            label="法律状态信息",
            columns=[
                table_column(key="date", header="法律状态公告日"),
                table_column(key="status", header="法律状态"),
                table_column(key="details", header="详细信息"),
            ],
            rows=[
                {"date": "20151223", "status": "公开", "details": "公开"},
                {"date": "20160120", "status": "实质审查的生效", "details": "实质审查的生效 IPC(主分类): H04M 3/487；申请日：20140529"},
                {"date": "20201211", "status": "专利申请权、专利权的转移", "details": "登记生效日：20201130；变更前申请人：阿里巴巴集团控股有限公司；变更后申请人：斑马智行网络(香港)有限公司。"},
                {"date": "20210507", "status": "授权", "details": "授权"},
            ],
        )
    )
    citation_rows = [
        {"index": 1, "content": "引证类别：A；公开(公告)号：CN119247024A；公开(公告)日：20250103；申请号：CN202411223548.2；申请日：20240903；标题：基于分解降噪和新型卷积神经网络的故障测距方法和系统；申请人：国网吉林省电力有限公司电力科学研究院等；IPC：G01R31/08; G06N3/0464; G06N3/08。"},
        {"index": 2, "content": "引证类别：A；公开(公告)号：CN119247024A；公开(公告)日：20250103；申请号：CN202411223548.2；申请日：20240903；标题：基于分解降噪和新型卷积神经网络的故障测距方法和系统；申请人：国网吉林省电力有限公司电力科学研究院等；IPC：G01R31/08; G06N3/0464; G06N3/08。"},
    ]
    doc.add_table_dataset(
        table_dataset(
            id="table-forward-citations",
            label="引证信息",
            columns=[table_column(key="index", header="序号"), table_column(key="content", header="引用被评专利的后续专利")],
            rows=citation_rows,
        )
    )
    doc.add_table_dataset(
        table_dataset(
            id="table-backward-citations",
            label="被引证信息",
            columns=[table_column(key="index", header="序号"), table_column(key="content", header="被引证专利")],
            rows=citation_rows,
        )
    )

    # metrics demo
    doc.add_metric_dataset(
        metric_dataset(
            id="metric-demo-overview",
            label="展示用指标集",
            values=[
                metric_value(key="remaining_life_years", value=8, label="剩余保护年限", unit="year"),
                metric_value(key="legal_status", value="有效", label="法律状态"),
                metric_value(key="family_scope", value="CN only", label="同族布局"),
            ],
        )
    )

    # sections
    cover = doc.new_section(id="front-cover", level=1, title="封面", numbering="none")
    cover.append_paragraph("专利估值分析报告", style="lead")
    cover.append_paragraph("专利号：CN201410234381.X")
    cover.append_paragraph("专利名称：一种呼叫请求处理的方法和装置")
    cover.append_paragraph("报告生成日期（评估基准日）：2026-02-09")
    cover.append_blocks(
        image_block(id="fig-cover-system", image_ref="img-model-system"),
        paragraph("图：牛津智能专利价值评估系统（封面展示图）", style="figure_caption"),
    )

    summary = doc.new_section(id="front-summary", level=1, title="估值概要", numbering="none")
    summary.append_paragraph("本节根据样例文档中的概要页生成。表格采用 grid 模式以保留跨列排布；饼图作为相邻 figure 呈现。", style="smallprint")
    summary.append_blocks(
        table_block(id="tbl-summary-overview", table_ref="table-summary-overview"),
        paragraph("表：估值概要（grid 示例，含跨列单元格）", style="table_caption"),
        chart_block(id="fig-overview-driver", chart_ref="chart-overview-driver"),
        paragraph("图：估值概要中的价值驱动因素分布", style="figure_caption"),
    )

    toc = doc.new_section(id="front-toc", level=1, title="目录", numbering="none")
    for line in [
        "封面 …… 1",
        "估值概要 …… 2",
        "目录 …… 3",
        "1. 专利价值评估方法 …… 4",
        "2. 专利基本信息 …… 5",
        "3. 专利价值驱动因素总体特征 …… 9",
        "4. 专利价值驱动因素——技术新颖性 …… 10",
        "附录 …… 11",
    ]:
        toc.append_paragraph(line)

    sec1 = doc.new_section(id="sec-method", level=1, title="专利价值评估方法", numbering="auto")
    sec1.append_paragraph("本次专利价值评估基于牛津智能自主研发的专利价值评估系统。", style="lead")
    sec1.append_bullet_items(
        "技术新颖性：重点评估原创性、先进性、适用范围与影响力。",
        "技术生命周期阶段：分析技术所处阶段、成熟度与未来发展态势。",
        "技术效用规模：评估市场应用空间、竞争格局以及专利运营情况。",
        "法律价值与风险：分析权利稳定性、保护范围及潜在风险。",
    )
    sec1.append_paragraph("上述指标体系与《专利评估指引》（GB/T 42728-2023）保持一致，从而确保评估方法的规范性与合规性。")
    sec1.append_blocks(
        image_block(id="fig-system-overview", image_ref="img-model-system"),
        paragraph("图1 牛津智能专利价值评估系统", style="figure_caption"),
    )
    sec1.append_paragraph("专利估值模型可表示为：")
    sec1.append_blocks(
        math_block(id="eq-core-model", latex="V = f(X; \\theta)"),
        paragraph("式1 估值模型示意表达", style="equation_caption"),
    )
    sec1.append_callout(
        callout(
            id="callout-method-highlights",
            blocks=[
                paragraph("相较于传统成本法、收益法、市场法，本评估体系具有系统性、数据驱动与可重复性优势。"),
                paragraph("该结果用于商业参考与内部研判，不构成交易价格承诺。", style="smallprint"),
            ],
        )
    )

    sec2 = doc.new_section(id="sec-basic", level=1, title="专利基本信息", numbering="auto")
    sub21 = sec2.new_subsection(id="sec-basic-biblio", title="著录项目信息")
    sub21.append_blocks(
        table_block(id="tbl-biblio-grid", table_ref="table-biblio-info"),
        paragraph("表：著录项目信息（grid 示例，含多处跨列）", style="table_caption"),
    )
    sub22 = sec2.new_subsection(id="sec-basic-legal", title="法律状态信息")
    sub22.append_blocks(
        table_block(id="tbl-legal-status", table_ref="table-legal-status"),
        paragraph("表：法律状态信息（record 示例）", style="table_caption"),
    )
    sub23 = sec2.new_subsection(id="sec-basic-classification", title="专利分类信息")
    sub23.append_blocks(
        table_block(id="tbl-classification-grid", table_ref="table-classification"),
        paragraph("表：专利分类信息（grid 示例，含 rowSpan）", style="table_caption"),
    )
    sub24 = sec2.new_subsection(id="sec-basic-citations", title="专利引证信息")
    sub241 = sub24.new_subsection(id="sec-basic-citations-forward", title="引证信息")
    sub241.append_blocks(
        table_block(id="tbl-forward-citations", table_ref="table-forward-citations"),
        paragraph("表：引证信息（record 示例）", style="table_caption"),
    )
    sub242 = sub24.new_subsection(id="sec-basic-citations-backward", title="被引证信息")
    sub242.append_blocks(
        table_block(id="tbl-backward-citations", table_ref="table-backward-citations"),
        paragraph("表：被引证信息（record 示例）", style="table_caption"),
    )
    sub25 = sec2.new_subsection(id="sec-basic-claims", title="权利要求信息")
    sub25.append_number_items(
        "一种呼叫请求处理的方法，其特征在于，包括接收查询请求、依据用户ID查询订单信息和/或物流信息，并将查询响应发送给终端。",
        "如权利要求1所述的方法，其特征在于，还包括根据物流信息进一步匹配电话号码并返回关联信息。",
        "如权利要求2所述的方法，其特征在于，订单信息查询由多数据库联合完成。",
    )
    sub25.append_paragraph("其余权利要求从略，样例中仅保留部分内容以突出协议结构。", style="smallprint")

    sec3 = doc.new_section(id="sec-factor-overall", level=1, title="专利价值驱动因素总体特征", numbering="auto")
    sec3.append_paragraph("被评专利估值主要由技术新颖性、技术生命周期、市场与团队因素，以及法律价值与风险共同驱动。")
    sec3.append_blocks(
        chart_block(id="fig-factor-overall", chart_ref="chart-factor-overall"),
        paragraph("图：专利价值驱动因素总体特征（pie 示例）", style="figure_caption"),
    )
    sec3.append_paragraph("整体而言，技术新颖性与技术生命周期是最敏感的两个维度；相关指标的提升或下降都可能对未来估值产生较为明显的影响。")

    sec4 = doc.new_section(id="sec-novelty", level=1, title="专利价值驱动因素——技术新颖性", numbering="auto")
    sub41 = sec4.new_subsection(id="sec-novelty-interpretation", title="评价结果及解读")
    sub41.append_paragraph("该因素评估专利技术的原创性、独特性、适用范围的多样性、技术覆盖面以及影响力等。")
    sub41.append_paragraph("对于被评专利，技术新颖性在估值中贡献比例较高，说明这一因素是专利估值的核心来源。")
    sub42 = sec4.new_subsection(id="sec-novelty-advanced", title="技术先进性")
    sub421 = sub42.new_subsection(id="sec-novelty-problem", title="技术问题重要性")
    sub421.append_paragraph("同族专利的地理覆盖范围可在一定程度上反映专利权人为保护相关技术所投入的研发与专利布局成本。")
    sub421.append_paragraph("被评专利仅在中国市场进行了专利布局，未见对应的 PCT 国际申请或其他国家/地区同族专利。该布局模式表明其技术重要性目前主要体现为区域性。")

    appendix = doc.new_section(id="appendix-root", level=1, title="附录", numbering="none")
    app1 = appendix.new_subsection(id="appendix-model", title="模型介绍")
    app1.append_paragraph("模型介绍部分可补充“关于我们”、方法来源与核心参考文献。", style="subheading")
    app1.append_paragraph("本样例同时用 bibliography 顶层 registry 存储完整参考文献信息，并在附录中提供可读清单。")
    app1.append_paragraph("参考文献：", style="subheading")
    for b in bib_entries[:6]:
        app1.append_paragraph(b["displayText"])
    app2 = appendix.new_subsection(id="appendix-data", title="数据来源说明")
    for txt in [
        "全球专利著录项目数据、法律状态数据、同族专利数据、专利引证数据、专利全文文本等，主要来源于 WIPO、USPTO、EPO、JPO、KIPO、CNIPA 等官方数据库及第三方专利数据库。",
        "中国专利复审无效宣告数据来源于国家知识产权局公开数据及第三方专利数据库。",
        "知识产权海关备案、标准必要专利、专利池、专利代理机构信用等数据，经 OxValue.AI 加工整理形成。",
    ]:
        app2.append_bullet_item(txt)
    app3 = appendix.new_subsection(id="appendix-disclaimer", title="免责条款与使用限制声明")
    for txt in [
        "本报告由 OxValue.AI 基于特定估值模型与数据算法自动生成，仅供商业参考与内部研判之用。",
        "估值结果不代表被评专利在真实公开市场上的实际可变现价值、拍卖成交价或未来收益保障。",
        "因依赖本报告内容而作出的商业决策、投资行为、许可交易或法律诉讼，其后果由使用者自行承担。",
    ]:
        app3.append_number_item(txt)
    app4 = appendix.new_subsection(id="appendix-copyright", title="知识产权与版权声明")
    app4.append_paragraph("本评估报告的全部内容，包括文字表述、数据指标体系、核心算法与估值模型逻辑、分析框架、图表及呈现形式，均属 OxValue.AI 享有完整所有权及著作权的专有智力成果。")
    app4.append_paragraph("引用或转载必须严格遵守授权边界，并在引用处清晰注明“数据/内容来源：OxValue.AI（牛津智能）”。", style="blockquote")
    app4.append_paragraph("—— OxValue.AI 法务与内容治理团队", style="quote_source")

    demo = doc.new_section(id="sec-capability-demo", level=1, title="协议能力展示区", numbering="manual")
    demo.append_paragraph("本节为样例补充，用于集中展示协议与包的主要能力。", style="lead")
    demo.append_paragraph("下面将额外展示 marks、markDefs、grid table、embedded image、caption 风格、callout、footnote、glossary、inline math 等能力。", style="smallprint")
    demo.append_paragraph("非正式小标题示例", style="subheading")
    demo.append_paragraph("这是一个通用 caption 样式示例。", style="caption")

    back = doc.new_section(id="back-cover", level=1, title="封底", numbering="none")
    back.append_paragraph("公司网址：")
    back.append_paragraph("中国版：https://www.oxvalue.cn/")
    back.append_paragraph("英文版：https://www.oxvalue.ai/")
    back.append_blocks(
        image_block(id="fig-company-qr", image_ref="img-company-qr"),
        paragraph("公司公众号二维码", style="figure_caption"),
    )

    return doc, bib_entries


def normalize_to_protocol_json(doc, bib_entries):
    data = doc.model_dump(by_alias=True, exclude_none=True)
    data["schemaVersion"] = "report.v1.0"

    # record tables gain explicit tableType
    for tbl in data["datasets"]["tables"]:
        tbl.setdefault("tableType", "record")

    # grid tables
    data["datasets"]["tables"].extend([
        make_grid_table(
            "table-summary-overview",
            "估值概要",
            4,
            [
                {"cells": [{"text": "被评专利", "header": True}, {"text": "CN201410234381.X\n一种呼叫请求处理的方法和装置", "colSpan": 3}]},
                {"cells": [{"text": "专利类型", "header": True}, {"text": "发明专利"}, {"text": "当前法律状态", "header": True}, {"text": "有效"}]},
                {"cells": [{"text": "申请日", "header": True}, {"text": "20140529"}, {"text": "申请号", "header": True}, {"text": "CN201410234381.X"}]},
                {"cells": [{"text": "首次公开日", "header": True}, {"text": "20151223"}, {"text": "申请公布号", "header": True}, {"text": "CN105187676A"}]},
                {"cells": [{"text": "授权公告日", "header": True}, {"text": "20210507"}, {"text": "授权公告号", "header": True}, {"text": "CN105187676B"}]},
                {"cells": [{"text": "预估到期日", "header": True}, {"text": "20340529"}, {"text": "剩余保护年限", "header": True}, {"text": "8年"}]},
                {"cells": [{"text": "申请人", "header": True}, {"text": "斑马智行网络(香港)有限公司"}, {"text": "申请人地址", "header": True}, {"text": "中国香港九龙长沙湾道788号罗氏商业广场6楼603室"}]},
                {"cells": [{"text": "当前权利人", "header": True}, {"text": "斑马智行网络(香港)有限公司"}, {"text": "当前权利人地址", "header": True}, {"text": "中国香港九龙长沙湾道788号罗氏商业广场6楼603室"}]},
                {"cells": [{"text": "发明人", "header": True}, {"text": "李丽鸿", "colSpan": 3}]},
                {"cells": [{"text": "主分类号", "header": True}, {"text": "H04M3/487", "colSpan": 3}]},
                {"cells": [{"text": "估计总价值", "header": True}, {"text": "根据国家有关评估的法律法规，本着客观、独立、公正、科学的原则，按照 OxValue.AI 估值方法，被评专利价值估算结果为：\n1809918 CNY — 2448713 CNY\n（评估基准日 2026年2月23日）", "colSpan": 3}]},
                {"cells": [{"text": "专利价值驱动因素", "header": True}, {"text": "图表见下方 figure；此处保留与原文档一致的版面占位含义。", "colSpan": 3}]},
            ],
        ),
        make_grid_table(
            "table-biblio-info",
            "著录项目信息",
            4,
            [
                {"cells": [{"text": "被评专利", "header": True}, {"text": "CN201410234381.X\n一种呼叫请求处理的方法和装置", "colSpan": 3}]},
                {"cells": [{"text": "专利类型", "header": True}, {"text": "发明专利"}, {"text": "当前法律状态", "header": True}, {"text": "有效"}]},
                {"cells": [{"text": "申请日", "header": True}, {"text": "20140529"}, {"text": "申请号", "header": True}, {"text": "CN201410234381.X"}]},
                {"cells": [{"text": "首次公开日", "header": True}, {"text": "20151223"}, {"text": "申请公布号", "header": True}, {"text": "CN105187676A"}]},
                {"cells": [{"text": "授权公告日", "header": True}, {"text": "20210507"}, {"text": "授权公告号", "header": True}, {"text": "CN105187676B"}]},
                {"cells": [{"text": "预估到期日", "header": True}, {"text": "20340529"}, {"text": "剩余保护年限", "header": True}, {"text": "8年"}]},
                {"cells": [{"text": "申请人", "header": True}, {"text": "斑马智行网络(香港)有限公司"}, {"text": "申请人地址", "header": True}, {"text": "中国香港九龙长沙湾道788号罗氏商业广场6楼603室"}]},
                {"cells": [{"text": "当前权利人", "header": True}, {"text": "斑马智行网络(香港)有限公司"}, {"text": "当前权利人地址", "header": True}, {"text": "中国香港九龙长沙湾道788号罗氏商业广场6楼603室"}]},
                {"cells": [{"text": "发明人", "header": True}, {"text": "李丽鸿", "colSpan": 3}]},
                {"cells": [{"text": "分类号", "header": True}, {"text": "H04M3/487", "colSpan": 3}]},
                {"cells": [{"text": "主分类号", "header": True}, {"text": "H04M3/487", "colSpan": 3}]},
                {"cells": [{"text": "代理机构", "header": True}, {"text": "北京三友知识产权代理有限公司 11127", "colSpan": 3}]},
                {"cells": [{"text": "代理人", "header": True}, {"text": "李辉", "colSpan": 3}]},
                {"cells": [{"text": "摘要", "header": True}, {"text": "本发明实施例涉及通信领域，可在来电显示界面中展示与用户 ID 相关的订单信息和/或物流信息。", "colSpan": 3}]},
                {"cells": [{"text": "摘要附图", "header": True}, {"text": "—", "colSpan": 3}]},
            ],
        ),
        make_grid_table(
            "table-classification",
            "专利分类信息",
            3,
            [
                {"cells": [{"text": "被评专利：CN201410234381.X 一种呼叫请求处理的方法和装置", "header": True, "colSpan": 3}]},
                {"cells": [{"text": "类别", "header": True}, {"text": "分类号", "header": True}, {"text": "类名", "header": True}]},
                {"cells": [{"text": "IPC分类", "header": True, "rowSpan": 3}, {"text": "H04N19/42"}, {"text": ""}]},
                {"cells": [{"text": "H04N19/20"}, {"text": ""}]},
                {"cells": [{"text": "H04N19/172"}, {"text": ""}]},
                {"cells": [{"text": "战略性新兴产业分类", "header": True}, {"text": "1.1"}, {"text": "下一代信息网络产业"}]},
            ],
        ),
    ])

    # protocol-shaped demo entries for logo/background/icon buckets
    data["assets"]["logos"] = [
        {
            "id": "logo-primary",
            "anchor": "logo-primary",
            "label": "Primary logo",
            "meta": {},
            "alt": "OxValue.AI 主 Logo",
            "mimeType": "image/png",
            "width": 320,
            "height": 96,
            "imageSource": {"kind": "url", "url": "assets/images/logo-primary.png"},
        }
    ]
    data["assets"]["backgrounds"] = [
        {
            "id": "bg-cover",
            "anchor": "bg-cover",
            "label": "Cover background",
            "meta": {},
            "alt": "封面背景图",
            "mimeType": "image/png",
            "width": 1600,
            "height": 900,
            "imageSource": {"kind": "url", "url": "assets/images/cover-bg.png"},
        }
    ]
    data["assets"]["icons"] = [
        {
            "id": "icon-accent",
            "anchor": "icon-accent",
            "label": "Accent icon",
            "meta": {},
            "alt": "强调图标占位图",
            "mimeType": "image/png",
            "width": 32,
            "height": 32,
            "imageSource": {"kind": "embedded", "encoding": "base64", "data": TINY_PNG_B64},
        }
    ]
    data["assets"]["attachments"] = []

    # bibliography displayText fallback
    for entry in data["bibliography"]:
        if "displayText" not in entry:
            entry["displayText"] = entry.get("label") or entry.get("title") or entry["id"]

    # raw protocol-compliant blocks for full capability coverage
    demo_sec = find_section(data["sections"], "sec-capability-demo")
    if demo_sec:
        demo_sec["body"].append(
            {
                "itemType": "content",
                "blocks": [
                    {
                        "_type": "block",
                        "style": "normal",
                        "children": [
                            {"_type": "span", "text": "本段展示文本修饰 marks：", "marks": []},
                            {"_type": "span", "text": "加粗", "marks": ["strong"]},
                            {"_type": "span", "text": "、", "marks": []},
                            {"_type": "span", "text": "斜体", "marks": ["em"]},
                            {"_type": "span", "text": "、", "marks": []},
                            {"_type": "span", "text": "下划线", "marks": ["underline"]},
                            {"_type": "span", "text": "、", "marks": []},
                            {"_type": "span", "text": "inline_code()", "marks": ["code"]},
                            {"_type": "span", "text": "。", "marks": []},
                        ],
                        "markDefs": [],
                    },
                    {
                        "_type": "block",
                        "style": "normal",
                        "children": [
                            {"_type": "span", "text": "本段展示 link、xref、citation、footnote、glossary 与 inline_math：官网", "marks": ["m_link"]},
                            {"_type": "span", "text": "；参见方法章节", "marks": ["m_xref_sec"]},
                            {"_type": "span", "text": "；图", "marks": ["m_xref_fig"]},
                            {"_type": "span", "text": "、表", "marks": ["m_xref_tbl"]},
                            {"_type": "span", "text": "、公式", "marks": ["m_xref_eq"]},
                            {"_type": "span", "text": "；文献", "marks": ["m_cite"]},
                            {"_type": "span", "text": "；脚注", "marks": ["m_fn"]},
                            {"_type": "span", "text": "；术语", "marks": ["m_term"]},
                            {"_type": "span", "text": "；行内公式 ", "marks": []},
                            {"_type": "span", "text": "V = f(X; θ)", "marks": ["m_inline_math"]},
                            {"_type": "span", "text": "。", "marks": []},
                        ],
                        "markDefs": [
                            {"_key": "m_link", "_type": "link", "href": "https://www.oxvalue.ai/"},
                            {"_key": "m_xref_sec", "_type": "xref", "targetId": "sec-method", "targetType": "section"},
                            {"_key": "m_xref_fig", "_type": "xref", "targetId": "fig-system-overview", "targetType": "figure"},
                            {"_key": "m_xref_tbl", "_type": "xref", "targetId": "tbl-legal-status", "targetType": "table"},
                            {"_key": "m_xref_eq", "_type": "xref", "targetId": "eq-core-model", "targetType": "equation"},
                            {"_key": "m_cite", "_type": "citation_ref", "targetId": "cite-fu-2026"},
                            {"_key": "m_fn", "_type": "footnote_ref", "targetId": "fn-report-scope"},
                            {"_key": "m_term", "_type": "glossary_term", "targetId": "term-dcf"},
                            {"_key": "m_inline_math", "_type": "inline_math", "latex": "V = f(X; \\\\theta)"},
                        ],
                    },
                    {
                        "_type": "block",
                        "style": "normal",
                        "children": [
                            {"_type": "span", "text": "同一段内的强制换行第一行。", "marks": []},
                            {"_type": "hard_break"},
                            {"_type": "span", "text": "这是通过 hard_break 产生的第二行。", "marks": []},
                        ],
                        "markDefs": [],
                    },
                    {
                        "_type": "block",
                        "style": "blockquote",
                        "children": [
                            {"_type": "span", "text": "高质量协议样例的核心价值，在于帮助渲染器开发者直接看到每一种节点该如何落地。", "marks": []}
                        ],
                        "markDefs": [],
                    },
                    {
                        "_type": "block",
                        "style": "quote_source",
                        "children": [
                            {"_type": "span", "text": "—— OVAPortableText 示例说明", "marks": []}
                        ],
                        "markDefs": [],
                    },
                    {
                        "_type": "block",
                        "style": "caption",
                        "children": [
                            {"_type": "span", "text": "这是一条通用 caption 示例，用于展示非 figure/table/equation 的说明文本样式。", "marks": []}
                        ],
                        "markDefs": [],
                    },
                    {
                        "_type": "block",
                        "style": "smallprint",
                        "children": [
                            {"_type": "span", "text": "注：本能力展示区包含与业务正文无关的补充内容，仅用于覆盖协议中的各类节点与枚举值。", "marks": []}
                        ],
                        "markDefs": [],
                    },
                    {
                        "_type": "block",
                        "style": "normal",
                        "listItem": "bullet",
                        "level": 1,
                        "children": [{"_type": "span", "text": "一级 bullet 列表项", "marks": []}],
                        "markDefs": [],
                    },
                    {
                        "_type": "block",
                        "style": "normal",
                        "listItem": "bullet",
                        "level": 2,
                        "children": [{"_type": "span", "text": "二级 bullet 列表项", "marks": []}],
                        "markDefs": [],
                    },
                    {
                        "_type": "block",
                        "style": "normal",
                        "listItem": "number",
                        "level": 1,
                        "children": [{"_type": "span", "text": "number 列表项示例", "marks": []}],
                        "markDefs": [],
                    },
                    {
                        "_type": "callout",
                        "id": "callout-capability-extra",
                        "anchor": "callout-capability-extra",
                        "blocks": [
                            {
                                "_type": "block",
                                "style": "normal",
                                "children": [{"_type": "span", "text": "这是一个额外的 callout，用于展示块级对象可嵌入受限文本子集。", "marks": []}],
                                "markDefs": [],
                            }
                        ],
                    },
                ],
            }
        )

    return data


def main():
    doc, bib_entries = build_document()
    data = normalize_to_protocol_json(doc, bib_entries)

    out_dir = Path(__file__).resolve().parent
    out_path = out_dir / "sample1_protocol_demo.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Written: {out_path}")


if __name__ == "__main__":
    main()
