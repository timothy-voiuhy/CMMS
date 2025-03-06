"""
Reporting module for CMMS application.
Provides comprehensive reporting capabilities using ReportLab.
"""

import os
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any, Optional, Union, Tuple

# ReportLab imports
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, 
                               TableStyle, PageBreak, Image, Flowable, 
                               KeepTogether, ListFlowable, ListItem)
from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart

# Define constants
REPORTS_DIR = os.path.join(os.path.expanduser("~"), "CMMS_Reports")
DEFAULT_PAGESIZE = A4
DEFAULT_MARGIN = 0.5 * inch
CMMS_BLUE = colors.Color(33/255, 150/255, 243/255)
CMMS_DARK = colors.Color(42/255, 42/255, 42/255)
CMMS_LIGHT = colors.Color(250/255, 250/255, 250/255)
CMMS_GREEN = colors.Color(76/255, 175/255, 80/255)
CMMS_RED = colors.Color(244/255, 67/255, 54/255)
CMMS_ORANGE = colors.Color(255/255, 152/255, 0/255)
CMMS_PURPLE = colors.Color(156/255, 39/255, 176/255)

# Ensure reports directory exists
os.makedirs(REPORTS_DIR, exist_ok=True)

# Custom flowables
class HorizontalLine(Flowable):
    """A horizontal line flowable."""
    
    def __init__(self, width, thickness=1, color=colors.black, space_before=0, space_after=0):
        Flowable.__init__(self)
        self.width = width
        self.thickness = thickness
        self.color = color
        self.space_before = space_before
        self.space_after = space_after
        
    def __repr__(self):
        return f"HorizontalLine(width={self.width})"
        
    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, self.width, 0)
        
    def wrap(self, *args):
        return (self.width, self.thickness + self.space_before + self.space_after)
        
    def getSpaceBefore(self):
        return self.space_before
        
    def getSpaceAfter(self):
        return self.space_after

class ReportHeader(Flowable):
    """A header flowable for reports."""
    
    def __init__(self, title, subtitle=None, logo_path=None, width=None, height=0.75*inch):
        Flowable.__init__(self)
        self.title = title
        self.subtitle = subtitle
        self.logo_path = logo_path
        self.width = width
        self.height = height
        
    def __repr__(self):
        return f"ReportHeader(title={self.title})"
        
    def draw(self):
        # Draw background
        self.canv.setFillColor(CMMS_DARK)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        
        # Draw title
        self.canv.setFillColor(colors.white)
        self.canv.setFont("Helvetica-Bold", 16)
        
        # Adjust position if logo exists
        logo_width = 0
        if self.logo_path and os.path.exists(self.logo_path):
            logo_width = 0.5 * inch
            self.canv.drawImage(self.logo_path, 0.1*inch, 0.1*inch, width=logo_width, height=self.height-0.2*inch)
        
        # Draw title text
        self.canv.drawString(logo_width + 0.2*inch, self.height/2 + 0.1*inch, self.title)
        
        # Draw subtitle if provided
        if self.subtitle:
            self.canv.setFont("Helvetica", 10)
            self.canv.drawString(logo_width + 0.2*inch, 0.2*inch, self.subtitle)
        
    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        return (availWidth, self.height)

# Main Report class
class Report:
    """Base class for all reports in the CMMS system."""
    
    def __init__(self, title, filename=None, pagesize=DEFAULT_PAGESIZE, 
                 margins=(DEFAULT_MARGIN, DEFAULT_MARGIN, DEFAULT_MARGIN, DEFAULT_MARGIN)):
        """
        Initialize a new report.
        
        Args:
            title: The title of the report
            filename: Optional filename, will be generated if not provided
            pagesize: Page size (default: A4)
            margins: Tuple of margins (left, right, top, bottom)
        """
        self.title = title
        self.creation_date = datetime.now()
        
        # Generate filename if not provided
        if filename is None:
            timestamp = self.creation_date.strftime('%Y%m%d_%H%M%S')
            safe_title = "".join([c if c.isalnum() else "_" for c in title])
            filename = f"{safe_title}_{timestamp}.pdf"
        
        self.filename = filename
        self.filepath = os.path.join(REPORTS_DIR, filename)
        
        # Initialize document
        self.doc = SimpleDocTemplate(
            self.filepath,
            pagesize=pagesize,
            leftMargin=margins[0],
            rightMargin=margins[1],
            topMargin=margins[2],
            bottomMargin=margins[3]
        )
        
        # Initialize styles
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        
        # Initialize story (content elements)
        self.story = []
        
        # Add metadata
        self.metadata = {
            'title': title,
            'creation_date': self.creation_date,
            'generated_by': 'CMMS Reporting Module'
        }
    
    def _setup_styles(self):
        """Set up custom styles for the report."""
        # Title style
        if 'ReportTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ReportTitle',
                parent=self.styles['Title'],
                fontSize=18,
                leading=22,
                textColor=CMMS_DARK,
                spaceAfter=12
            ))
        
        # Heading styles - modify existing styles instead of adding new ones
        self.styles['Heading1'].fontSize = 16
        self.styles['Heading1'].textColor = CMMS_BLUE
        self.styles['Heading1'].spaceAfter = 10
        
        self.styles['Heading2'].fontSize = 14
        self.styles['Heading2'].textColor = CMMS_DARK
        self.styles['Heading2'].spaceAfter = 8
        
        self.styles['Heading3'].fontSize = 12
        self.styles['Heading3'].textColor = CMMS_DARK
        self.styles['Heading3'].spaceAfter = 6
        
        # Normal text style
        if 'BodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='BodyText',
                parent=self.styles['Normal'],
                fontSize=10,
                leading=14,
                spaceAfter=6
            ))
        
        # Table header style
        if 'TableHeader' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='TableHeader',
                parent=self.styles['Normal'],
                fontSize=10,
                leading=12,
                textColor=colors.white,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ))
        
        # Footer style
        if 'Footer' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.gray,
                alignment=TA_CENTER
            ))
        
        # Info box style
        if 'InfoBox' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='InfoBox',
                parent=self.styles['Normal'],
                fontSize=10,
                leading=14,
                backColor=colors.lightgrey,
                borderPadding=5,
                borderWidth=0.5,
                borderColor=colors.grey
            ))
    
    def add_title(self, subtitle=None):
        """Add the report title to the story."""
        # Add report header
        self.story.append(ReportHeader(self.title, subtitle))
        self.story.append(Spacer(1, 0.25*inch))
        
        # Add generation date
        date_text = f"Generated on: {self.creation_date.strftime('%Y-%m-%d %H:%M')}"
        self.story.append(Paragraph(date_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.25*inch))
    
    def add_section(self, title, level=1):
        """Add a section heading to the story."""
        style_name = f"Heading{level}"
        self.story.append(Paragraph(title, self.styles[style_name]))
        self.story.append(HorizontalLine(self.doc.width, 1, CMMS_BLUE, 0, 6))
    
    def add_paragraph(self, text):
        """Add a paragraph to the story."""
        self.story.append(Paragraph(text, self.styles['BodyText']))
    
    def add_spacer(self, height=0.1*inch):
        """Add a spacer to the story."""
        self.story.append(Spacer(1, height))
    
    def add_page_break(self):
        """Add a page break to the story."""
        self.story.append(PageBreak())
    
    def add_table(self, data, colWidths=None, style=None, header_row=True):
        """
        Add a table to the story.
        
        Args:
            data: List of rows, where each row is a list of cells
            colWidths: Optional list of column widths
            style: Optional TableStyle
            header_row: Whether the first row is a header row
        """
        if not data:
            self.add_paragraph("No data available.")
            return
        
        # Create table
        table = Table(data, colWidths=colWidths)
        
        # Apply default style if none provided
        if style is None:
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), CMMS_DARK if header_row else colors.white),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white if header_row else colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ])
        
        table.setStyle(style)
        self.story.append(table)
    
    def add_info_box(self, title, content_dict):
        """
        Add an information box with key-value pairs.
        
        Args:
            title: Title of the info box
            content_dict: Dictionary of key-value pairs to display
        """
        # Add title
        self.story.append(Paragraph(title, self.styles['Heading3']))
        
        # Create data for table
        data = []
        for key, value in content_dict.items():
            data.append([key, str(value)])
        
        # Create table
        table = Table(data, colWidths=[1.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.1*inch))
    
    def add_chart(self, chart_type, data, title=None, width=6*inch, height=3*inch):
        """
        Add a chart to the story.
        
        Args:
            chart_type: Type of chart ('bar', 'pie', 'line')
            data: Data for the chart
            title: Optional title for the chart
            width: Width of the chart
            height: Height of the chart
        """
        drawing = Drawing(width, height)
        
        if chart_type == 'bar':
            chart = VerticalBarChart()
            chart.x = 50
            chart.y = 50
            chart.height = height - 100
            chart.width = width - 100
            chart.data = data
            chart.strokeColor = colors.black
            chart.valueAxis.valueMin = 0
            chart.valueAxis.valueMax = max([max(row) for row in data]) * 1.1
            chart.valueAxis.valueStep = chart.valueAxis.valueMax / 10
            chart.categoryAxis.labels.boxAnchor = 'ne'
            chart.categoryAxis.labels.dx = 8
            chart.categoryAxis.labels.dy = -2
            chart.categoryAxis.labels.angle = 30
            chart.bars[0].fillColor = CMMS_BLUE
            
        elif chart_type == 'pie':
            chart = Pie()
            chart.x = width / 2
            chart.y = height / 2
            chart.width = min(width, height) - 100
            chart.height = min(width, height) - 100
            chart.data = data
            chart.labels = [str(d) for d in data]
            chart.slices.strokeWidth = 0.5
            chart.slices[0].fillColor = CMMS_BLUE
            chart.slices[1].fillColor = CMMS_GREEN
            chart.slices[2].fillColor = CMMS_ORANGE
            chart.slices[3].fillColor = CMMS_RED
            chart.slices[4].fillColor = CMMS_PURPLE
            
        elif chart_type == 'line':
            chart = HorizontalLineChart()
            chart.x = 50
            chart.y = 50
            chart.height = height - 100
            chart.width = width - 100
            chart.data = data
            chart.joinedLines = 1
            chart.lines[0].symbol = None
            chart.lines[0].strokeColor = CMMS_BLUE
            chart.lines[0].strokeWidth = 2
            chart.valueAxis.valueMin = 0
            chart.valueAxis.valueMax = max([max(row) for row in data]) * 1.1
            chart.valueAxis.valueStep = chart.valueAxis.valueMax / 10
            chart.categoryAxis.labels.boxAnchor = 'ne'
            chart.categoryAxis.labels.dx = 8
            chart.categoryAxis.labels.dy = -2
            chart.categoryAxis.labels.angle = 30
            
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
        
        drawing.add(chart)
        
        # Add title if provided
        if title:
            self.story.append(Paragraph(title, self.styles['Heading3']))
        
        self.story.append(drawing)
        self.story.append(Spacer(1, 0.1*inch))
    
    def add_footer(self):
        """Add a footer to the story."""
        footer_text = f"Generated by CMMS Reporting Module | {self.creation_date.strftime('%Y-%m-%d %H:%M')}"
        self.story.append(Paragraph(footer_text, self.styles['Footer']))
    
    def build(self):
        """Build the report and save it to file."""
        self.doc.build(self.story)
        return self.filepath

