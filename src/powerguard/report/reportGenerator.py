import os
import sqlite3
import subprocess
import sys
import xml.etree.ElementTree as ET
from lxml import etree
from docxtpl import DocxTemplate
from docx import Document
from datetime import datetime
from pathlib import Path
from typing import Optional
from zipfile import ZipFile
import shutil

import pprint


from collections import defaultdict
from typing import List, Dict, Any
from pydantic import BaseModel, Field, field_validator

from powerguard.bootstrap import paths
from powerguard.data.data_manager import DataManager


class ReportGenerator(BaseModel):
    """
    ReportGenerator class for generating formatted Word reports using Pydantic.
    """

    data_manager: DataManager
    template_path: Path = Field(default="Report_Template.docx")
    xml_schema_file: str = Field(default="general_schema")
    output_path: Path = Field(default=paths.get("output_dir"))

    @field_validator("template_path")
    def validate_template_path(cls, value: Path) -> Path:
        """
        Ensure the template path exists and is a file.
        """
        # Get the template directory from paths
        template_folder = paths.get("template_dir")
        # Make sure the folder exists, create it if it doesn't
        template_folder.mkdir(parents=True, exist_ok=True)

        # If no template_path was provided, set it to the default in the template folder
        if not value:
            value = template_folder / "Report_Template.docx"

        # Full path to the template file
        full_template_path = template_folder / value

        # Validate if the template file exists and is a file
        if not full_template_path.exists() or not full_template_path.is_file():
            raise ValueError(f"Template file not found: {full_template_path}")

        return full_template_path

    @field_validator("output_path")
    def validate_output_path(cls, value: Path) -> Path:
        """
        Ensure the template path exists and is a file.
        """

        output_folder = paths.get("output_dir")

        output_folder.mkdir(parents=True, exist_ok=True)

        # Full path to the template file
        full_output_folder = output_folder

        # Validate if the template file exists and is a file
        if not full_output_folder.exists() or not full_output_folder.is_dir():
            raise ValueError(f"Output Folder not found: {full_output_folder}")

        return full_output_folder

    def generate_file_name(self, report_data: dict) -> str:
        """
        Generate a file name based on client name, UPS model, date, and report ID.

        Args:
            report_data (dict): The full report data containing `client_name`, `ups_model`, and `report_id`.

        Returns:
            str: The generated file name.
        """
        # Adjusted to use flat keys directly
        client_name = report_data.get("client_name", "UnknownClient")
        ups_model = report_data.get("ups_model", "UnknownModel")
        report_id = report_data.get("test_report_id", "0")  # Updated key for report ID
        date_str = datetime.now().strftime("%Y%m%d")

        print(
            f"Generating filename with: client_name={client_name}, ups_model={ups_model}, report_id={report_id}"
        )

        # Create a sanitized file name
        file_name = f"{client_name}_{ups_model}_{report_id}_{date_str}"
        return file_name.replace(" ", "_")

    def aggregate_report_data(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregates and sorts data from a list of rows into a hierarchical structure.
        Args:
            rows (list): List of dictionaries containing report data.
        Returns:
            dict: Aggregated and sorted report data with power measures coming last.
        """
        if not rows:
            raise ValueError("No rows provided to aggregate")

        if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
            raise TypeError("Rows must be a list of dictionaries")

        # Start with the first row
        aggregated = {
            "test_report_id": rows[0]["test_report_id"],
            "test_name": rows[0]["test_name"],
            "test_description": rows[0]["test_description"],
            "test_result": rows[0]["test_result"],
            "client_name": rows[0]["client_name"],
            "standard": rows[0]["standard"],
            "ups_model": rows[0]["ups_model"],
            "measurements": [],  # This will hold the list of sorted measurements
        }

        # Group data for measurements and power measures
        measurements = defaultdict(lambda: {"power_measures": []})

        for row in rows:
            measurement_id = row["measurement_unique_id"]
            measurement = measurements[measurement_id]

            # Update measurement details, ensuring power measures are added last
            if not measurement.get("measurement_name"):
                measurement.update(
                    {
                        "measurement_unique_id": row.get("measurement_unique_id"),
                        "measurement_name": row.get("measurement_name"),
                        "measurement_timestamp": row.get("measurement_timestamp"),
                        "measurement_loadtype": row.get("measurement_loadtype"),
                        "load_percentage": row.get("load_percentage", 0),
                        "phase_name": row.get("phase_name", "Unknown"),
                        "step_id": row.get("step_id", 0),
                        "steady_state_voltage_tol": row.get(
                            "steady_state_voltage_tol", 0
                        ),
                        "voltage_dc_component": row.get("voltage_dc_component", 0),
                        "load_pf_deviation": row.get("load_pf_deviation", 0),
                        "switch_time_ms": row.get("switch_time_ms", 0),
                        "run_interval_sec": row.get("run_interval_sec", 0),
                        "backup_time_sec": row.get("backup_time_sec", 0),
                        "overload_time_sec": row.get("overload_time_sec", 0),
                        "temperature_1": row.get("temperature_1", 0),
                        "temperature_2": row.get("temperature_2", 0),
                    }
                )

            # Add power measures to this measurement
            if row.get("power_measure_id"):
                measurement["power_measures"].append(
                    {
                        "power_measure_id": row["power_measure_id"],
                        "power_measure_type": row["power_measure_type"],
                        "power_measure_name": row["power_measure_name"],
                        "power_measure_voltage": row["power_measure_voltage"],
                        "power_measure_current": row["power_measure_current"],
                        "power_measure_power": row["power_measure_power"],
                        "power_measure_pf": row["power_measure_pf"],
                    }
                )

        # Sort measurements by `measurement_unique_id`
        sorted_measurements = sorted(
            measurements.values(), key=lambda m: m["measurement_unique_id"]
        )

        # Ensure power measures come last in each measurement
        for measurement in sorted_measurements:
            power_measures = measurement.pop("power_measures", [])
            measurement["power_measures"] = sorted(
                power_measures, key=lambda pm: pm["power_measure_id"]
            )

        # Add sorted measurements to the final report
        aggregated["measurements"] = sorted_measurements

        return aggregated

    def create_xml_from_report(self, report_data: list[dict], file_name: str,flatten:bool =True) -> Path:
        """
        Generate an XML file from the report data, flattening nested dictionaries.

        Args:
            report_data (list[dict]): A list of rows fetched from the database.
            file_name (str): The name of the output XML file.

        Returns:
            Path: The path to the saved XML file.
        """

        def flatten_dict(data, parent_key="", sep="_"):
            """
            Recursively flatten a nested dictionary.
            """
            items = []
            for k, v in data.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    # Recursively flatten dictionaries
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                elif isinstance(v, list):
                    # Handle lists by indexing items
                    for i, item in enumerate(v):
                        indexed_key = f"{new_key}{sep}{i}"
                        if isinstance(item, dict):
                            items.extend(
                                flatten_dict(item, indexed_key, sep=sep).items()
                            )
                        else:
                            items.append((indexed_key, item))
                else:
                    # Add simple key-value pairs
                    items.append((new_key, v))
            return dict(items)

        # Step 1: Aggregate report data into a single dictionary

        aggregated_data = self.aggregate_report_data(report_data)
        pprint.pprint(f"context data dictionary is { aggregated_data }")

        # Step 2: Flatten the report data, including nested dictionaries and lists
        flattened_data = flatten_dict(aggregated_data)
        if flatten:
            xml_data=flattened_data 
        else:
            xml_data= aggregated_data    
        # Step 3: Create XML structure
        root = ET.Element("TestReport")
        for key, value in xml_data.items():
            child = ET.SubElement(root, key)
            # Convert non-string values to strings
            child.text = str(value) if value is not None else ""

        # Step 4: Construct full XML file path in the output directory
        xml_path = self.output_path / file_name
        # Ensure the parent directory exists
        xml_path.parent.mkdir(parents=True, exist_ok=True)

        # Step 5: Check if the file exists and confirm overwrite
        if xml_path.exists():
            print(f"XML file already exists at {xml_path}. Overwriting.")

        # Write XML to file
        tree = ET.ElementTree(root)
        tree.write(xml_path, encoding="utf-8", xml_declaration=True)
        print(f"XML generated and saved to {xml_path}")
        return xml_path

    # def generate_report(self, report_id: int, use_cpp: bool = False):
    #     """
    #     Generate a formatted report using a template and optionally call a C++ executable.

    #     Args:
    #         report_id (int): The ID of the report to generate.
    #         use_cpp (bool): Whether to use the C++ backend (default: False).
    #     """
    #     # Step 1: Retrieve report data from DataManager
    #     rows = self.data_manager.get_test_report(report_id)

    #     if not rows:
    #         raise ValueError(f"No report found for ID {report_id}")

    #     # print(f"Fetched report data for ID {report_id}: {rows}")

    #     # Step 2: Aggregate report data into a single dictionary
    #     report_data = self.aggregate_report_data(rows)

    #     # Step 3: Generate file name
    #     file_name = self.generate_file_name(report_data)

    #     # Step 4: Generate XML
    #     # xml_path = self.create_xml_from_report(rows, f"{file_name}.xml")
    #     xml_path = self.create_xml_from_report(rows, f"{self.xml_schema_file}.xml")
    #     # Step 5: Optionally process XML with C++
    #     if use_cpp:
    #         self.call_cpp_for_processing(xml_path)

    #     # Step 6: Generate the output Word file path
    #     output_file_path = self.output_path / f"{file_name}.docx"

    #     # Step 8: Edit the Word template
    #     self.edit_word_document(output_file_path, xml_path)

    def sanitize_xml_file(self, xml_path):
        # Read the file with encoding that tolerates BOM
        with open(xml_path, "r", encoding="utf-8-sig") as f:
            content = f.read()

        # Strip unnecessary whitespace and extra newlines
        sanitized_content = content.strip()

        # Overwrite the file with cleaned content
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(sanitized_content)

    def call_cpp_for_processing(
        self, xml_path: Path, cpp_executable: Path = Path("process_report")
    ):
        """
        Call a C++ executable to process the XML data.
        """
        if not cpp_executable.exists():
            raise FileNotFoundError(f"C++ executable '{cpp_executable}' not found.")

        # Call the C++ executable with the XML file as an argument
        subprocess.run([str(cpp_executable), str(xml_path)], check=True)
        print("C++ processing completed.")

    # def generate_all_reports(self, output_dir: Path = Path("reports")):
    #     """
    #     Generate XML reports for all test reports in the database.

    #     Args:
    #         output_dir (Path): The directory where the reports will be saved.
    #     """
    #     try:
    #         # Ensure the output directory exists
    #         output_dir.mkdir(parents=True, exist_ok=True)

    #         # Retrieve all TestReport IDs and their test names
    #         reports = self.get_all_report_id_testName()

    #         # Generate XML reports for each entry
    #         for report in reports:
    #             report_id = report["report_id"]

    #             # Fetch the full report data for this report_id
    #             report_data = self.get_test_report(report_id)
    #             if not report_data:
    #                 print(f"Skipping report_id {report_id}: No data found.")
    #                 continue

    #             # Generate the file name
    #             file_name = self.generate_file_name(report_data)

    #             # Generate the XML report
    #             xml_file_path = output_dir / file_name
    #             self.create_xml_from_report(report_data, xml_file_path)
    #             print(f"Report generated: {xml_file_path}")
    #     except sqlite3.Error as e:
    #         raise Exception(f"Error generating reports: {e}")

    # def generate_report(self, report_id: int, use_cpp: bool = False) -> Path:
    #     """
    #     Generates a test report from aggregated data and saves it as a Word document.

    #     Args:
    #         rows (List[Dict[str, Any]]): List of dictionaries containing report data.

    #     Returns:
    #         Path: Path to the generated Word report.
    #     """
    #     # Step 1: Retrieve report data from DataManager
    #     rows = self.data_manager.get_test_report(report_id)

    #     if not rows:
    #         raise ValueError(f"No report found for ID {report_id}")

    #     # print(f"Fetched report data for ID {report_id}: {rows}")

    #     # Step 2: Aggregate report data into a single dictionary

    #     aggregated_data = self.aggregate_report_data(rows)

    #     # Step 3: Generate XML(For future use)

    #     xml_path = self.create_xml_from_report(rows, f"{self.xml_schema_file}.xml")
    #     self.sanitize_xml_file(xml_path)
    #     # Step 4: Optionally process XML with C++
    #     if use_cpp:
    #         self.call_cpp_for_processing(xml_path)
    #     # Step 5:Finally generate the docx
    #     # Ensure output directory exists
    #     self.output_path.mkdir(parents=True, exist_ok=True)

    #     # Generate a base file name
    #     base_file_name = self.generate_file_name(aggregated_data)

    #     # Determine final file name, avoiding duplicates
    #     counter = 1
    #     output_file = self.output_path / f"{base_file_name}.docx"
    #     while output_file.exists():
    #         output_file = self.output_path / f"{base_file_name}({counter}).docx"
    #         counter += 1

    #     # Load the template
    #     template = DocxTemplate(self.template_path)

    #     # Render the template with the aggregated data
    #     template.render(aggregated_data)

    #     # Save the generated report
    #     template.save(output_file)

    #     return output_file
    # def generate_template(self, report_id: str) -> None:
    #     """
    #     Generates a Jinja2-compatible Word template for the report.
    #     """
    #     rows = self.data_manager.get_test_report(report_id)
    #     aggregated_data = self.aggregate_report_data(rows)

    #     doc = Document()
    #     doc.add_heading("Template Document", level=1)
    #     doc.add_paragraph("High-Level Fields:")

    #     for key in aggregated_data:
    #         if key == "measurements":
    #             continue
    #         doc.add_paragraph(f"{{{{ {key} }}}}")

    #     doc.add_heading("Measurements:", level=2)
    #     doc.add_paragraph("{% for measurement in measurements %}")
    #     for m_key in aggregated_data["measurements"][0]:
    #         if m_key == "power_measures":
    #             continue
    #         doc.add_paragraph(f"    {{{{ measurement.{m_key} }}}}")

    #     doc.add_paragraph("    {% for power_measure in measurement.power_measures %}")
    #     for p_key in aggregated_data["measurements"][0]["power_measures"][0]:
    #         doc.add_paragraph(f"        {{{{ power_measure.{p_key} }}}}")
    #     doc.add_paragraph("    {% endfor %}")
    #     doc.add_paragraph("{% endfor %}")

    #     doc.save(self.template_path)
    #     print(f"Template saved to {self.template_path}")
   

    def generate_template(self, report_id: str) -> None:
        """
        Generates a Word template dynamically for test report data.
        """
        # Fetch and aggregate report data
        rows = self.data_manager.get_test_report(report_id)
        aggregated_data = self.aggregate_report_data(rows)

        # Initialize the document
        doc = Document()

        # Add metadata section with placeholders
        doc.add_heading("Test Report", level=1)
        doc.add_paragraph("Report ID: {{ test_report_id }}")
        doc.add_paragraph("Test Name: {{ test_name }}")
        doc.add_paragraph("Description: {{ test_description }}")
        doc.add_paragraph("Result: {{ test_result }}")
        doc.add_paragraph("Client: {{ client_name }}")
        doc.add_paragraph("Standard: {{ standard }}")
        doc.add_paragraph("UPS Model: {{ ups_model }}")

        # Add measurements section with placeholder for looping
        doc.add_heading("Measurements", level=2)
        doc.add_paragraph("{% for measurement in measurements %}")

        # Add measurement details
        doc.add_paragraph("Measurement Details:")
        table = doc.add_table(rows=1, cols=6)
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "Measurement ID"
        hdr_cells[1].text = "Name"
        hdr_cells[2].text = "Timestamp"
        hdr_cells[3].text = "Load Type"
        hdr_cells[4].text = "Load (%)"
        hdr_cells[5].text = "Phase"

        # Loop over measurements to add rows
        doc.add_paragraph("{% for measurement in measurements %}")
        row = table.add_row().cells
        row[0].text = "{{ measurement.measurement_unique_id }}"
        row[1].text = "{{ measurement.measurement_name }}"
        row[2].text = "{{ measurement.measurement_timestamp }}"
        row[3].text = "{{ measurement.measurement_loadtype }}"
        row[4].text = "{{ measurement.load_percentage }}"
        row[5].text = "{{ measurement.phase_name }}"
        doc.add_paragraph("{% endfor %}")  # Close the first loop for measurements

        # Add power measures section with placeholders for each measurement
        doc.add_paragraph("Power Measures:")
        doc.add_paragraph("{% for measurement in measurements %}")

        power_table = doc.add_table(rows=1, cols=5)
        power_hdr_cells = power_table.rows[0].cells
        power_hdr_cells[0].text = "Power Measure ID"
        power_hdr_cells[1].text = "Type"
        power_hdr_cells[2].text = "Name"
        power_hdr_cells[3].text = "Voltage (V)"
        power_hdr_cells[4].text = "Current (A)"

        # Loop over power measures for each measurement
        doc.add_paragraph("{% for power_measure in measurement.power_measures %}")
        power_row = power_table.add_row().cells
        power_row[0].text = "{{ power_measure.power_measure_id }}"
        power_row[1].text = "{{ power_measure.power_measure_type }}"
        power_row[2].text = "{{ power_measure.power_measure_name }}"
        power_row[3].text = "{{ power_measure.power_measure_voltage }}"
        power_row[4].text = "{{ power_measure.power_measure_current }}"
        doc.add_paragraph("{% endfor %}")  # Close the second loop for power measures

        doc.add_paragraph("{% endfor %}")  # Close the outer loop for measurements

        # Save the template
        doc.save(self.template_path)
        print(f"Template successfully saved to: {self.template_path}")

    def generate_report(self, report_id: int, use_cpp: bool = False) -> Path:
        """
        Generates a test report from aggregated data and saves it as a Word document.

        Args:
            report_id (int): The ID of the test report to generate.
            use_cpp (bool): Whether to process XML with a C++ tool.

        Returns:
            Path: Path to the generated Word report.
        """
        # Step 1: Retrieve report data from DataManager
        
        rows = self.data_manager.get_test_report(report_id)

        if not rows:
            raise ValueError(f"No report found for ID {report_id}")

        # Step 2: Aggregate report data into a single dictionary
        aggregated_data = self.aggregate_report_data(rows)

        # Step 3: Generate XML (For future use)
        xml_path = self.create_xml_from_report(rows, f"{self.xml_schema_file}.xml",False)
        self.sanitize_xml_file(xml_path)

        # Step 4: Optionally process XML with C++
        if use_cpp:
            self.call_cpp_for_processing(xml_path)

        # Step 5: Ensure output directory exists
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Step 6: Generate the file name
        base_file_name = self.generate_file_name(aggregated_data)

        # Construct the full output file path
        output_file = self.output_path / f"{base_file_name}.docx"

        # Step 7: Load the template
        template = DocxTemplate(self.template_path)

        # Render the template with the aggregated data
        template.render(aggregated_data)

        # Step 8: Save the report, overwriting if it already exists
        if output_file.exists():
            print(f"Updating existing report: {output_file}")
        else:
            print(f"Creating new report: {output_file}")

        template.save(output_file)

        return output_file


if __name__ == "__main__":
    # Initialize DataManager
    data_manager = DataManager()

    # Initialize ReportGenerator with Pydantic
    report_generator = ReportGenerator(
        data_manager=data_manager, template_path=Path("Report_Template.docx")
    )

    # Generate a report
    report = data_manager.generate_mock_data(112, "ABB", "maxgreen2", "FHR")
    report_id = data_manager.insert_test_report(report)
    # print(f"Got report id: {report_id}")
    # print("-------------------report object----------------------")
    # print(f"Generated report: {report}")
    # print("-------------------report object----------------------")

    report_generator.generate_report(report_id, use_cpp=False)
