# Tables and grids

## Table of contents

- [Official table contract](#official-table-contract)
- [Rich HTML syntax](#rich-html-syntax)
- [JSON block schema](#json-block-schema)
- [Rows, colspan, and rowspan](#rows-colspan-and-rowspan)
- [Column limit](#column-limit)
- [Alignment](#alignment)
- [RTL guidance](#rtl-guidance)
- [Responsive design guidance](#responsive-design-guidance)
- [Examples](#examples)
- [Anti-patterns](#anti-patterns)

## Official table contract

Telegram Bot API 10.3 represents an outgoing structured table as `InputRichBlockTable` with:

- `type`: always `table`
- `cells`: two-dimensional array of `RichBlockTableCell`
- optional `is_bordered`
- optional `is_striped`
- optional `is_compact`
- optional `caption` (`RichText`)

There is no documented top-level `rows` field on `InputRichBlockTable`.

`RichText` may be a plain string, an array of rich-text values, or a documented `RichText*` object, so a simple table-cell value such as `{"text": "Keyboard"}` is valid at the Bot API level.

## Rich HTML syntax

```html
<table bordered striped compact>
  <caption>Inventory</caption>
  <tr>
    <th align="left">Product</th>
    <th align="right">Stock</th>
  </tr>
  <tr>
    <td align="left">Keyboard</td>
    <td align="right">14</td>
  </tr>
</table>
```

Supported presentation attributes map to the structured fields:

| Rich HTML | JSON field |
| --- | --- |
| `bordered` | `is_bordered` |
| `striped` | `is_striped` |
| `compact` | `is_compact` |

Do not use historical aliases such as `has_borders` as canonical Bot API schema.

## JSON block schema

Correct shape:

```json
{
  "type": "table",
  "cells": [
    [
      {"text": "Product", "is_header": true, "align": "left"},
      {"text": "Stock", "is_header": true, "align": "right"}
    ],
    [
      {"text": "Keyboard", "align": "left"},
      {"text": "14", "align": "right"}
    ]
  ],
  "is_bordered": true,
  "is_striped": true,
  "is_compact": true,
  "caption": "Inventory"
}
```

Frameworks may wrap `RichText` in generated types. Prefer those generated types when available, but keep the underlying Bot API field name `cells`.

## Rows, colspan, and rowspan

`RichBlockTableCell` supports `colspan` and `rowspan` when the value is greater than 1.

Do **not** invent a requirement that every source row must contain the same number of cells. Telegram's own Rich HTML examples include a table where earlier rows occupy multiple columns and a later row contains only one cell. The documented hard constraint is the table's maximum of 20 columns, not an equal-source-row-length rule.

When generating dynamic tables:

- require positive integer `colspan`/`rowspan` values;
- account for active rowspans when estimating effective column usage;
- keep the effective table width at or below 20 columns;
- test complex spans with the Telegram clients you support.

Do not branch application logic on an exact human-readable server error sentence for malformed table markup.

## Column limit

Telegram documents a maximum of **20 columns** in a rich-message table.

A mobile-friendly design should generally use fewer. This repository recommends roughly 2-6 columns for normal bot UI, but that is a project design recommendation, not a Telegram limit.

## Alignment

`RichBlockTableCell` supports:

- optional `is_header`;
- optional `colspan`;
- optional `rowspan`;
- horizontal `align`: `left`, `center`, `right`;
- vertical `valign`: `top`, `middle`, `bottom`.

Rich HTML:

```html
<tr>
  <td colspan="2" align="right"><b>Total</b></td>
  <td align="right">$77.00</td>
</tr>
```

Table cells can contain inline formatting. Do not put arbitrary block-level rich content inside a cell.

## RTL guidance

Use `is_rtl: true` on the containing `InputRichMessage` when right-to-left layout is required.

Recommended practices for Persian/Arabic tables:

- keep semantic data order stable in your application model;
- align labels and narrative text according to the language;
- isolate long Latin identifiers, tracking codes, or SKU values with inline code or separate cells when it improves readability;
- test on the Telegram clients you support.

Do not document a particular client column-mirroring behavior as a server guarantee unless Telegram explicitly specifies it.

## Responsive design guidance

Project recommendations:

- Prefer `compact` for data-dense mobile tables.
- Avoid long prose inside cells.
- Put secondary details in a `details` block below the table instead of adding many columns.
- Use short labels and format numbers before interpolation.
- Consider a list/card layout if content remains wide on small screens.

These are design practices, not API requirements.

## Examples

### Invoice

```html
<table bordered striped compact>
  <caption>Invoice</caption>
  <tr>
    <th>Description</th>
    <th align="center">Qty</th>
    <th align="right">Amount</th>
  </tr>
  <tr>
    <td>Managed hosting</td>
    <td align="center">1</td>
    <td align="right">$80.00</td>
  </tr>
  <tr>
    <td colspan="2" align="right"><b>Total</b></td>
    <td align="right"><b>$80.00</b></td>
  </tr>
</table>
```

### Span pattern similar to Telegram's official example

```html
<table bordered compact>
  <tr>
    <td colspan="2" rowspan="2">A</td>
    <td>B</td>
    <td>C</td>
  </tr>
  <tr>
    <td valign="top">D</td>
    <td valign="middle">E</td>
  </tr>
  <tr>
    <td>Final row may have fewer source cells</td>
  </tr>
</table>
```

## Anti-patterns

Do not:

- emit a JSON table with `rows` instead of `cells`;
- exceed 20 effective columns;
- impose an undocumented equal-row-width invariant;
- place block-level content inside a table cell;
- interpolate unescaped HTML from database/user values;
- guess that a malformed table will always fall back to plain text;
- depend on an exact server error sentence;
- build a 15-20 column table merely because the API permits it.

Run `scripts/validate_rich_message.py` for generated JSON block trees before dispatch where feasible.
