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

    # def create_xml_from_report(
    #     self, report_data: list[dict], file_name: str, flatten: bool = True
    # ) -> Path:
    #     """
    #     Generate an XML file from the report data, flattening nested dictionaries.

    #     Args:
    #         report_data (list[dict]): A list of rows fetched from the database.
    #         file_name (str): The name of the output XML file.

    #     Returns:
    #         Path: The path to the saved XML file.
    #     """

    #     def flatten_dict(data, parent_key="", sep="_"):
    #         """
    #         Recursively flatten a nested dictionary.
    #         """
    #         items = []
    #         for k, v in data.items():
    #             new_key = f"{parent_key}{sep}{k}" if parent_key else k
    #             if isinstance(v, dict):
    #                 # Recursively flatten dictionaries
    #                 items.extend(flatten_dict(v, new_key, sep=sep).items())
    #             elif isinstance(v, list):
    #                 # Handle lists by indexing items
    #                 for i, item in enumerate(v):
    #                     indexed_key = f"{new_key}{sep}{i}"
    #                     if isinstance(item, dict):
    #                         items.extend(
    #                             flatten_dict(item, indexed_key, sep=sep).items()
    #                         )
    #                     else:
    #                         items.append((indexed_key, item))
    #             else:
    #                 # Add simple key-value pairs
    #                 items.append((new_key, v))
    #         return dict(items)

    #     # Step 1: Aggregate report data into a single dictionary

    #     aggregated_data = self.aggregate_report_data(report_data)
    #     pprint.pprint(f"context data dictionary is { aggregated_data }")

    #     # Step 2: Flatten the report data, including nested dictionaries and lists
    #     flattened_data = flatten_dict(aggregated_data)
    #     if flatten:
    #         xml_data = flattened_data
    #     else:
    #         xml_data = aggregated_data
    #     # Step 3: Create XML structure
    #     root = ET.Element("TestReport")
    #     for key, value in xml_data.items():
    #         child = ET.SubElement(root, key)
    #         # Convert non-string values to strings
    #         child.text = str(value) if value is not None else ""

    #     # Step 4: Construct full XML file path in the output directory
    #     xml_path = self.output_path / file_name
    #     # Ensure the parent directory exists
    #     xml_path.parent.mkdir(parents=True, exist_ok=True)

    #     # Step 5: Check if the file exists and confirm overwrite
    #     if xml_path.exists():
    #         print(f"XML file already exists at {xml_path}. Overwriting.")

    #     # Write XML to file
    #     tree = ET.ElementTree(root)
    #     tree.write(xml_path, encoding="utf-8", xml_declaration=True)
    #     print(f"XML generated and saved to {xml_path}")
    #     return xml_path
    def create_xml_from_report(
        self, report_data: list[dict], file_name: str, flatten: bool = True
    ) -> Path:
        """
        Generate an XML file from the report data, with optional flattening.

        Args:
            report_data (list[dict]): A list of rows fetched from the database.
            file_name (str): The name of the output XML file.
            flatten (bool): Whether to flatten nested dictionaries (default: True).

        Returns:
            Path: The path to the saved XML file.
        """

        def flatten_dict(data, parent_key="", sep="_"):
            """Recursively flatten a nested dictionary."""
            items = []
            for k, v in data.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                elif isinstance(v, list):
                    for i, item in enumerate(v):
                        indexed_key = f"{new_key}{sep}{i}"
                        if isinstance(item, dict):
                            items.extend(
                                flatten_dict(item, indexed_key, sep=sep).items()
                            )
                        else:
                            items.append((indexed_key, item))
                else:
                    items.append((new_key, v))
            return dict(items)

        def create_nested_xml(element, data):
            """Recursively create XML elements for nested structures."""
            if isinstance(data, dict):
                for key, value in data.items():
                    child = ET.SubElement(element, key)
                    create_nested_xml(child, value)
            elif isinstance(data, list):
                for item in data:
                    item_element = ET.SubElement(element, "Item")
                    create_nested_xml(item_element, item)
            else:
                element.text = str(data) if data is not None else ""

        # Step 1: Aggregate report data into a single dictionary
        aggregated_data = self.aggregate_report_data(report_data)
        pprint.pprint(f"context data dictionary is {aggregated_data}")

        # Step 2: Flatten or preserve nested structure based on the flag
        xml_data = flatten_dict(aggregated_data) if flatten else aggregated_data

        # Step 3: Create XML structure
        root = ET.Element("TestReport")
        if flatten:
            for key, value in xml_data.items():
                child = ET.SubElement(root, key)
                child.text = str(value) if value is not None else ""
        else:
            create_nested_xml(root, xml_data)

        # Step 4: Construct full XML file path in the output directory
        xml_path = self.output_path / file_name
        xml_path.parent.mkdir(parents=True, exist_ok=True)

        # Step 5: Check if the file exists and confirm overwrite
        if xml_path.exists():
            print(f"XML file already exists at {xml_path}. Overwriting.")

        # Write XML to file
        tree = ET.ElementTree(root)
        tree.write(xml_path, encoding="utf-8", xml_declaration=True)
        print(f"XML generated and saved to {xml_path}")
        return xml_path

    def generate_report(
        self, report_id: int, use_cpp: bool = False, use_xml: bool = False, use_flatten:bool=True
    ) -> Path:
        """
        Generates a test report from aggregated data and saves it as a Word document.

        Args:
            report_id (int): The ID of the test report to generate.
            use_cpp (bool): Whether to process XML with a C++ tool.

        Returns:
            Path: Path to the generated Word report.
        """

        rows = self.data_manager.get_test_report(report_id)

        if not rows:
            raise ValueError(f"No report found for ID {report_id}")

        aggregated_data = self.aggregate_report_data(rows)

        xml_path = self.create_xml_from_report(
            rows, f"{self.xml_schema_file}.xml", use_flatten
        )
        self.sanitize_xml_file(xml_path)

        if use_cpp and use_xml:
            self.call_cpp_for_processing(xml_path)

        self.output_path.mkdir(parents=True, exist_ok=True)

        base_file_name = self.generate_file_name(aggregated_data)

        output_file_path = self.output_path / f"{base_file_name}.docx"

        if use_xml:
            self.edit_word_document(output_file_path, xml_path)
        else:
            template = DocxTemplate(self.template_path)
            template.render(aggregated_data)
            if output_file_path.exists():
                print(f"Updating existing report: {output_file_path}")
            else:
                print(f"Creating new report: {output_file_path}")

            template.save(output_file_path)
        return output_file_path

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

    def edit_word_document(self, output_path: Path, xml_path: Path):
        """
        Edit a Word document with content controls based on the XML data.
        """
        # Parse the XML to get data
        tree = ET.parse(xml_path)
        root = tree.getroot()
        data_map = {
            child.tag: child.text for child in root
        }  # Create a dictionary of XML data

        # Open the Word document as a zip file
        with ZipFile(self.template_path, "r") as docx:
            # Extract the XML for the main document
            document_xml = docx.read("word/document.xml")

        # Parse the XML
        doc_tree = etree.fromstring(document_xml)

        # Replace content controls (w:sdt and w:sdtContent) with corresponding data
        namespace = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        }
        content_controls = doc_tree.xpath("//w:sdt", namespaces=namespace)

        for control in content_controls:
            tag_element = control.find(".//w:tag", namespaces=namespace)
            if tag_element is not None:
                tag = tag_element.attrib.get(
                    f"{{{namespace['w']}}}val"
                )  # Get the tag value
                if tag in data_map:  # If there's data for this tag
                    content = control.find(".//w:sdtContent", namespaces=namespace)
                    if content is not None:
                        # Replace text inside the content control
                        for text in content.xpath(".//w:t", namespaces=namespace):
                            text.text = data_map[tag]

        # Overwrite the existing file if it exists
        if output_path.exists():
            print(f"Word document already exists at {output_path}. Overwriting.")
        # Write the updated XML back to the Word document
        with ZipFile(self.template_path, "r") as docx:
            with ZipFile(output_path, "w") as new_docx:
                for file in docx.filelist:
                    if file.filename != "word/document.xml":
                        new_docx.writestr(file.filename, docx.read(file.filename))
                new_docx.writestr(
                    "word/document.xml", etree.tostring(doc_tree, pretty_print=True)
                )

        print(f"Word document updated and saved to {output_path}")


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

    report_generator.generate_report(report_id, use_cpp=False, use_xml=False,use_flatten=False)
