"""
スキルシート生成サービス

- Excel (.xlsx) : openpyxl を使用して社員1名につき1シート生成
- PDF          : reportlab を使用して社員1名につき1ページ生成
- combined     : 複数社員を1ファイルにまとめる
- zip          : 社員ごとの個別ファイルを ZIP にまとめる
"""
import io
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.employee import Employee
from app.models.skill import EmployeeSkill
from app.models.certification import EmployeeCertification
from app.models.project import EmployeeProject

# エクスポートファイルの保存先ディレクトリ
EXPORTS_DIR = Path("exports")


# ── Excel 生成 ────────────────────────────────────────────────────────────────

def _write_excel_sheet(ws, emp: Employee) -> None:
    """社員1名分のデータをワークシートに書き込む。"""
    from openpyxl.styles import Font, PatternFill, Alignment

    # ── ヘッダー ─────────────────────────────────────────────
    ws["A1"] = "スキルシート"
    ws["A1"].font = Font(bold=True, size=14)
    ws.merge_cells("A1:E1")

    # ── 基本情報 ─────────────────────────────────────────────
    row = 3
    info_pairs = [
        ("氏名", emp.name_ja, "社員番号", emp.employee_number),
        ("部署", emp.department.name_ja if emp.department else "—", "入社日", str(emp.joined_at)),
        ("日本語レベル", emp.japanese_level or "—", "拠点", emp.office_location),
        ("メール", emp.email, "", ""),
    ]
    for label1, val1, label2, val2 in info_pairs:
        ws.cell(row=row, column=1, value=label1).font = Font(bold=True)
        ws.cell(row=row, column=2, value=val1)
        if label2:
            ws.cell(row=row, column=4, value=label2).font = Font(bold=True)
            ws.cell(row=row, column=5, value=val2)
        row += 1

    row += 1  # 空白行

    # ── スキル ────────────────────────────────────────────────
    approved_skills = [s for s in emp.skills if s.status == "APPROVED"]
    ws.cell(row=row, column=1, value="【スキル】").font = Font(bold=True, color="1F6DAF")
    row += 1
    if approved_skills:
        headers = ["スキル名", "承認レベル", "経験年数（年）", "最終使用日"]
        for col, h in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col, value=h)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(fill_type="solid", fgColor="D9E1F2")
        row += 1
        for s in approved_skills:
            ws.cell(row=row, column=1, value=s.skill.name if s.skill else "—")
            ws.cell(row=row, column=2, value=s.approved_level)
            ws.cell(row=row, column=3, value=float(s.experience_years) if s.experience_years else None)
            ws.cell(row=row, column=4, value=str(s.last_used_at) if s.last_used_at else "—")
            row += 1
    else:
        ws.cell(row=row, column=1, value="（スキルなし）")
        row += 1

    row += 1  # 空白行

    # ── 資格 ──────────────────────────────────────────────────
    approved_certs = [c for c in emp.certifications if c.status == "APPROVED"]
    ws.cell(row=row, column=1, value="【資格】").font = Font(bold=True, color="1F6DAF")
    row += 1
    if approved_certs:
        headers = ["資格名", "カテゴリ", "取得日", "有効期限"]
        for col, h in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col, value=h)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(fill_type="solid", fgColor="D9E1F2")
        row += 1
        for c in approved_certs:
            name = c.custom_name or (c.certification_master.name if c.certification_master else "—")
            cat = c.certification_master.category if c.certification_master else "—"
            ws.cell(row=row, column=1, value=name)
            ws.cell(row=row, column=2, value=cat)
            ws.cell(row=row, column=3, value=str(c.obtained_at))
            ws.cell(row=row, column=4, value=str(c.expires_at) if c.expires_at else "—")
            row += 1
    else:
        ws.cell(row=row, column=1, value="（資格なし）")
        row += 1

    row += 1  # 空白行

    # ── プロジェクト経歴 ──────────────────────────────────────
    ws.cell(row=row, column=1, value="【プロジェクト経歴】").font = Font(bold=True, color="1F6DAF")
    row += 1
    sorted_projects = sorted(emp.projects, key=lambda p: p.started_at, reverse=True)
    if sorted_projects:
        headers = ["プロジェクト名", "期間", "役割", "技術スタック", "チーム規模"]
        for col, h in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col, value=h)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(fill_type="solid", fgColor="D9E1F2")
        row += 1
        for ep in sorted_projects:
            pname = ep.project.name if ep.project else "—"
            period = f"{ep.started_at}〜{ep.ended_at or '現在'}"
            tech = ", ".join(ep.tech_stack) if ep.tech_stack else "—"
            ws.cell(row=row, column=1, value=pname)
            ws.cell(row=row, column=2, value=period)
            ws.cell(row=row, column=3, value=ep.role)
            ws.cell(row=row, column=4, value=tech)
            ws.cell(row=row, column=5, value=ep.team_size)
            row += 1
    else:
        ws.cell(row=row, column=1, value="（プロジェクト経歴なし）")

    # カラム幅自動調整（簡易）
    from openpyxl.utils import get_column_letter
    col_widths = [30, 15, 12, 30, 10]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def generate_xlsx(employees: list[Employee]) -> bytes:
    """社員リストから Excel ワークブック（複数シート）を生成してバイト列を返す。"""
    from openpyxl import Workbook

    wb = Workbook()
    wb.remove(wb.active)  # デフォルトシートを削除

    for emp in employees:
        sheet_name = (emp.name_ja or emp.employee_number)[:31]
        ws = wb.create_sheet(title=sheet_name)
        _write_excel_sheet(ws, emp)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ── PDF 生成 ──────────────────────────────────────────────────────────────────

