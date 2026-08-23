"""
Compliance report generator module for JSON and PDF audit reports.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
import uuid

# ReportLab imports for PDF generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class JSONReportGenerator:
    """Generates structured JSON compliance reports from repository data."""

    DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "generated"

    def build_report(
        self,
        report_data: dict[str, Any],
        environment: str = "production",
    ) -> dict[str, Any]:
        """Compile a deterministic JSON report structure."""

        report_id = str(uuid.uuid4())
        generated_at = datetime.now(timezone.utc).isoformat()

        summary = report_data.get("summary", {})
        resources = report_data.get("resources", [])
        violations = report_data.get("violations", [])

        return {
            "metadata": {
                "report_id": report_id,
                "schema_version": "1.0.0",
                "generated_at": generated_at,
                "environment": environment,
            },
            "summary": {
                "total_resources": summary.get("total_resources", 0),
                "compliant_resources": summary.get("compliant_resources", 0),
                "non_compliant_resources": summary.get("non_compliant_resources", 0),
                "total_violations": summary.get("total_violations", 0),
                "compliance_percentage": summary.get("compliance_percentage", 100.0),
                "violations_by_severity": summary.get("violations_by_severity", {
                    "CRITICAL": 0,
                    "HIGH": 0,
                    "MEDIUM": 0,
                    "LOW": 0,
                }),
            },
            "resources": resources,
            "violations": violations,
        }

    def export_json(
        self,
        report_dict: dict[str, Any],
        output_path: Path | str | None = None,
    ) -> Path:
        """Write the report structure to disk as formatted JSON."""

        if output_path is None:
            output_dir = self.DEFAULT_OUTPUT_DIR
            output_dir.mkdir(parents=True, exist_ok=True)
            target = output_dir / "compliance_report.json"
        else:
            target = Path(output_path)
            target.parent.mkdir(parents=True, exist_ok=True)

        target.write_text(json.dumps(report_dict, indent=2), encoding="utf-8")
        return target


class PDFReportGenerator:
    """Generates professional compliance PDF audit reports from structured JSON data."""

    DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "generated"

    def export_pdf(
        self,
        report_dict: dict[str, Any],
        output_path: Path | str | None = None,
    ) -> Path:
        """Compile a PDF report and write it to disk."""

        if output_path is None:
            output_dir = self.DEFAULT_OUTPUT_DIR
            output_dir.mkdir(parents=True, exist_ok=True)
            target = output_dir / "compliance_report.pdf"
        else:
            target = Path(output_path)
            target.parent.mkdir(parents=True, exist_ok=True)

        # Document margin setup: 0.5 inch (36 pt)
        doc = SimpleDocTemplate(
            str(target),
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Styles customization
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#0f172a'),
            spaceAfter=4
        )
        
        subtitle_style = ParagraphStyle(
            'DocSubTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=12,
            textColor=colors.HexColor('#64748b'),
            spaceAfter=15
        )
        
        section_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=15,
            textColor=colors.HexColor('#1e293b'),
            spaceBefore=12,
            spaceAfter=6,
            keepWithNext=True
        )

        cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#334155')
        )
        
        cell_bold = ParagraphStyle(
            'TableCellBold',
            parent=cell_style,
            fontName='Helvetica-Bold'
        )

        cell_center = ParagraphStyle(
            'TableCellCenter',
            parent=cell_style,
            alignment=TA_CENTER
        )

        header_cell_center = ParagraphStyle(
            'HeaderCellCenter',
            parent=cell_center,
            textColor=colors.white
        )

        header_cell_left = ParagraphStyle(
            'HeaderCellLeft',
            parent=cell_style,
            textColor=colors.white
        )

        story = []

        # Title Block
        story.append(Paragraph("CloudCompliance Sentinel", title_style))
        story.append(Paragraph("Compliance Drift Auditing Report", subtitle_style))
        story.append(Spacer(1, 10))

        # Metadata Section Table
        meta_id = report_dict["metadata"]["report_id"]
        meta_time = report_dict["metadata"]["generated_at"]
        meta_env = report_dict["metadata"]["environment"]
        resources = report_dict.get("resources", [])
        is_demo = any(r.get("resource_id", "").startswith("demo-") for r in resources)
        if is_demo or meta_env.lower() in ["demo", "simulated"]:
            meta_env = "DEMO / SIMULATED"
        
        meta_data = [
            [Paragraph("<b>Audit ID:</b>", cell_style), Paragraph(meta_id, cell_style)],
            [Paragraph("<b>Timestamp (UTC):</b>", cell_style), Paragraph(meta_time, cell_style)],
            [Paragraph("<b>Environment Scope:</b>", cell_style), Paragraph(meta_env.upper(), cell_style)],
        ]
        meta_table = Table(meta_data, colWidths=[120, 420])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 4),
            ('LINEBELOW', (0,-1), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 15))

        # Executive summary metrics
        summary = report_dict.get("summary", {})
        total_res = summary.get("total_resources", 0)
        compliant_res = summary.get("compliant_resources", 0)
        non_compliant_res = summary.get("non_compliant_resources", 0)
        compliance_pct = summary.get("compliance_percentage", 100.0)
        
        status_text = "NON_COMPLIANT" if non_compliant_res > 0 else "COMPLIANT"
        status_color = "#ef4444" if non_compliant_res > 0 else "#10b981"
        
        summary_headers = [
            Paragraph("<b>Overall Status</b>", header_cell_center),
            Paragraph("<b>Compliance Rate</b>", header_cell_center),
            Paragraph("<b>Total Scanned</b>", header_cell_center),
            Paragraph("<b>Compliant</b>", header_cell_center),
            Paragraph("<b>Non-Compliant</b>", header_cell_center)
        ]
        
        summary_values = [
            Paragraph(f"<font color='{status_color}'><b>{status_text}</b></font>", cell_center),
            Paragraph(f"<b>{compliance_pct}%</b>", cell_center),
            Paragraph(str(total_res), cell_center),
            Paragraph(str(compliant_res), cell_center),
            Paragraph(str(non_compliant_res), cell_center)
        ]
        
        summary_table = Table([summary_headers, summary_values], colWidths=[108]*5)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#f8fafc')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 8),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ]))
        
        # Summary table styling complete
            
        story.append(Paragraph("Executive Compliance Summary", section_style))
        story.append(summary_table)
        story.append(Spacer(1, 15))

        # Severity breakdown statistics
        severity_counts = summary.get("violations_by_severity", {})
        severity_headers = [
            Paragraph("<b>Severity</b>", cell_style),
            Paragraph("<b>Count</b>", cell_center),
            Paragraph("<b>Description</b>", cell_style)
        ]
        severity_rows = [
            severity_headers,
            [Paragraph("<font color='#ef4444'><b>CRITICAL</b></font>", cell_style), Paragraph(str(severity_counts.get("CRITICAL", 0)), cell_center), Paragraph("Immediate security risk requiring urgent action.", cell_style)],
            [Paragraph("<font color='#ef4444'><b>HIGH</b></font>", cell_style), Paragraph(str(severity_counts.get("HIGH", 0)), cell_center), Paragraph("Encryption disabled or public access detected.", cell_style)],
            [Paragraph("<font color='#f59e0b'><b>MEDIUM</b></font>", cell_style), Paragraph(str(severity_counts.get("MEDIUM", 0)), cell_center), Paragraph("Audit/logging configuration is disabled or missing.", cell_style)],
            [Paragraph("<font color='#38bdf8'><b>LOW</b></font>", cell_style), Paragraph(str(severity_counts.get("LOW", 0)), cell_center), Paragraph("Minor compliance configuration drift.", cell_style)]
        ]
        severity_table = Table(severity_rows, colWidths=[120, 80, 340])
        severity_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 6),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ]))
        story.append(Paragraph("Severity Classifications", section_style))
        story.append(severity_table)
        story.append(Spacer(1, 20))

        # Violations Table Log
        violations = report_dict.get("violations", [])
        story.append(Paragraph("Compliance Violations Log", section_style))
        
        if len(violations) == 0:
            story.append(Paragraph("<b>No compliance violations discovered. All assets comply with standard policies.</b>", cell_style))
        else:
            col_widths = [45, 60, 95, 90, 50, 200]
            violation_headers = [
                Paragraph("<b>Provider</b>", header_cell_left),
                Paragraph("<b>Type</b>", header_cell_left),
                Paragraph("<b>Resource Name</b>", header_cell_left),
                Paragraph("<b>Rule</b>", header_cell_left),
                Paragraph("<b>Severity</b>", header_cell_left),
                Paragraph("<b>Message</b>", header_cell_left)
            ]
            
            table_rows = [violation_headers]
            for v in violations:
                provider = v.get("provider", "AWS")
                res_type = v.get("resource_type", "storage")
                res_name = v.get("resource_name") or v.get("resource_id", "unknown")
                rule_id = v.get("rule_id", "").replace("_", " ")
                severity = v.get("severity", "HIGH").upper()
                msg = v.get("message", "")
                
                sev_color = "#ef4444"
                if severity == "MEDIUM":
                    sev_color = "#f59e0b"
                elif severity == "LOW":
                    sev_color = "#38bdf8"
                
                provider_tag = f"<font color='#f97316'><b>{provider}</b></font>" if provider == "AWS" else f"<font color='#3b82f6'><b>{provider}</b></font>"
                
                row = [
                    Paragraph(provider_tag, cell_style),
                    Paragraph(res_type, cell_style),
                    Paragraph(res_name, cell_style),
                    Paragraph(rule_id, cell_style),
                    Paragraph(f"<font color='{sev_color}'><b>{severity}</b></font>", cell_style),
                    Paragraph(msg, cell_style)
                ]
                table_rows.append(row)
                
            violations_table = Table(table_rows, colWidths=col_widths, repeatRows=1)
            violations_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('PADDING', (0,0), (-1,-1), 5),
                ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#0f172a')),
            ]))
            
            # Violation headers styling complete
                
            story.append(violations_table)

        doc.build(story)
        return target


# Maintain backwards compatibility
ReportGenerator = JSONReportGenerator