# Specific report types
class CraftsmanReport(Report):
    """Report for craftsman information."""
    
    def __init__(self, craftsman_data, report_type="complete", filename=None):
        """
        Initialize a craftsman report.
        
        Args:
            craftsman_data: Dictionary containing craftsman data
            report_type: Type of report ('complete', 'performance', 'skills', 'training')
            filename: Optional filename
        """
        self.craftsman = craftsman_data.get('craftsman', {})
        self.skills = craftsman_data.get('skills', [])
        self.training = craftsman_data.get('training', [])
        self.work_history = craftsman_data.get('work_history', [])
        self.performance = craftsman_data.get('performance', {})
        self.teams = craftsman_data.get('teams', [])
        self.report_type = report_type
        
        # Generate title based on report type
        if report_type == "complete":
            title = f"Craftsman Report - {self.craftsman.get('first_name', '')} {self.craftsman.get('last_name', '')}"
        elif report_type == "performance":
            title = f"Performance Report - {self.craftsman.get('first_name', '')} {self.craftsman.get('last_name', '')}"
        elif report_type == "skills":
            title = f"Skills Report - {self.craftsman.get('first_name', '')} {self.craftsman.get('last_name', '')}"
        elif report_type == "training":
            title = f"Training Report - {self.craftsman.get('first_name', '')} {self.craftsman.get('last_name', '')}"
        else:
            title = f"Craftsman Report - {self.craftsman.get('first_name', '')} {self.craftsman.get('last_name', '')}"
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            employee_id = self.craftsman.get('employee_id', 'unknown')
            filename = f"craftsman_{report_type}_{employee_id}_{timestamp}.pdf"
        
        super().__init__(title, filename)
    
    def generate(self):
        """Generate the report content based on report type."""
        self.add_title()
        
        if self.report_type == "complete":
            self.generate_complete_report()
        elif self.report_type == "performance":
            self.generate_performance_report()
        elif self.report_type == "skills":
            self.generate_skills_report()
        elif self.report_type == "training":
            self.generate_training_report()
        else:
            self.generate_complete_report()
        
        self.add_footer()
        return self.build()
    
    def generate_complete_report(self):
        """Generate a complete craftsman report."""
        # Basic information section
        self.add_section("Basic Information")
        
        basic_info = {
            "Employee ID": self.craftsman.get('employee_id', 'N/A'),
            "Name": f"{self.craftsman.get('first_name', '')} {self.craftsman.get('last_name', '')}",
            "Specialization": self.craftsman.get('specialization', 'N/A'),
            "Experience Level": self.craftsman.get('experience_level', 'N/A'),
            "Phone": self.craftsman.get('phone', 'N/A'),
            "Email": self.craftsman.get('email', 'N/A'),
            "Hire Date": str(self.craftsman.get('hire_date', 'N/A')),
            "Status": self.craftsman.get('status', 'N/A')
        }
        
        self.add_info_box("Personal Details", basic_info)
        self.add_spacer()
        
        # Skills section
        self.add_section("Skills & Certifications")
        
        if self.skills:
            skills_data = [["Skill", "Level", "Certification", "Expiry Date"]]
            for skill in self.skills:
                skills_data.append([
                    skill.get('skill_name', 'N/A'),
                    skill.get('skill_level', 'N/A'),
                    skill.get('certification', 'N/A'),
                    str(skill.get('expiry_date', 'N/A'))
                ])
            self.add_table(skills_data)
        else:
            self.add_paragraph("No skills or certifications recorded.")
        
        self.add_spacer()
        
        # Training section
        self.add_section("Training Records")
        
        if self.training:
            training_data = [["Training", "Completion Date", "Provider", "Status"]]
            for record in self.training:
                training_data.append([
                    record.get('training_name', 'N/A'),
                    str(record.get('completion_date', 'N/A')),
                    record.get('training_provider', 'N/A'),
                    record.get('training_status', 'N/A')
                ])
            self.add_table(training_data)
        else:
            self.add_paragraph("No training records available.")
        
        self.add_spacer()
        
        # Performance section
        self.add_section("Performance Metrics")
        
        if self.performance:
            performance_info = {
                "Tasks Completed (Last Month)": self.performance.get('month_count', 'N/A'),
                "Average Rating (Last Month)": f"{self.performance.get('month_rating', 0):.1f}" if self.performance.get('month_rating') is not None else 'N/A',
                "On-Time Completion Rate": f"{self.performance.get('month_percentage', 0):.1f}%" if self.performance.get('month_percentage') is not None else 'N/A'
            }
            self.add_info_box("Monthly Performance", performance_info)
            
            # Add performance chart if data available
            if 'monthly_data' in self.performance:
                monthly_data = self.performance['monthly_data']
                if monthly_data:
                    chart_data = [[d.get('count', 0) for d in monthly_data]]
                    labels = [d.get('month', 'N/A') for d in monthly_data]
                    self.add_chart('bar', chart_data, "Monthly Work Orders Completed")
        else:
            self.add_paragraph("No performance metrics available.")
        
        self.add_spacer()
        
        # Teams section
        self.add_section("Team Membership")
        
        if self.teams:
            teams_data = [["Team Name", "Role", "Team Leader", "Joined Date"]]
            for team in self.teams:
                teams_data.append([
                    team.get('team_name', 'N/A'),
                    team.get('role', 'N/A'),
                    f"{team.get('leader_first_name', '')} {team.get('leader_last_name', '')}" if team.get('leader_first_name') else 'N/A',
                    str(team.get('joined_date', 'N/A'))
                ])
            self.add_table(teams_data)
        else:
            self.add_paragraph("Not a member of any teams.")
    
    def generate_performance_report(self):
        """Generate a performance-focused report."""
        # Performance overview
        self.add_section("Performance Overview")
        
        if self.performance:
            performance_info = {
                "Tasks Completed (Last Month)": self.performance.get('month_count', 'N/A'),
                "Average Rating (Last Month)": f"{self.performance.get('month_rating', 0):.1f}" if self.performance.get('month_rating') is not None else 'N/A',
                "On-Time Completion Rate": f"{self.performance.get('month_percentage', 0):.1f}%" if self.performance.get('month_percentage') is not None else 'N/A',
                "Tasks Completed (Year to Date)": self.performance.get('year_count', 'N/A'),
                "Average Rating (Year to Date)": f"{self.performance.get('year_rating', 0):.1f}" if self.performance.get('year_rating') is not None else 'N/A'
            }
            self.add_info_box("Performance Metrics", performance_info)
            
            # Add performance chart if data available
            if 'monthly_data' in self.performance:
                monthly_data = self.performance['monthly_data']
                if monthly_data:
                    chart_data = [[d.get('count', 0) for d in monthly_data]]
                    self.add_chart('bar', chart_data, "Monthly Work Orders Completed")
            
            # Add rating chart if data available
            if 'rating_data' in self.performance:
                rating_data = self.performance['rating_data']
                if rating_data:
                    chart_data = [[d.get('rating', 0) for d in rating_data]]
                    self.add_chart('line', chart_data, "Performance Rating Trend")
        else:
            self.add_paragraph("No performance metrics available.")
        
        self.add_spacer()
        
        # Recent work history
        self.add_section("Recent Work History")
        
        if self.work_history:
            # Only show the 10 most recent entries
            recent_history = self.work_history[:10]
            history_data = [["Date", "Task Type", "Equipment", "Description", "Rating"]]
            for entry in recent_history:
                history_data.append([
                    str(entry.get('task_date', 'N/A')),
                    entry.get('task_type', 'N/A'),
                    str(entry.get('equipment_id', 'N/A')),
                    entry.get('task_description', 'N/A'),
                    str(entry.get('performance_rating', 'N/A'))
                ])
            self.add_table(history_data)
        else:
            self.add_paragraph("No work history available.")
    
    def generate_skills_report(self):
        """Generate a skills-focused report."""
        # Skills overview
        self.add_section("Skills Overview")
        
        basic_info = {
            "Employee ID": self.craftsman.get('employee_id', 'N/A'),
            "Name": f"{self.craftsman.get('first_name', '')} {self.craftsman.get('last_name', '')}",
            "Specialization": self.craftsman.get('specialization', 'N/A'),
            "Experience Level": self.craftsman.get('experience_level', 'N/A')
        }
        self.add_info_box("Craftsman Details", basic_info)
        
        self.add_spacer()
        
        # Skills and certifications
        self.add_section("Skills & Certifications")
        
        if self.skills:
            skills_data = [["Skill", "Level", "Certification", "Certification Date", "Expiry Date", "Authority"]]
            for skill in self.skills:
                skills_data.append([
                    skill.get('skill_name', 'N/A'),
                    skill.get('skill_level', 'N/A'),
                    skill.get('certification', 'N/A'),
                    str(skill.get('certification_date', 'N/A')),
                    str(skill.get('expiry_date', 'N/A')),
                    skill.get('certification_authority', 'N/A')
                ])
            self.add_table(skills_data)
            
            # Add skills distribution chart
            skill_levels = {}
            for skill in self.skills:
                level = skill.get('skill_level', 'Unknown')
                skill_levels[level] = skill_levels.get(level, 0) + 1
            
            if skill_levels:
                chart_data = list(skill_levels.values())
                self.add_chart('pie', chart_data, "Skills Distribution by Level")
        else:
            self.add_paragraph("No skills or certifications recorded.")
        
        self.add_spacer()
        
        # Expiring certifications
        self.add_section("Expiring Certifications", 2)
        
        if self.skills:
            today = datetime.now().date()
            expiring_soon = []
            
            for skill in self.skills:
                if skill.get('expiry_date'):
                    expiry_date = skill['expiry_date']
                    if isinstance(expiry_date, str):
                        try:
                            expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
                        except ValueError:
                            continue
                    
                    days_until_expiry = (expiry_date - today).days
                    if days_until_expiry <= 90:  # Expiring in the next 90 days
                        expiring_soon.append({
                            'skill_name': skill.get('skill_name', 'N/A'),
                            'certification': skill.get('certification', 'N/A'),
                            'expiry_date': expiry_date,
                            'days_remaining': days_until_expiry
                        })
            
            if expiring_soon:
                expiring_data = [["Skill", "Certification", "Expiry Date", "Days Remaining"]]
                for skill in sorted(expiring_soon, key=lambda x: x['days_remaining']):
                    expiring_data.append([
                        skill['skill_name'],
                        skill['certification'],
                        str(skill['expiry_date']),
                        str(skill['days_remaining'])
                    ])
                self.add_table(expiring_data)
            else:
                self.add_paragraph("No certifications expiring in the next 90 days.")
        else:
            self.add_paragraph("No skills or certifications recorded.")
    
    def generate_training_report(self):
        """Generate a training-focused report."""
        # Training overview
        self.add_section("Training Overview")
        
        basic_info = {
            "Employee ID": self.craftsman.get('employee_id', 'N/A'),
            "Name": f"{self.craftsman.get('first_name', '')} {self.craftsman.get('last_name', '')}",
            "Specialization": self.craftsman.get('specialization', 'N/A'),
            "Experience Level": self.craftsman.get('experience_level', 'N/A')
        }
        self.add_info_box("Craftsman Details", basic_info)
        
        self.add_spacer()
        
        # Training records
        self.add_section("Training Records")
        
        if self.training:
            training_data = [["Training", "Start Date", "Completion Date", "Provider", "Certification", "Status"]]
            for record in self.training:
                training_data.append([
                    record.get('training_name', 'N/A'),
                    str(record.get('training_date', 'N/A')),
                    str(record.get('completion_date', 'N/A')),
                    record.get('training_provider', 'N/A'),
                    record.get('certification_received', 'N/A'),
                    record.get('training_status', 'N/A')
                ])
            self.add_table(training_data)
            
            # Add training status chart
            status_counts = {}
            for record in self.training:
                status = record.get('training_status', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            if status_counts:
                chart_data = list(status_counts.values())
                self.add_chart('pie', chart_data, "Training Status Distribution")
        else:
            self.add_paragraph("No training records available.")
        
        self.add_spacer()
        
        # Upcoming and in-progress training
        self.add_section("Upcoming & In-Progress Training", 2)
        
        if self.training:
            upcoming = [t for t in self.training if t.get('training_status') in ['Scheduled', 'In Progress']]
            if upcoming:
                upcoming_data = [["Training", "Start Date", "Provider", "Status"]]
                for record in upcoming:
                    upcoming_data.append([
                        record.get('training_name', 'N/A'),
                        str(record.get('training_date', 'N/A')),
                        record.get('training_provider', 'N/A'),
                        record.get('training_status', 'N/A')
                    ])
                self.add_table(upcoming_data)
            else:
                self.add_paragraph("No upcoming or in-progress training.")
        else:
            self.add_paragraph("No training records available.")


class TeamReport(Report):
    """Report for team information."""
    
    def __init__(self, team_data, filename=None):
        """
        Initialize a team report.
        
        Args:
            team_data: Dictionary containing team data
            filename: Optional filename
        """
        self.team_name = team_data.get('team_name', 'Unknown Team')
        self.team_leader = team_data.get('team_leader', 'N/A')
        self.description = team_data.get('description', '')
        self.members = team_data.get('members', [])
        self.performance = team_data.get('performance', {})
        
        # Generate title
        title = f"Team Report - {self.team_name}"
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = "".join([c if c.isalnum() else "_" for c in self.team_name])
            filename = f"team_report_{safe_name}_{timestamp}.pdf"
        
        super().__init__(title, filename)
    
    def generate(self):
        """Generate the team report."""
        self.add_title()
        
        # Team information section
        self.add_section("Team Information")
        
        team_info = {
            "Team Name": self.team_name,
            "Team Leader": self.team_leader,
            "Number of Members": len(self.members),
            "Description": self.description or "No description available."
        }
        
        self.add_info_box("Team Details", team_info)
        self.add_spacer()
        
        # Team members section
        self.add_section("Team Members")
        
        if self.members:
            members_data = [["Name", "Role", "Specialization", "Experience Level", "Joined Date"]]
            for member in self.members:
                members_data.append([
                    f"{member.get('first_name', '')} {member.get('last_name', '')}",
                    member.get('role', 'N/A'),
                    member.get('specialization', 'N/A'),
                    member.get('experience_level', 'N/A'),
                    str(member.get('joined_date', 'N/A'))
                ])
            self.add_table(members_data)
            
            # Add specialization distribution chart
            spec_counts = {}
            for member in self.members:
                spec = member.get('specialization', 'Unknown')
                spec_counts[spec] = spec_counts.get(spec, 0) + 1
            
            if spec_counts:
                chart_data = list(spec_counts.values())
                self.add_chart('pie', chart_data, "Team Specialization Distribution")
        else:
            self.add_paragraph("No team members found.")
        
        self.add_spacer()
        
        # Team performance section
        self.add_section("Team Performance")
        
        if self.performance:
            performance_info = {
                "Tasks Completed (Last Month)": self.performance.get('tasks_completed', 'N/A'),
                "Average Completion Time": f"{self.performance.get('avg_completion_time', 'N/A')} hours",
                "Team Efficiency Rate": f"{self.performance.get('efficiency_rate', 'N/A')}%",
                "On-Time Completion Rate": f"{self.performance.get('on_time_rate', 'N/A')}%"
            }
            self.add_info_box("Performance Metrics", performance_info)
            
            # Add performance chart if data available
            if 'monthly_data' in self.performance:
                monthly_data = self.performance['monthly_data']
                if monthly_data:
                    chart_data = [[d.get('count', 0) for d in monthly_data]]
                    self.add_chart('bar', chart_data, "Monthly Work Orders Completed")
        else:
            self.add_paragraph("No performance metrics available.")
        
        self.add_footer()
        return self.build()


class EquipmentReport(Report):
    """Report for equipment information."""
    
    def __init__(self, equipment_data, report_type="complete", filename=None):
        """
        Initialize an equipment report.
        
        Args:
            equipment_data: Dictionary containing equipment data
            report_type: Type of report ('complete', 'maintenance', 'technical', 'safety')
            filename: Optional filename
        """
        self.equipment = equipment_data.get('equipment', {})
        self.technical_info = equipment_data.get('technical_info', {})
        self.maintenance_history = equipment_data.get('maintenance_history', [])
        self.maintenance_schedule = equipment_data.get('maintenance_schedule', [])
        self.tools = equipment_data.get('tools', [])
        self.safety_info = equipment_data.get('safety_info', {})
        self.report_type = report_type
        
        # Generate title based on report type
        equipment_name = self.equipment.get('equipment_name', 'Unknown Equipment')
        if report_type == "complete":
            title = f"Equipment Report - {equipment_name}"
        elif report_type == "maintenance":
            title = f"Maintenance Report - {equipment_name}"
        elif report_type == "technical":
            title = f"Technical Report - {equipment_name}"
        elif report_type == "safety":
            title = f"Safety Report - {equipment_name}"
        else:
            title = f"Equipment Report - {equipment_name}"
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = "".join([c if c.isalnum() else "_" for c in equipment_name])
            filename = f"equipment_{report_type}_{safe_name}_{timestamp}.pdf"
        
        super().__init__(title, filename)
    
    def generate(self):
        """Generate the report content based on report type."""
        self.add_title()
        
        if self.report_type == "complete":
            self.generate_complete_report()
        elif self.report_type == "maintenance":
            self.generate_maintenance_report()
        elif self.report_type == "technical":
            self.generate_technical_report()
        elif self.report_type == "safety":
            self.generate_safety_report()
        else:
            self.generate_complete_report()
        
        self.add_footer()
        return self.build()
    
    def generate_complete_report(self):
        """Generate a complete equipment report."""
        # Basic information section
        self.add_section("Equipment Information")
        
        basic_info = {
            "Equipment ID": self.equipment.get('equipment_id', 'N/A'),
            "Equipment Name": self.equipment.get('equipment_name', 'N/A'),
            "Part Number": self.equipment.get('part_number', 'N/A'),
            "Manufacturer": self.equipment.get('manufacturer', 'N/A'),
            "Model": self.equipment.get('model', 'N/A'),
            "Serial Number": self.equipment.get('serial_number', 'N/A'),
            "Location": self.equipment.get('location', 'N/A'),
            "Installation Date": str(self.equipment.get('installation_date', 'N/A')),
            "Status": self.equipment.get('status', 'N/A')
        }
        
        self.add_info_box("Equipment Details", basic_info)
        self.add_spacer()
        
        # Technical information section
        self.add_section("Technical Specifications")
        
        if self.technical_info:
            tech_info = {
                "Power Requirements": self.technical_info.get('power_requirements', 'N/A'),
                "Operating Temperature": self.technical_info.get('operating_temperature', 'N/A'),
                "Weight": self.technical_info.get('weight', 'N/A'),
                "Dimensions": self.technical_info.get('dimensions', 'N/A'),
                "Operating Pressure": self.technical_info.get('operating_pressure', 'N/A'),
                "Capacity": self.technical_info.get('capacity', 'N/A'),
                "Precision/Accuracy": self.technical_info.get('precision_accuracy', 'N/A')
            }
            
            self.add_info_box("Technical Details", tech_info)
            
            if self.technical_info.get('detailed_specifications'):
                self.add_section("Detailed Specifications", 2)
                self.add_paragraph(self.technical_info.get('detailed_specifications'))
        else:
            self.add_paragraph("No technical information available.")
        
        self.add_spacer()
        
        # Maintenance schedule section
        self.add_section("Maintenance Schedule")
        
        if self.maintenance_schedule:
            schedule_data = [["Task", "Frequency", "Last Done", "Next Due", "Required Parts"]]
            for task in self.maintenance_schedule:
                schedule_data.append([
                    task.get('task_name', 'N/A'),
                    f"{task.get('frequency', 'N/A')} {task.get('frequency_unit', '')}",
                    str(task.get('last_done', 'N/A')),
                    str(task.get('next_due', 'N/A')),
                    task.get('required_parts', 'N/A')
                ])
            self.add_table(schedule_data)
        else:
            self.add_paragraph("No maintenance schedule available.")
        
        self.add_spacer()
        
        # Maintenance history section
        self.add_section("Maintenance History")
        
        if self.maintenance_history:
            # Only show the 10 most recent entries
            recent_history = sorted(
                self.maintenance_history, 
                key=lambda x: x.get('date', '1900-01-01'), 
                reverse=True
            )[:10]
            
            history_data = [["Date", "Event Type", "Description", "Performed By"]]
            for entry in recent_history:
                history_data.append([
                    str(entry.get('date', 'N/A')),
                    entry.get('event_type', 'N/A'),
                    entry.get('description', 'N/A'),
                    entry.get('performed_by', 'N/A')
                ])
            self.add_table(history_data)
        else:
            self.add_paragraph("No maintenance history available.")
        
        self.add_spacer()
        
        # Special tools section
        self.add_section("Special Tools")
        
        if self.tools:
            tools_data = [["Tool Name", "Specification", "Purpose", "Location"]]
            for tool in self.tools:
                tools_data.append([
                    tool.get('tool_name', 'N/A'),
                    tool.get('specification', 'N/A'),
                    tool.get('purpose', 'N/A'),
                    tool.get('location', 'N/A')
                ])
            self.add_table(tools_data)
        else:
            self.add_paragraph("No special tools listed.")
        
        self.add_spacer()
        
        # Safety information section
        self.add_section("Safety Information")
        
        if self.safety_info:
            safety_info = {
                "PPE Requirements": self.safety_info.get('ppe_requirements', 'N/A'),
                "Operating Precautions": self.safety_info.get('operating_precautions', 'N/A'),
                "Emergency Procedures": self.safety_info.get('emergency_procedures', 'N/A'),
                "Hazardous Materials": self.safety_info.get('hazardous_materials', 'N/A'),
                "Lockout Procedures": self.safety_info.get('lockout_procedures', 'N/A')
            }
            
            self.add_info_box("Safety Details", safety_info)
        else:
            self.add_paragraph("No safety information available.")
    
    def generate_maintenance_report(self):
        """Generate a maintenance-focused report."""
        # Basic equipment info
        self.add_section("Equipment Information")
        
        basic_info = {
            "Equipment ID": self.equipment.get('equipment_id', 'N/A'),
            "Equipment Name": self.equipment.get('equipment_name', 'N/A'),
            "Part Number": self.equipment.get('part_number', 'N/A'),
            "Manufacturer": self.equipment.get('manufacturer', 'N/A'),
            "Model": self.equipment.get('model', 'N/A'),
            "Status": self.equipment.get('status', 'N/A')
        }
        
        self.add_info_box("Equipment Details", basic_info)
        self.add_spacer()
        
        # Maintenance schedule section
        self.add_section("Maintenance Schedule")
        
        if self.maintenance_schedule:
            # Separate upcoming and overdue tasks
            today = datetime.now().date()
            upcoming = []
            overdue = []
            
            for task in self.maintenance_schedule:
                next_due = task.get('next_due')
                if isinstance(next_due, str):
                    try:
                        next_due = datetime.strptime(next_due, '%Y-%m-%d').date()
                    except ValueError:
                        continue
                
                if next_due < today:
                    overdue.append(task)
                else:
                    upcoming.append(task)
            
            # Show overdue tasks
            self.add_section("Overdue Tasks", 2)
            if overdue:
                overdue_data = [["Task", "Frequency", "Last Done", "Next Due", "Days Overdue"]]
                for task in sorted(overdue, key=lambda x: x.get('next_due', '1900-01-01')):
                    next_due = task.get('next_due')
                    if isinstance(next_due, str):
                        try:
                            next_due = datetime.strptime(next_due, '%Y-%m-%d').date()
                        except ValueError:
                            next_due = today
                    
                    days_overdue = (today - next_due).days
                    
                    overdue_data.append([
                        task.get('task_name', 'N/A'),
                        f"{task.get('frequency', 'N/A')} {task.get('frequency_unit', '')}",
                        str(task.get('last_done', 'N/A')),
                        str(next_due),
                        str(days_overdue)
                    ])
                self.add_table(overdue_data)
            else:
                self.add_paragraph("No overdue maintenance tasks.")
            
            # Show upcoming tasks
            self.add_section("Upcoming Tasks", 2)
            if upcoming:
                upcoming_data = [["Task", "Frequency", "Last Done", "Next Due", "Days Until Due"]]
                for task in sorted(upcoming, key=lambda x: x.get('next_due', '2100-01-01')):
                    next_due = task.get('next_due')
                    if isinstance(next_due, str):
                        try:
                            next_due = datetime.strptime(next_due, '%Y-%m-%d').date()
                        except ValueError:
                            next_due = today
                    
                    days_until = (next_due - today).days
                    
                    upcoming_data.append([
                        task.get('task_name', 'N/A'),
                        f"{task.get('frequency', 'N/A')} {task.get('frequency_unit', '')}",
                        str(task.get('last_done', 'N/A')),
                        str(next_due),
                        str(days_until)
                    ])
                self.add_table(upcoming_data)
            else:
                self.add_paragraph("No upcoming maintenance tasks.")
        else:
            self.add_paragraph("No maintenance schedule available.")
        
        self.add_spacer()
        
        # Maintenance history section
        self.add_section("Maintenance History")
        
        if self.maintenance_history:
            history_data = [["Date", "Event Type", "Description", "Performed By"]]
            for entry in sorted(self.maintenance_history, key=lambda x: x.get('date', '1900-01-01'), reverse=True):
                history_data.append([
                    str(entry.get('date', 'N/A')),
                    entry.get('event_type', 'N/A'),
                    entry.get('description', 'N/A'),
                    entry.get('performed_by', 'N/A')
                ])
            self.add_table(history_data)
            
            # Add maintenance history chart
            if len(self.maintenance_history) > 0:
                # Count maintenance events by month for the last 12 months
                month_counts = {}
                today = datetime.now().date()
                for i in range(12):
                    month = (today.replace(day=1) - timedelta(days=i*30)).strftime('%Y-%m')
            month_counts[month] = 0
            
            for entry in self.maintenance_history:
                date = entry.get('date')
                if isinstance(date, str):
                    try:
                        date = datetime.strptime(date, '%Y-%m-%d').date()
                    except ValueError:
                        continue
            
            month = date.strftime('%Y-%m')
            if month in month_counts:
                month_counts[month] += 1
            
            chart_data = [[month_counts[m] for m in sorted(month_counts.keys())]]
            self.add_chart('bar', chart_data, "Maintenance Events by Month")
        else:
            self.add_paragraph("No maintenance history available.")
    
    def generate_technical_report(self):
        """Generate a technical-focused report."""
        # Basic equipment info
        self.add_section("Equipment Information")
        
        basic_info = {
            "Equipment ID": self.equipment.get('equipment_id', 'N/A'),
            "Equipment Name": self.equipment.get('equipment_name', 'N/A'),
            "Part Number": self.equipment.get('part_number', 'N/A'),
            "Manufacturer": self.equipment.get('manufacturer', 'N/A'),
            "Model": self.equipment.get('model', 'N/A'),
            "Serial Number": self.equipment.get('serial_number', 'N/A')
        }
        
        self.add_info_box("Equipment Details", basic_info)
        self.add_spacer()
        
        # Technical information section
        self.add_section("Technical Specifications")
        
        if self.technical_info:
            tech_info = {
                "Power Requirements": self.technical_info.get('power_requirements', 'N/A'),
                "Operating Temperature": self.technical_info.get('operating_temperature', 'N/A'),
                "Weight": self.technical_info.get('weight', 'N/A'),
                "Dimensions": self.technical_info.get('dimensions', 'N/A'),
                "Operating Pressure": self.technical_info.get('operating_pressure', 'N/A'),
                "Capacity": self.technical_info.get('capacity', 'N/A'),
                "Precision/Accuracy": self.technical_info.get('precision_accuracy', 'N/A')
            }
            
            self.add_info_box("Technical Details", tech_info)
            
            if self.technical_info.get('detailed_specifications'):
                self.add_section("Detailed Specifications", 2)
                self.add_paragraph(self.technical_info.get('detailed_specifications'))
        else:
            self.add_paragraph("No technical information available.")
        
        self.add_spacer()
        
        # Special tools section
        self.add_section("Special Tools")
        
        if self.tools:
            tools_data = [["Tool Name", "Specification", "Purpose", "Location"]]
            for tool in self.tools:
                tools_data.append([
                    tool.get('tool_name', 'N/A'),
                    tool.get('specification', 'N/A'),
                    tool.get('purpose', 'N/A'),
                    tool.get('location', 'N/A')
                ])
            self.add_table(tools_data)
        else:
            self.add_paragraph("No special tools listed.")
    
    def generate_safety_report(self):
        """Generate a safety-focused report."""
        # Basic equipment info
        self.add_section("Equipment Information")
        
        basic_info = {
            "Equipment ID": self.equipment.get('equipment_id', 'N/A'),
            "Equipment Name": self.equipment.get('equipment_name', 'N/A'),
            "Manufacturer": self.equipment.get('manufacturer', 'N/A'),
            "Model": self.equipment.get('model', 'N/A'),
            "Location": self.equipment.get('location', 'N/A'),
            "Status": self.equipment.get('status', 'N/A')
        }
        
        self.add_info_box("Equipment Details", basic_info)
        self.add_spacer()
        
        # Safety information section
        self.add_section("Safety Information")
        
        if self.safety_info:
            # PPE Requirements
            self.add_section("PPE Requirements", 2)
            self.add_paragraph(self.safety_info.get('ppe_requirements', 'No PPE requirements specified.'))
            
            # Operating Precautions
            self.add_section("Operating Precautions", 2)
            self.add_paragraph(self.safety_info.get('operating_precautions', 'No operating precautions specified.'))
            
            # Emergency Procedures
            self.add_section("Emergency Procedures", 2)
            self.add_paragraph(self.safety_info.get('emergency_procedures', 'No emergency procedures specified.'))
            
            # Hazardous Materials
            self.add_section("Hazardous Materials", 2)
            self.add_paragraph(self.safety_info.get('hazardous_materials', 'No hazardous materials specified.'))
            
            # Lockout Procedures
            self.add_section("Lockout Procedures", 2)
            self.add_paragraph(self.safety_info.get('lockout_procedures', 'No lockout procedures specified.'))
        else:
            self.add_paragraph("No safety information available.")
        
        self.add_spacer()
        
        # Safety incidents section
        self.add_section("Safety Incidents")
        
        if self.maintenance_history:
            # Filter for safety-related incidents
            safety_incidents = [
                entry for entry in self.maintenance_history 
                if entry.get('event_type', '').lower() in ['incident', 'accident', 'safety']
            ]
            
            if safety_incidents:
                incidents_data = [["Date", "Description", "Reported By"]]
                for incident in sorted(safety_incidents, key=lambda x: x.get('date', '1900-01-01'), reverse=True):
                    incidents_data.append([
                        str(incident.get('date', 'N/A')),
                        incident.get('description', 'N/A'),
                        incident.get('performed_by', 'N/A')
                    ])
                self.add_table(incidents_data)
            else:
                self.add_paragraph("No safety incidents recorded.")
        else:
            self.add_paragraph("No maintenance history available.")


class WorkOrderReport(Report):
    """Report for work order information."""
    
    def __init__(self, work_order_data, report_type="summary", filename=None):
        """
        Initialize a work order report.
        
        Args:
            work_order_data: Dictionary containing work order data
            report_type: Type of report ('summary', 'detail', 'cost')
            filename: Optional filename
        """
        self.work_orders = work_order_data.get('work_orders', [])
        self.summary = work_order_data.get('summary', {})
        self.report_type = report_type
        
        # Generate title based on report type
        if report_type == "summary":
            title = "Work Orders Summary Report"
        elif report_type == "detail":
            title = "Work Orders Detailed Report"
        elif report_type == "cost":
            title = "Work Orders Cost Analysis Report"
        else:
            title = "Work Orders Report"
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"work_orders_{report_type}_{timestamp}.pdf"
        
        super().__init__(title, filename)
    
    def generate(self):
        """Generate the report content based on report type."""
        self.add_title()
        
        if self.report_type == "summary":
            self.generate_summary_report()
        elif self.report_type == "detail":
            self.generate_detail_report()
        elif self.report_type == "cost":
            self.generate_cost_report()
        else:
            self.generate_summary_report()
        
        self.add_footer()
        return self.build()
    
    def generate_summary_report(self):
        """Generate a summary work orders report."""
        # Report parameters
        self.add_section("Report Parameters")
        
        params = {
            "Start Date": self.summary.get('start_date', 'N/A'),
            "End Date": self.summary.get('end_date', 'N/A'),
            "Status Filter": self.summary.get('status_filter', 'All'),
            "Total Work Orders": self.summary.get('total_work_orders', 0)
        }
        
        self.add_info_box("Parameters", params)
        self.add_spacer()
        
        # Work orders summary
        self.add_section("Work Orders Summary")
        
        if self.work_orders:
            # Status distribution
            status_counts = {}
            for wo in self.work_orders:
                status = wo.get('status', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            status_info = {status: count for status, count in status_counts.items()}
            self.add_info_box("Status Distribution", status_info)
            
            # Add status chart
            if status_counts:
                chart_data = list(status_counts.values())
                self.add_chart('pie', chart_data, "Work Orders by Status")
            
            # Priority distribution
            priority_counts = {}
            for wo in self.work_orders:
                priority = wo.get('priority', 'Unknown')
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            priority_info = {priority: count for priority, count in priority_counts.items()}
            self.add_info_box("Priority Distribution", priority_info)
            
            # Add priority chart
            if priority_counts:
                chart_data = list(priority_counts.values())
                self.add_chart('pie', chart_data, "Work Orders by Priority")
            
            # Recent work orders
            self.add_section("Recent Work Orders")
            
            # Show the 10 most recent work orders
            recent_orders = sorted(
                self.work_orders,
                key=lambda x: x.get('created_date', '1900-01-01'),
                reverse=True
            )[:10]
            
            if recent_orders:
                recent_data = [["ID", "Title", "Equipment", "Status", "Priority", "Due Date"]]
                for wo in recent_orders:
                    recent_data.append([
                        str(wo.get('work_order_id', 'N/A')),
                        wo.get('title', 'N/A'),
                        wo.get('equipment_name', 'N/A'),
                        wo.get('status', 'N/A'),
                        wo.get('priority', 'N/A'),
                        str(wo.get('due_date', 'N/A'))
                    ])
                self.add_table(recent_data)
            else:
                self.add_paragraph("No work orders available.")
        else:
            self.add_paragraph("No work orders available for the selected period.")
    
    def generate_detail_report(self):
        """Generate a detailed work orders report."""
        # Report parameters
        self.add_section("Report Parameters")
        
        params = {
            "Start Date": self.summary.get('start_date', 'N/A'),
            "End Date": self.summary.get('end_date', 'N/A'),
            "Status Filter": self.summary.get('status_filter', 'All'),
            "Total Work Orders": self.summary.get('total_work_orders', 0)
        }
        
        self.add_info_box("Parameters", params)
        self.add_spacer()
        
        # Work orders details
        self.add_section("Work Orders Details")
        
        if self.work_orders:
            # Group work orders by status
            status_groups = {}
            for wo in self.work_orders:
                status = wo.get('status', 'Unknown')
                if status not in status_groups:
                    status_groups[status] = []
                status_groups[status].append(wo)
            
            # Display work orders by status
            for status, orders in status_groups.items():
                self.add_section(f"{status} Work Orders", 2)
                
                orders_data = [["ID", "Title", "Equipment", "Assigned To", "Created Date", "Due Date"]]
                for wo in orders:
                    orders_data.append([
                        str(wo.get('work_order_id', 'N/A')),
                        wo.get('title', 'N/A'),
                        wo.get('equipment_name', 'N/A'),
                        wo.get('assigned_to', 'Unassigned'),
                        str(wo.get('created_date', 'N/A')),
                        str(wo.get('due_date', 'N/A'))
                    ])
                self.add_table(orders_data)
                self.add_spacer()
        else:
            self.add_paragraph("No work orders available for the selected period.")
    
    def generate_cost_report(self):
        """Generate a cost analysis work orders report."""
        # Report parameters
        self.add_section("Report Parameters")
        
        params = {
            "Start Date": self.summary.get('start_date', 'N/A'),
            "End Date": self.summary.get('end_date', 'N/A'),
            "Status Filter": self.summary.get('status_filter', 'All'),
            "Total Work Orders": self.summary.get('total_work_orders', 0)
        }
        
        self.add_info_box("Parameters", params)
        self.add_spacer()
        
        # Cost summary
        self.add_section("Cost Summary")
        
        if 'cost_summary' in self.summary:
            cost_summary = self.summary['cost_summary']
            
            summary_info = {
                "Total Labor Hours": f"{cost_summary.get('total_hours', 0):.2f}",
                "Total Labor Cost": f"${cost_summary.get('total_labor_cost', 0):.2f}",
                "Total Parts Cost": f"${cost_summary.get('total_parts_cost', 0):.2f}",
                "Grand Total": f"${cost_summary.get('grand_total', 0):.2f}"
            }
            
            self.add_info_box("Cost Totals", summary_info)
            
            # Add cost chart
            if 'cost_by_month' in cost_summary:
                monthly_costs = cost_summary['cost_by_month']
                if monthly_costs:
                    labor_costs = [month.get('labor_cost', 0) for month in monthly_costs]
                    parts_costs = [month.get('parts_cost', 0) for month in monthly_costs]
                    chart_data = [labor_costs, parts_costs]
                    self.add_chart('bar', chart_data, "Monthly Costs (Labor vs Parts)")
        else:
            self.add_paragraph("No cost data available.")
        
        self.add_spacer()
        
        # Cost details
        self.add_section("Cost Details by Work Order")
        
        if self.work_orders and any('labor_cost' in wo or 'parts_cost' in wo for wo in self.work_orders):
            cost_data = [["ID", "Title", "Labor Hours", "Labor Cost", "Parts Cost", "Total Cost"]]
            for wo in self.work_orders:
                labor_hours = wo.get('labor_hours', 0) or 0
                labor_cost = wo.get('labor_cost', 0) or 0
                parts_cost = wo.get('parts_cost', 0) or 0
                total_cost = labor_cost + parts_cost
                
                cost_data.append([
                    str(wo.get('work_order_id', 'N/A')),
                    wo.get('title', 'N/A'),
                    f"{labor_hours:.2f}",
                    f"${labor_cost:.2f}",
                    f"${parts_cost:.2f}",
                    f"${total_cost:.2f}"
                ])
            self.add_table(cost_data)
        else:
            self.add_paragraph("No detailed cost data available for work orders.")


class InventoryReport(Report):
    """Report for inventory information."""
    
    def __init__(self, report_data, filename=None):
        """
        Initialize an inventory report.
        
        Args:
            report_data: Dictionary containing inventory data and summary
            filename: Optional filename
        """
        self.items = report_data.get('items', [])
        self.summary = report_data.get('summary', {})
        
        # Generate title
        title = "Inventory Report"
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"inventory_report_{timestamp}.pdf"
        
        super().__init__(title, filename)
    
    def generate(self):
        """Generate the inventory report."""
        self.add_title()
        
        # Summary section
        self.add_section("Summary")
        
        summary_info = {
            "Total Items": self.summary.get('total_items', 0),
            "Total Value": f"${self.summary.get('total_value', 0):.2f}",
            "Low Stock Items": self.summary.get('low_stock_items', 0),
            "Report Date": self.summary.get('report_date', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.add_info_box("Inventory Summary", summary_info)
        self.add_spacer()
        
        # Inventory details section
        self.add_section("Inventory Details")
        
        if self.items:
            items_data = [["Item Code", "Name", "Category", "Quantity", "Unit", "Location", "Unit Cost", "Total Value"]]
            for item in self.items:
                total_value = float(item.get('quantity', 0)) * float(item.get('unit_cost', 0))
                items_data.append([
                    item.get('item_code', 'N/A'),
                    item.get('name', 'N/A'),
                    item.get('category', 'N/A'),
                    str(item.get('quantity', 0)),
                    item.get('unit', 'N/A'),
                    item.get('location', 'N/A'),
                    f"${float(item.get('unit_cost', 0)):.2f}",
                    f"${total_value:.2f}"
                ])
            self.add_table(items_data)
        else:
            self.add_paragraph("No inventory items found.")
        
        self.add_footer()
        return self.build()


class InventoryValuationReport(Report):
    """Report for inventory valuation analysis."""
    
    def __init__(self, report_data, filename=None):
        """
        Initialize an inventory valuation report.
        
        Args:
            report_data: Dictionary containing inventory data and valuations
            filename: Optional filename
        """
        self.items = report_data.get('items', [])
        self.valuations = report_data.get('valuations', {})
        self.summary = report_data.get('summary', {})
        
        # Generate title
        title = "Inventory Valuation Report"
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"inventory_valuation_{timestamp}.pdf"
        
        super().__init__(title, filename)
    
    def generate(self):
        """Generate the valuation report."""
        self.add_title()
        
        # Summary section
        self.add_section("Summary")
        
        summary_info = {
            "Total Inventory Value": f"${self.summary.get('total_value', 0):.2f}",
            "Report Date": self.summary.get('report_date', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.add_info_box("Valuation Summary", summary_info)
        self.add_spacer()
        
        # Category valuation section
        self.add_section("Valuation by Category")
        
        if self.valuations:
            valuation_data = [["Category", "Item Count", "Total Value", "Percentage"]]
            total_value = self.summary.get('total_value', 0)
            
            for category, data in self.valuations.items():
                percentage = (data['value'] / total_value * 100) if total_value > 0 else 0
                valuation_data.append([
                    category,
                    str(data['count']),
                    f"${data['value']:.2f}",
                    f"{percentage:.1f}%"
                ])
            
            self.add_table(valuation_data)
            
            # Add pie chart of category values
            values = [data['value'] for data in self.valuations.values()]
            self.add_chart('pie', values, "Value Distribution by Category")
        else:
            self.add_paragraph("No valuation data available.")
        
        self.add_footer()
        return self.build()


class InventoryMovementReport(Report):
    """Report for inventory movement analysis."""
    
    def __init__(self, report_data, filename=None):
        """
        Initialize an inventory movement report.
        
        Args:
            report_data: Dictionary containing inventory data and movement information
            filename: Optional filename
        """
        self.items = report_data.get('items', [])
        self.movement_data = report_data.get('movement_data', [])
        self.summary = report_data.get('summary', {})
        
        # Generate title
        title = "Inventory Movement Report"
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"inventory_movement_{timestamp}.pdf"
        
        super().__init__(title, filename)
    
    def generate(self):
        """Generate the movement report."""
        self.add_title()
        
        # Summary section
        self.add_section("Summary")
        
        summary_info = {
            "Total Items": self.summary.get('total_items', 0),
            "Low Stock Items": self.summary.get('low_stock_items', 0),
            "Items to Reorder": self.summary.get('reorder_items', 0),
            "Report Date": self.summary.get('report_date', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.add_info_box("Movement Summary", summary_info)
        self.add_spacer()
        
        # Movement details section
        self.add_section("Movement Details")
        
        if self.movement_data:
            movement_data = [["Item Code", "Name", "Current Qty", "Min Qty", "Reorder Point", "Status"]]
            for item in self.movement_data:
                movement_data.append([
                    item.get('item_code', 'N/A'),
                    item.get('name', 'N/A'),
                    f"{item.get('quantity', 0)} {item.get('unit', '')}",
                    str(item.get('min_quantity', 0)),
                    str(item.get('reorder_point', 0)),
                    item.get('status', 'N/A')
                ])
            self.add_table(movement_data)
            
            # Add status distribution chart
            status_counts = {}
            for item in self.movement_data:
                status = item.get('status', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            if status_counts:
                values = list(status_counts.values())
                self.add_chart('pie', values, "Item Status Distribution")
        else:
            self.add_paragraph("No movement data available.")
        
        self.add_footer()
        return self.build()


class InventoryCustomReport(Report):
    """Report for custom inventory analysis."""
    
    def __init__(self, report_data, filename=None):
        """
        Initialize a custom inventory report.
        
        Args:
            report_data: Dictionary containing inventory data and selected options
            filename: Optional filename
        """
        self.items = report_data.get('items', [])
        self.options = report_data.get('options', {})
        self.summary = report_data.get('summary', {})
        
        # Generate title
        title = "Custom Inventory Report"
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"inventory_custom_{timestamp}.pdf"
        
        super().__init__(title, filename)
    
    def generate(self):
        """Generate the custom report."""
        self.add_title()
        
        # Add selected sections
        if self.options.get('inventory_summary'):
            self.add_section("Inventory Summary")
            
            summary_info = {
                "Total Items": self.summary.get('total_items', 0),
                "Total Value": f"${self.summary.get('total_value', 0):.2f}",
                "Report Date": self.summary.get('report_date', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.add_info_box("Summary", summary_info)
            self.add_spacer()
        
        if self.options.get('low_stock'):
            self.add_section("Low Stock Items")
            
            low_stock = [item for item in self.items if item.get('quantity', 0) <= item.get('minimum_quantity', 0)]
            if low_stock:
                low_stock_data = [["Item Code", "Name", "Current Qty", "Min Qty", "Location"]]
                for item in low_stock:
                    low_stock_data.append([
                        item.get('item_code', 'N/A'),
                        item.get('name', 'N/A'),
                        str(item.get('quantity', 0)),
                        str(item.get('minimum_quantity', 0)),
                        item.get('location', 'N/A')
                    ])
                self.add_table(low_stock_data)
            else:
                self.add_paragraph("No items are currently below minimum quantity.")
            
            self.add_spacer()
        
        if self.options.get('valuation'):
            self.add_section("Valuation Analysis")
            
            # Calculate valuations by category
            valuations = {}
            for item in self.items:
                category = item.get('category', 'Uncategorized')
                value = float(item.get('quantity', 0)) * float(item.get('unit_cost', 0))
                
                if category not in valuations:
                    valuations[category] = 0.0
                valuations[category] += value
            
            if valuations:
                valuation_data = [["Category", "Total Value"]]
                for category, value in valuations.items():
                    valuation_data.append([category, f"${value:.2f}"])
                self.add_table(valuation_data)
                
                # Add pie chart
                values = list(valuations.values())
                self.add_chart('pie', values, "Value Distribution by Category")
            else:
                self.add_paragraph("No valuation data available.")
            
            self.add_spacer()
        
        if self.options.get('movement'):
            self.add_section("Movement Analysis")
            
            reorder_items = [item for item in self.items if item.get('quantity', 0) <= item.get('reorder_point', 0)]
            if reorder_items:
                reorder_data = [["Item Code", "Name", "Current Qty", "Reorder Point"]]
                for item in reorder_items:
                    reorder_data.append([
                        item.get('item_code', 'N/A'),
                        item.get('name', 'N/A'),
                        str(item.get('quantity', 0)),
                        str(item.get('reorder_point', 0))
                    ])
                self.add_table(reorder_data)
            else:
                self.add_paragraph("No items currently need reordering.")
        
        self.add_footer()
        return self.build()


# Helper functions for creating reports
def create_craftsman_report(db_manager, craftsman_id, report_type="complete", filename=None, return_elements=False):
    """
    Create a craftsman report using data from the database.
    
    Args:
        db_manager: Database manager instance
        craftsman_id: ID of the craftsman
        report_type: Type of report to generate
        filename: Optional filename
        return_elements: If True, return the report elements instead of building the PDF
        
    Returns:
        Path to the generated report file or list of report elements if return_elements is True
    """
    # Get craftsman data
    craftsman = db_manager.get_craftsman_by_id(craftsman_id)
    
    if not craftsman:
        return None
    
    # Get additional data
    craftsman_data = {
        'craftsman': craftsman,
        'skills': db_manager.get_craftsman_skills(craftsman_id),
        'training': db_manager.get_craftsman_training(craftsman_id),
        'work_history': db_manager.get_craftsman_work_history(craftsman_id),
        'performance': db_manager.get_craftsman_performance(craftsman_id),
        'teams': db_manager.get_craftsman_teams(craftsman_id)
    }
    
    # Create report
    report = CraftsmanReport(craftsman_data, report_type, filename)
    
    # If we need to return elements instead of building the PDF
    if return_elements:
        # Generate the story (content elements)
        report.add_title()
        
        if report_type == "complete":
            report.generate_complete_report()
        elif report_type == "performance":
            report.generate_performance_report()
        elif report_type == "skills":
            report.generate_skills_report()
        elif report_type == "training":
            report.generate_training_report()
        else:
            report.generate_complete_report()
        
        report.add_footer()
        
        # Return the story elements
        return report.story
    else:
        # Generate and return the report path
        return report.generate()


def create_team_report(db_manager, team_name):
    """
    Create a team report using data from the database.
    
    Args:
        db_manager: Database manager instance
        team_name: Name of the team
        
    Returns:
        Path to the generated report file
    """
    # Get team data
    team = db_manager.get_team_by_name(team_name)
    
    if not team:
        return None
    
    # Get additional data
    team_data = {
        'team_name': team.get('team_name', 'Unknown Team'),
        'team_leader': f"{team.get('leader_first_name', '')} {team.get('leader_last_name', '')}",
        'description': team.get('description', ''),
        'members': db_manager.get_team_members(team.get('team_id')),
        'performance': db_manager.get_team_performance(team.get('team_id'))
    }
    
    # Create and generate report
    report = TeamReport(team_data)
    return report.generate()


def create_equipment_report(db_manager, equipment_id, report_type="complete"):
    """
    Create an equipment report using data from the database.
    
    Args:
        db_manager: Database manager instance
        equipment_id: ID of the equipment
        report_type: Type of report to generate
        
    Returns:
        Path to the generated report file
    """
    # Get equipment data
    equipment = db_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        return None
    
    # Get additional data
    equipment_data = {
        'equipment': equipment,
        'technical_info': db_manager.get_technical_info(equipment_id),
        'maintenance_history': db_manager.get_equipment_history(equipment_id),
        'maintenance_schedule': db_manager.get_maintenance_schedule(equipment_id),
        'tools': db_manager.get_special_tools(equipment_id),
        'safety_info': db_manager.get_safety_info(equipment_id)
    }
    
    # Create and generate report
    report = EquipmentReport(equipment_data, report_type)
    return report.generate()


def create_work_order_report(db_manager, start_date, end_date, status_filter=None, report_type="summary", custom_fields=None):
    """
    Create a work order report using data from the database.
    
    Args:
        db_manager: Database manager instance
        start_date: Start date for the report period
        end_date: End date for the report period
        status_filter: Optional status filter
        report_type: Type of report to generate
        custom_fields: List of fields to include in custom report
        
    Returns:
        Path to the generated report file
    """
    # Get work orders
    work_orders = db_manager.get_work_orders_for_report(start_date, end_date, status_filter)
    
    if custom_fields:
        # Filter work orders to only include selected fields
        filtered_orders = []
        for wo in work_orders:
            filtered_wo = {field: wo.get(field, '') for field in custom_fields}
            filtered_orders.append(filtered_wo)
        work_orders = filtered_orders
    
    # Prepare summary data
    summary = {
        'start_date': start_date,
        'end_date': end_date,
        'status_filter': status_filter if status_filter else 'All',
        'total_work_orders': len(work_orders)
    }
    
    # Add cost summary for cost reports
    if report_type == "cost":
        cost_data = db_manager.get_work_order_costs(start_date, end_date, status_filter)
        
        # Calculate totals
        total_hours = sum(wo.get('labor_hours', 0) or 0 for wo in cost_data)
        total_labor_cost = sum(wo.get('labor_cost', 0) or 0 for wo in cost_data)
        total_parts_cost = sum(wo.get('parts_cost', 0) or 0 for wo in cost_data)
        grand_total = total_labor_cost + total_parts_cost
        
        summary['cost_summary'] = {
            'total_hours': total_hours,
            'total_labor_cost': total_labor_cost,
            'total_parts_cost': total_parts_cost,
            'grand_total': grand_total
        }
        
        # Use cost data instead of regular work orders
        work_orders = cost_data
    
    # Create report data
    report_data = {
        'work_orders': work_orders,
        'summary': summary
    }
    
    # Create and generate report
    report = WorkOrderReport(report_data, report_type)
    return report.generate()


def open_report_file(file_path):
    """
    Open a report file with the default application.
    
    Args:
        file_path: Path to the report file
    """
    import platform
    import subprocess
    
    try:
        if platform.system() == "Windows":
            os.startfile(file_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", file_path])
        else:  # Linux
            subprocess.run(["xdg-open", file_path])
        return True
    except Exception as e:
        print(f"Error opening report file: {e}")
        return False


def open_containing_folder(file_path):
    """
    Open the folder containing the report file.
    
    Args:
        file_path: Path to the report file
    """
    import platform
    import subprocess
    
    try:
        folder_path = os.path.dirname(file_path)
        if platform.system() == "Windows":
            subprocess.run(['explorer', folder_path])
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(['open', folder_path])
        else:  # Linux
            subprocess.run(['xdg-open', folder_path])
        return True
    except Exception as e:
        print(f"Error opening containing folder: {e}")
        return False