def generate_pdf(employees: list[Employee]) -> bytes:
    """社員リストから PDF を生成してバイト列を返す。"""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont

    # 日本語 CJK フォント登録
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title", fontName="HeiseiKakuGo-W5", fontSize=16, spaceAfter=8
    )
    heading_style = ParagraphStyle(
        "Heading", fontName="HeiseiKakuGo-W5", fontSize=11, spaceAfter=4,
        textColor=colors.HexColor("#1F6DAF"),
    )
    normal_style = ParagraphStyle(
        "Normal", fontName="HeiseiKakuGo-W5", fontSize=9
    )

    table_header_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9E1F2")),
        ("FONTNAME", (0, 0), (-1, -1), "HeiseiKakuGo-W5"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ])

    story: list = []

    for i, emp in enumerate(employees):
        if i > 0:
            story.append(PageBreak())

        story.append(Paragraph("スキルシート", title_style))

        # 基本情報
        info_data = [
            ["氏名", emp.name_ja or "—", "社員番号", emp.employee_number],
            ["部署", emp.department.name_ja if emp.department else "—", "入社日", str(emp.joined_at)],
            ["日本語", emp.japanese_level or "—", "拠点", emp.office_location],
        ]
        info_table = Table(info_data, colWidths=[25 * mm, 55 * mm, 25 * mm, 55 * mm])
        info_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "HeiseiKakuGo-W5"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (0, -1), "HeiseiKakuGo-W5"),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 6 * mm))

        # スキル
        story.append(Paragraph("【スキル】", heading_style))
        approved_skills = [s for s in emp.skills if s.status == "APPROVED"]
        if approved_skills:
            skill_data = [["スキル名", "承認Lv", "経験年数"]]
            for s in approved_skills:
                skill_data.append([
                    s.skill.name if s.skill else "—",
                    str(s.approved_level) if s.approved_level else "—",
                    f"{float(s.experience_years):.1f}年" if s.experience_years else "—",
                ])
            t = Table(skill_data, colWidths=[80 * mm, 30 * mm, 30 * mm])
            t.setStyle(table_header_style)
            story.append(t)
        else:
            story.append(Paragraph("（スキルなし）", normal_style))
        story.append(Spacer(1, 4 * mm))

        # 資格
        story.append(Paragraph("【資格】", heading_style))
        approved_certs = [c for c in emp.certifications if c.status == "APPROVED"]
        if approved_certs:
            cert_data = [["資格名", "取得日", "有効期限"]]
            for c in approved_certs:
                name = c.custom_name or (c.certification_master.name if c.certification_master else "—")
                cert_data.append([
                    name,
                    str(c.obtained_at),
                    str(c.expires_at) if c.expires_at else "—",
                ])
            t = Table(cert_data, colWidths=[90 * mm, 30 * mm, 30 * mm])
            t.setStyle(table_header_style)
            story.append(t)
        else:
            story.append(Paragraph("（資格なし）", normal_style))
        story.append(Spacer(1, 4 * mm))

        # プロジェクト経歴
        story.append(Paragraph("【プロジェクト経歴】", heading_style))
        sorted_projects = sorted(emp.projects, key=lambda p: p.started_at, reverse=True)
        if sorted_projects:
            proj_data = [["プロジェクト名", "期間", "役割", "技術スタック"]]
            for ep in sorted_projects:
                pname = ep.project.name if ep.project else "—"
                period = f"{ep.started_at}〜{ep.ended_at or '現在'}"
                tech = ", ".join(ep.tech_stack) if ep.tech_stack else "—"
                proj_data.append([pname, period, ep.role, tech])
            t = Table(proj_data, colWidths=[50 * mm, 35 * mm, 20 * mm, 55 * mm])
            t.setStyle(table_header_style)
            story.append(t)
        else:
            story.append(Paragraph("（プロジェクト経歴なし）", normal_style))

    doc.build(story)
    return buf.getvalue()


