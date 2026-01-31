## Context

The `pc_automation.py` module currently supports basic patterns (Value, Toggle, ExpandCollapse). To automate testing that mirrors Windows Narrator, we need to support "Common & Structural Controls" like Sliders, ProgressBars, and Tables. Narrator explicitly announces "Item X of Y", enabled state, and grid coordinates, which are currently missing.

**Constraints:**
-   Must match Narrator behavior.
-   JSON output format must remain valid.
-   `HelpText` is explicitly excluded for new apps per requirements.

## Goals / Non-Goals

**Goals:**
-   Extract `PositionInSet` and `SizeOfSet` (Item X of Y).

**Non-Goals (Deferred):**
-   Extract `IsEnabled` boolean (code commented out - needs review).
-   Extract `ItemStatus` string (code commented out - needs review).
-   Support for rare controls (SemanticZoom, IPOctet).
-   Extraction of `HelpText` for UIA-native apps.
-   Pattern-based extraction (RangeValuePattern, GridItemPattern, etc.) - deferred to future.

## Decisions

### Decision 1: Direct Property Extraction for Base Props

**Rationale:**
-   `IsEnabled` and `ItemStatus` are base UIA properties available on almost all elements.
-   `PositionInSet` and `SizeOfSet` are increasingly standard UIA properties (ids 30024 and 30025). We will attempt to fetch these directly.

**Implementation:**
-   Use `element.GetPropertyValue(PropertyId.PositionInSetProperty)` (ID: 30152) for PositionInSet
-   Use `element.GetPropertyValue(PropertyId.SizeOfSetProperty)` (ID: 30153) for SizeOfSet
-   Returns `0` (int) when property not set or unsupported
-   If value > 0, include in Position dict; otherwise return None

### Decision 2: JSON Structure

**Format:**
```json
{
  "Name": "...",
  "LocalizedControlType": "...",
  "IsEnabled": true,
  "ItemStatus": "...",
  "Position": { "Index": 1, "Total": 5 }
}
```
**Rationale:** Base properties are extracted directly from element. Fields are nullable/omitted if data is missing.

## Risks / Trade-offs

### Risk 1: Missing Position Info
**Mitigation:** `PositionInSet` is not always set by developers. If `0` or missing, we report it as `null` or skip it to avoid false data (Narrator also falls silent if data is missing).

### Risk 2: Unknown GetPropertyValue Behavior
**Mitigation:** Spike task added to test actual behavior of `GetPropertyValue(30024/30025)` before implementation. This prevents runtime errors from incorrect assumptions.

## Deferred to Future Changes

The following features are explicitly out of scope for this change:

1. **Pattern-based extraction:** RangeValuePattern, GridItemPattern, TableItemPattern, LegacyIAccessiblePattern
2. **JSON Structure:** Nested vs Flat decision - pending verification with actual pattern implementation
3. **Testing Strategy:** Manual vs automated comparison with Narrator output

## Implementation Notes

**Key additions to `pc_automation.py`:**
-   Logic in `get_focused_element_info` to extract `IsEnabled`, `ItemStatus`, `PositionInSet`, `SizeOfSet`.
-   No new pattern handlers or control mappings needed - base properties only.
