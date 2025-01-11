from pathlib import Path

import win32com.client as win32
from pydantic import BaseModel, ConfigDict, Field

from powerguard.bootstrap import paths
from proto.ups_defines_pb2 import LOAD, MODE, OverLoad, Phase, spec


class WordReportGenerator(BaseModel):
    output_path: Path = Field(default=paths["output_dir"])
    template_path: Path = Field(default=Path(paths["template_dir"]) / "test_report_template.docx")
    WordApp: win32.DispatchBaseClass = None  # Excluded from validation
    WrdDoc: win32.DispatchBaseClass = None

    model_config = ConfigDict(arbitrary_types_allowed=True)  # Allow arbitrary types

    def __init__(self, visible: bool = True, **data):
        super().__init__(**data)
        self.WordApp = win32.gencache.EnsureDispatch('Word.Application')
        self.WordApp.Visible = visible
        self.WrdDoc = self.WordApp.Documents.Add()

    def add_paragraph(self, key: str, value: str):
        """
        Adds a paragraph to the Word document with the format 'Key: Value'.
        """
        paragraph = self.WrdDoc.Content.Paragraphs.Add()
        paragraph.Range.Text = f"{key}: {value}"
        paragraph.Alignment = 2  # Align right
        paragraph.Range.InsertParagraphAfter()

    def save_document(self, file_name: str = "test_report.docx"):
        """
        Saves the Word document to the specified file name within the output_path directory.
        Ensures that the file name and path are valid.
        """
        
        self.output_path.mkdir(parents=True, exist_ok=True)       
        file_path = self.output_path / file_name       
        file_path_str = str(file_path.resolve())        
        if not file_path_str.lower().endswith(".docx"):
            file_path_str += ".docx"
        try:
            # Save the document
            self.WrdDoc.SaveAs(file_path_str)
            print(f"Document saved at: {file_path_str}")
        except Exception as e:
            print(f"Failed to save the document. Error: {e}")
    def copy_pages_from_template(self, page_start: int, page_end: int):
        """
        Copies specific pages from the template file into the current document.
        """
        try:
            # Open the template document
            template_doc = self.WordApp.Documents.Open(str(self.template_path.resolve()))

            # Select and copy the specified range of pages
            template_doc.Range(template_doc.GoTo(1, 1, page_start).Start, 
                               template_doc.GoTo(1, 1, page_end).End).Copy()

            # Paste into the new document
            self.WrdDoc.Content.Paste()

            # Close the template document
            template_doc.Close(False)
            print(f"Copied pages {page_start} to {page_end} from template.")
        except Exception as e:
            print(f"Failed to copy pages from template. Error: {e}")

    def add_specification_table(self, spec_obj):
        """
        Creates a Word table for the UPS specification using the provided Protobuf `spec` object.

        :param spec_obj: A `spec` Protobuf object containing UPS specification details.
        """
        try:
            # Move the insertion point to the end of the document
            range_end = self.WrdDoc.Content
            range_end.Collapse(win32.constants.wdCollapseEnd)  # Move to the end of the content

            # Insert a new paragraph to separate the table from previous content
            range_end.InsertParagraphAfter()
            range_end.Collapse(win32.constants.wdCollapseEnd)  # Collapse again after the paragraph

            # Create the table
            rows = 15  # Number of spec fields + header
            columns = 2  # Key-Value pair format
            table = self.WrdDoc.Tables.Add(range_end, rows, columns)

            # Set table headers
            table.Cell(1, 1).Range.Text = "Specification"
            table.Cell(1, 2).Range.Text = "Value"

            # Extract overload details
            overload_data = {
                "Overload Long": f"{spec_obj.overload_long.load_percentage}% for {spec_obj.overload_long.overload_time_min} minutes",
                "Overload Medium": f"{spec_obj.overload_medium.load_percentage}% for {spec_obj.overload_medium.overload_time_min} minutes",
                "Overload Short": f"{spec_obj.overload_short.load_percentage}% for {spec_obj.overload_short.overload_time_min} minutes",
            }

            # Populate table rows
            spec_data = [
                ("Phase", Phase.Name(spec_obj.phase)),  # Get enum name
                ("Rated VA", spec_obj.rated_va),
                ("Rated Voltage", spec_obj.rated_voltage),
                ("Rated Current", spec_obj.rated_current),
                ("Min Input Voltage", spec_obj.min_input_voltage),
                ("Max Input Voltage", spec_obj.max_input_voltage),
                ("Power Factor Rated Current", spec_obj.pf_rated_current),
                ("Max Continuous Amp", spec_obj.max_continous_amp),
                ("Overload Amp", spec_obj.overload_amp),
                *overload_data.items(),  # Add overload details
                ("Avg Switch Time (ms)", spec_obj.avg_switch_time_ms),
                ("Avg Backup Time (ms)", spec_obj.avg_backup_time_ms),
            ]

            for idx, (key, value) in enumerate(spec_data, start=2):  # Start from row 2 to leave header row
                table.Rows.Item(idx).Cells.Item(1).Range.Text = key
                table.Rows.Item(idx).Cells.Item(2).Range.Text = str(value) if value is not None else "N/A"

            # Apply basic formatting
            table.Rows.Item(1).Range.Font.Bold = True  # Bold header row
            table.Borders.Enable = True  # Enable borders for the table

            print("Specification table added successfully.")
        except Exception as e:
            print(f"Failed to add specification table. Error: {e}")






# Example usage
if __name__ == "__main__":
    from proto.ups_defines_pb2 import LOAD, MODE, OverLoad, Phase, spec
    report = WordReportGenerator()
    overload_long = OverLoad(load_percentage=110, overload_time_min=10)
    overload_medium = OverLoad(load_percentage=125, overload_time_min=5)
    overload_short = OverLoad(load_percentage=150, overload_time_min=2)
    ups_spec = spec(
            phase=Phase.SINGLE_PHASE,  # SINGLE_PHASE from enum Phase
            rated_va=5000,
            rated_voltage=230,
            rated_current=21,
            min_input_voltage=200,
            max_input_voltage=240,
            pf_rated_current=1,  # 1.0 PF represented as 100 for simplicity
            max_continous_amp=25,
            overload_amp=30,
            overload_long=overload_long,
            overload_medium=overload_medium,
            overload_short=overload_short,
            avg_switch_time_ms=500,
            avg_backup_time_ms=120000,
        )

    # Copy pages 1 and 2 from the template
    report.copy_pages_from_template(page_start=1, page_end=3)

    # Add additional paragraphs dynamically
    report.add_paragraph("TestName", "No Load Test")
    report.add_paragraph("Standard", "IEC602040-3 -2021")
    report.add_paragraph("Clause", "6.2.2.4")
    report.add_paragraph("Operation Mode", "NORMAL_MODE")
    report.add_paragraph("Minimum Input Voltage", "180")
    report.add_paragraph("Maximum Input Voltage", "240")
    report.add_paragraph("Step Change", "10V")
    report.add_specification_table(ups_spec)

    # Save the document
    report.save_document()
