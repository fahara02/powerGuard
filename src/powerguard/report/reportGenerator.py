import os
import sqlite3
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Optional
from zipfile import ZipFile

from docx import Document
from lxml import etree
from pydantic import BaseModel, Field, field_validator

from powerguard.bootstrap import paths
from powerguard.data.data_manager import DataManager


class ReportGenerator(BaseModel):
    """
    ReportGenerator class for generating formatted Word reports using Pydantic.
    """
    data_manager: DataManager
    template_path: Path = Field(default="test_report_template.docx")
    output_path:Path =Field(default= paths.get("output_dir")   )

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
            value = template_folder / "test_report_template.docx"

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
        full_output_folder= output_folder 

        # Validate if the template file exists and is a file
        if not full_output_folder.exists() or not full_output_folder.is_dir():
            raise ValueError(f"Output Folder not found: {full_output_folder}")

        return full_output_folder



    # def create_xml_from_report(self, report_data: dict, xml_path: Path = Path("report_data.xml")) -> Path:
    #     """
    #     Generate an XML file from the report data, flattening nested dictionaries.
    #     """
    #     def flatten_dict(data, parent_key='', sep='_'):
    #         """
    #         Recursively flatten a nested dictionary.
    #         """
    #         items = []
    #         for k, v in data.items():
    #             new_key = f"{parent_key}{sep}{k}" if parent_key else k
    #             if isinstance(v, dict):
    #                 items.extend(flatten_dict(v, new_key, sep=sep).items())
    #             else:
    #                 items.append((new_key, v))
    #         return dict(items)

    #     # Flatten the report data, including nested dictionaries like `settings`
    #     flattened_data = flatten_dict(report_data)

    #     # Create XML structure
    #     root = ET.Element("TestReport")
    #     for key, value in flattened_data.items():
    #         child = ET.SubElement(root, key)
    #         child.text = str(value)

    #     # Write XML to file
    #     tree = ET.ElementTree(root)
    #     tree.write(xml_path)
    #     print(f"XML generated and saved to {xml_path}")
    #     return xml_path
    # def create_xml_from_report(self, report_data: dict, xml_path: Path = Path("report_data.xml")) -> Path:
    #     """
    #     Generate an XML file from the report data, flattening nested dictionaries.
    #     """
    #     def flatten_dict(data, parent_key='', sep='_'):
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
    #                         items.extend(flatten_dict(item, indexed_key, sep=sep).items())
    #                     else:
    #                         items.append((indexed_key, item))
    #             else:
    #                 # Add simple key-value pairs
    #                 items.append((new_key, v))
    #         return dict(items)

    #     # Flatten the report data, including nested dictionaries and lists
    #     flattened_data = flatten_dict(report_data)

    #     # Create XML structure
    #     root = ET.Element("TestReport")
    #     for key, value in flattened_data.items():
    #         child = ET.SubElement(root, key)
    #         # Convert non-string values to strings
    #         child.text = str(value) if value is not None else ""

    #     # Write XML to file
    #     tree = ET.ElementTree(root)
    #     tree.write(xml_path, encoding="utf-8", xml_declaration=True)
    #     print(f"XML generated and saved to {xml_path}")
    #     return xml_path
    def create_xml_from_report(self, report_data: dict, file_name: str) -> Path:
        """
        Generate an XML file from the report data, flattening nested dictionaries.

        Args:
            report_data (dict): The data to be converted to XML.
            file_name (str): The name of the output XML file.

        Returns:
            Path: The path to the saved XML file.
        """
        def flatten_dict(data, parent_key='', sep='_'):
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
                            items.extend(flatten_dict(item, indexed_key, sep=sep).items())
                        else:
                            items.append((indexed_key, item))
                else:
                    # Add simple key-value pairs
                    items.append((new_key, v))
            return dict(items)

        # Flatten the report data, including nested dictionaries and lists
        flattened_data = flatten_dict(report_data)

        # Create XML structure
        root = ET.Element("TestReport")
        for key, value in flattened_data.items():
            child = ET.SubElement(root, key)
            # Convert non-string values to strings
            child.text = str(value) if value is not None else ""

        # Construct full XML file path in the output directory
        xml_path = self.output_path / file_name

        # Write XML to file
        tree = ET.ElementTree(root)
        tree.write(xml_path, encoding="utf-8", xml_declaration=True)
        print(f"XML generated and saved to {xml_path}")
        return xml_path

    def edit_word_document(self, output_path: Path, xml_path: Path):
        """
        Edit a Word document with content controls based on the XML data.
        """
        # Parse the XML to get data
        tree = ET.parse(xml_path)
        root = tree.getroot()
        data_map = {child.tag: child.text for child in root}  # Create a dictionary of XML data

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
                tag = tag_element.attrib.get(f"{{{namespace['w']}}}val")  # Get the tag value
                if tag in data_map:  # If there's data for this tag
                    content = control.find(".//w:sdtContent", namespaces=namespace)
                    if content is not None:
                        # Replace text inside the content control
                        for text in content.xpath(".//w:t", namespaces=namespace):
                            text.text = data_map[tag]

        # Write the updated XML back to the Word document
        with ZipFile(self.template_path, "r") as docx:
            with ZipFile(output_path, "w") as new_docx:
                for file in docx.filelist:
                    if file.filename != "word/document.xml":
                        new_docx.writestr(file.filename, docx.read(file.filename))
                new_docx.writestr("word/document.xml", etree.tostring(doc_tree, pretty_print=True))

        print(f"Word document updated and saved to {output_path}")

    def call_cpp_for_processing(self, xml_path: Path, cpp_executable: Path = Path("process_report")):
        """
        Call a C++ executable to process the XML data.
        """
        if not cpp_executable.exists():
            raise FileNotFoundError(f"C++ executable '{cpp_executable}' not found.")

        # Call the C++ executable with the XML file as an argument
        subprocess.run([str(cpp_executable), str(xml_path)], check=True)
        print("C++ processing completed.")

    def generate_file_name(self, report_data: dict) -> str:
        """
        Generate a file name based on client name, UPS model, date, and report ID.

        Args:
            report_data (dict): The full report data containing `client_name`, `ups_model`, and `report_id`.

        Returns:
            str: The generated file name.
        """
        client_name = report_data.get("settings", {}).get("client_name", "UnknownClient")
        ups_model = report_data.get("settings", {}).get("ups_model", "UnknownModel")
        report_id = report_data.get("report_id", "0")
        date_str = datetime.now().strftime("%Y%m%d")

        # Create a sanitized file name
        file_name = f"{client_name}_{ups_model}_{report_id}_{date_str}"
        return file_name.replace(" ", "_")

    def generate_all_reports(self, output_dir: Path = Path("reports")):
        """
        Generate XML reports for all test reports in the database.

        Args:
            output_dir (Path): The directory where the reports will be saved.
        """
        try:
            # Ensure the output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)

            # Retrieve all TestReport IDs and their test names
            reports = self.get_all_report_id_testName()

            # Generate XML reports for each entry
            for report in reports:
                report_id = report["report_id"]

                # Fetch the full report data for this report_id
                report_data = self.get_test_report(report_id)
                if not report_data:
                    print(f"Skipping report_id {report_id}: No data found.")
                    continue

                # Generate the file name
                file_name = self.generate_file_name(report_data)

                # Generate the XML report
                xml_file_path = output_dir / file_name
                self.create_xml_from_report(report_data, xml_file_path)
                print(f"Report generated: {xml_file_path}")
        except sqlite3.Error as e:
            raise Exception(f"Error generating reports: {e}")
    def generate_report(self, report_id: int, use_cpp: bool = False):
        """
        Generate a formatted report using a template and optionally call a C++ executable.
        """
        # Step 1: Retrieve report data from DataManager
        report_data = self.data_manager.get_test_report(report_id)

        if not report_data:
            raise ValueError(f"No report found for ID {report_id}")

        # Step 2: Generate file name
        file_name = self.generate_file_name(report_data)

        # Step 3: Generate XML
        xml_path = self.create_xml_from_report(report_data, f"{file_name}.xml")

        # Step 4: Optionally process XML with C++
        if use_cpp:
            self.call_cpp_for_processing(xml_path)

        # Step 5: Generate the output Word file path
        output_file_path = self.output_path / f"{file_name}.docx"

        # Step 6: Edit the Word template
        self.edit_word_document(output_file_path, xml_path)



if __name__ == "__main__":
    # Initialize DataManager
    data_manager = DataManager()
    report=data_manager.insert_mock_data("Walton","maxgreen2","FHR")
    # Initialize ReportGenerator with Pydantic
    report_generator = ReportGenerator(
        data_manager=data_manager,
        template_path=Path("test_report_template.docx")
    )

    # Generate a report
    report_id = report.settings.report_id
    report_generator.generate_report(report_id, use_cpp=False)