# ── メインエクスポート処理 ─────────────────────────────────────────────────────

async def export_skillsheet(
    db: AsyncSession,
    employee_ids: list[str],
    format: str,
    output_style: str,
    filename_prefix: str,
    include_salary: bool,
) -> dict:
    """
    スキルシートを生成してファイルを保存し、ダウンロード情報を返す。

    Returns:
        dict: download_url, expires_at, filename
    """
    # エクスポートディレクトリを確保
    EXPORTS_DIR.mkdir(exist_ok=True)

    # ── 社員データを一括取得 ──────────────────────────────────
    stmt = (
        select(Employee)
        .where(Employee.id.in_(employee_ids))
        .options(
            selectinload(Employee.skills).selectinload(EmployeeSkill.skill),
            selectinload(Employee.certifications).selectinload(EmployeeCertification.certification_master),
            selectinload(Employee.projects).selectinload(EmployeeProject.project),
            selectinload(Employee.department),
        )
    )
    result = await db.execute(stmt)
    employees = result.scalars().all()

    # 見つからない ID があれば 404
    found_ids = {emp.id for emp in employees}
    missing = set(employee_ids) - found_ids
    if missing:
        raise HTTPException(status_code=404, detail=f"Employees not found: {missing}")

    # ── ファイル生成 ──────────────────────────────────────────
    ext = "zip" if output_style == "zip" else ("pdf" if format == "pdf" else "xlsx")
    token = str(uuid.uuid4())
    filename = f"{filename_prefix}_{token[:8]}.{ext}"
    filepath = EXPORTS_DIR / f"{token}.{ext}"

    if output_style == "zip":
        # 社員ごとに個別ファイルを ZIP に格納
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for emp in employees:
                safe_name = (emp.name_ja or emp.employee_number).replace("/", "_")
                if format == "pdf":
                    content = generate_pdf([emp])
                    inner_name = f"{safe_name}.pdf"
                else:
                    content = generate_xlsx([emp])
                    inner_name = f"{safe_name}.xlsx"
                zf.writestr(inner_name, content)
        filepath.write_bytes(zip_buf.getvalue())
    elif format == "pdf":
        filepath.write_bytes(generate_pdf(list(employees)))
    else:
        filepath.write_bytes(generate_xlsx(list(employees)))

    expires_at = datetime.now(timezone.utc).replace(microsecond=0)
    expires_at = expires_at.replace(hour=(expires_at.hour + 1) % 24)

    return {
        "download_url": f"/api/v1/skillsheet/download/{token}",
        "expires_at": expires_at.isoformat(),
        "filename": filename,
    }
