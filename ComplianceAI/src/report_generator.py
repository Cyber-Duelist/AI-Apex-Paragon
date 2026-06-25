"""
ComplianceAI - PDF Compliance Report Generator
Generates professional compliance reports using fpdf2.
"""

import os
import io
from datetime import datetime
from fpdf import FPDF


class ComplianceReport(FPDF):
    """Custom FPDF subclass for generating branded ComplianceAI reports."""

    # ── Brand colours ─────────────────────────────────────────────────────
    BRAND_BLUE = (30, 58, 138)       # Dark blue
    BRAND_BLUE_LIGHT = (59, 130, 246) # Accent blue
    WHITE = (255, 255, 255)
    DARK = (31, 41, 55)
    GRAY = (107, 114, 128)

    RISK_COLOURS = {
        "high": (220, 38, 38),      # Red
        "critical": (220, 38, 38),
        "medium": (245, 158, 11),   # Orange
        "low": (34, 197, 94),       # Green
    }

    # ── Header / Footer ──────────────────────────────────────────────────

    def header(self):
        """Render a blue header bar with the ComplianceAI title."""
        # Blue bar across the top
        self.set_fill_color(*self.BRAND_BLUE)
        self.rect(0, 0, self.w, 18, "F")

        # Title text
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*self.WHITE)
        self.set_xy(10, 4)
        self.cell(0, 10, "ComplianceAI Report", align="L")

        # Date on the right
        self.set_font("Helvetica", "", 9)
        self.set_xy(-60, 5)
        self.cell(50, 8, datetime.now().strftime("%B %d, %Y"), align="R")

        # Reset position below header
        self.set_y(22)
        self.set_text_color(*self.DARK)

    def footer(self):
        """Render page number at the bottom of each page."""
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*self.GRAY)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    # ── Internal helpers ─────────────────────────────────────────────────

    def _section_title(self, title: str):
        """Render a styled section heading."""
        self.ln(6)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*self.BRAND_BLUE)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        # Underline
        self.set_draw_color(*self.BRAND_BLUE_LIGHT)
        self.set_line_width(0.6)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)
        self.set_text_color(*self.DARK)

    def _key_value(self, key: str, value: str):
        """Print a bold key followed by its value on the same line."""
        self.set_font("Helvetica", "B", 11)
        self.cell(50, 8, f"{key}:", new_x="END")
        self.set_font("Helvetica", "", 11)
        self.cell(0, 8, str(value), new_x="LMARGIN", new_y="NEXT")

    # ── Main generation method ───────────────────────────────────────────

    def generate_report(
        self,
        document_name: str,
        framework: str,
        risk_score: float,
        risk_level: str,
        findings_list: list,
        recommendations: str,
        output_path: str,
    ) -> str:
        """Build the full compliance report and save it to *output_path*.

        Parameters
        ----------
        document_name : str
            Name of the analysed document.
        framework : str
            Compliance framework (e.g. "GDPR", "SOC 2", "HIPAA").
        risk_score : float
            Numeric risk score (0-100).
        risk_level : str
            "low", "medium", "high", or "critical".
        findings_list : list[str]
            List of finding descriptions.
        recommendations : str
            Free-text recommendations paragraph.
        output_path : str
            Filesystem path where the PDF will be saved.

        Returns
        -------
        str
            The *output_path* the report was written to.
        """
        self.alias_nb_pages()
        self.set_auto_page_break(auto=True, margin=20)

        # ── Title page ────────────────────────────────────────────────────
        self.add_page()
        self.ln(20)

        # Big centred title
        self.set_font("Helvetica", "B", 26)
        self.set_text_color(*self.BRAND_BLUE)
        self.cell(0, 14, "Compliance Analysis Report", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(6)

        # Accent line
        mid = self.w / 2
        self.set_draw_color(*self.BRAND_BLUE_LIGHT)
        self.set_line_width(1)
        self.line(mid - 40, self.get_y(), mid + 40, self.get_y())
        self.ln(12)

        # Meta info
        self.set_text_color(*self.DARK)
        self._key_value("Document", document_name)
        self._key_value("Framework", framework)
        self._key_value("Date", datetime.now().strftime("%B %d, %Y  %H:%M"))
        self._key_value("Risk Score", f"{risk_score:.1f} / 100")

        # Risk level badge
        self.ln(4)
        level_lower = risk_level.lower()
        colour = self.RISK_COLOURS.get(level_lower, self.GRAY)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*self.WHITE)
        self.set_fill_color(*colour)
        badge_text = f"  Risk Level: {risk_level.upper()}  "
        badge_width = self.get_string_width(badge_text) + 12
        self.cell(badge_width, 12, badge_text, new_x="LMARGIN", new_y="NEXT", fill=True)
        self.set_text_color(*self.DARK)
        self.ln(8)

        # ── Findings section ─────────────────────────────────────────────
        self._section_title("Findings")
        if findings_list:
            self.set_font("Helvetica", "", 11)
            for idx, finding in enumerate(findings_list, 1):
                # Numbered bullet
                self.set_font("Helvetica", "B", 11)
                bullet = f"{idx}. "
                self.cell(10, 7, bullet, new_x="END")
                self.set_font("Helvetica", "", 11)
                # Multi-cell for wrapping
                self.multi_cell(0, 7, str(finding), new_x="LMARGIN", new_y="NEXT")
                self.ln(2)
        else:
            self.set_font("Helvetica", "I", 11)
            self.set_text_color(*self.GRAY)
            self.cell(0, 8, "No findings recorded.", new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(*self.DARK)

        # ── Recommendations section ──────────────────────────────────────
        self._section_title("Recommendations")
        self.set_font("Helvetica", "", 11)
        if recommendations:
            self.multi_cell(0, 7, str(recommendations))
        else:
            self.set_font("Helvetica", "I", 11)
            self.set_text_color(*self.GRAY)
            self.cell(0, 8, "No recommendations provided.", new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(*self.DARK)

        # ── Disclaimer ───────────────────────────────────────────────────
        self.ln(12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*self.GRAY)
        self.multi_cell(
            0,
            5,
            "Disclaimer: This report was generated by ComplianceAI and is intended for informational "
            "purposes only. It does not constitute legal advice. Please consult a qualified compliance "
            "professional for authoritative guidance.",
        )

        # ── Save ─────────────────────────────────────────────────────────
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        self.output(output_path)
        return output_path


# ---------------------------------------------------------------------------
# Helper for Streamlit download button
# ---------------------------------------------------------------------------

def generate_compliance_report(
    doc_name: str,
    framework: str,
    risk_score: float,
    risk_level: str,
    findings: list,
    recommendations: str,
    output_dir: str,
) -> bytes:
    """Generate a compliance PDF and return its raw bytes.

    This is a convenience wrapper designed for use with Streamlit's
    ``st.download_button`` which expects ``bytes`` data.

    Parameters
    ----------
    doc_name : str
        Name of the document analysed.
    framework : str
        Compliance framework identifier.
    risk_score : float
        Numeric risk score.
    risk_level : str
        Risk level string.
    findings : list[str]
        List of finding descriptions.
    recommendations : str
        Recommendations text.
    output_dir : str
        Directory where the temporary PDF will be written.

    Returns
    -------
    bytes
        The raw PDF file content.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in doc_name)
    output_path = os.path.join(output_dir, f"compliance_report_{safe_name}_{timestamp}.pdf")

    report = ComplianceReport()
    report.generate_report(
        document_name=doc_name,
        framework=framework,
        risk_score=risk_score,
        risk_level=risk_level,
        findings_list=findings,
        recommendations=recommendations,
        output_path=output_path,
    )

    with open(output_path, "rb") as f:
        pdf_bytes = f.read()

    return pdf_bytes
