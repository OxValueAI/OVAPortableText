"""
Public package exports for OVAPortableText.
OVAPortableText 的公开导出入口。
"""

from .base import OvaBaseModel
from .block_objects import BlockObject, CalloutBlock, ChartBlock, ImageBlock, MathBlock, TableBlock
from .content import (
    ALLOWED_DECORATOR_MARKS,
    ALLOWED_TEXT_STYLES,
    AnnotationMarkDef,
    BlockElement,
    ContentItem,
    DecoratorMark,
    LinkMarkDef,
    ListItemStyle,
    MarkDef,
    Span,
    TextBlock,
    TextStyle,
)
from .document import Document, DocumentMeta
from .exceptions import DocumentValidationError, ValidationIssue, ValidationReport
from .helpers import (
    annotation_def,
    attachment_asset,
    background_asset,
    background_asset_embedded,
    background_asset_from_file,
    background_asset_url,
    bibliography_entry,
    blocks_from_items,
    bullet_item,
    callout,
    chart_block,
    citation_ref,
    code_span,
    create_document,
    document,
    em,
    footnote_entry,
    footnote_ref,
    grid_table_cell,
    grid_table_dataset,
    grid_table_row,
    glossary_entry,
    glossary_term,
    hard_break,
    icon_asset,
    icon_asset_embedded,
    icon_asset_from_file,
    icon_asset_url,
    inline_math,
    image_asset,
    image_asset_embedded,
    image_asset_from_file,
    image_asset_url,
    image_block,
    link_def,
    logo_asset,
    logo_asset_embedded,
    logo_asset_from_file,
    logo_asset_url,
    marked,
    math_block,
    metric_dataset,
    metric_value,
    number_item,
    paragraph,
    pie_chart_dataset,
    chart_dataset,
    pie_chart_from_parallel_arrays,
    pie_slice,
    record_table_dataset,
    section,
    span,
    strong,
    table_block,
    table_column,
    table_dataset,
    underline,
    xref,
)
from .inline import CitationRef, FootnoteRef, GlossaryTerm, HardBreak, InlineMath, InlineObject, XRef
from .numbering import DocumentNumbering, NumberingConfig, NumberedTarget
from .registry import (
    AssetsRegistry,
    AttachmentAsset,
    BackgroundAsset,
    BibliographyEntry,
    ChartDataset,
    DatasetsRegistry,
    FootnoteEntry,
    GenericChartDataset,
    GlossaryEntry,
    GridTableCell,
    GridTableDataset,
    GridTableRow,
    IconAsset,
    ImageAsset,
    ImageLikeAssetBase,
    ImageSource,
    ImageSourceEmbedded,
    ImageSourceUrl,
    LogoAsset,
    MetricDataset,
    MetricValue,
    PieChartDataset,
    PieSlice,
    RecordTableDataset,
    RegistryEntryBase,
    TableColumn,
    TableDataset,
)
from .resolver import DocumentResolver, ResolvedTarget
from .section import NumberingMode, Section
from .theme import ThemeConfig
from .validator import assert_valid_document, validate_document
from .version import __version__

__all__ = [name for name in globals() if not name.startswith("_")]
