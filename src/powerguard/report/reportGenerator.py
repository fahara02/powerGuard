import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Optional

from docx import Document
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



    def create_xml_from_report(self, report_data: dict, xml_path: Path = Path("report_data.xml")) -> Path:
        """
        Generate an XML file from the report data.
        """
        root = ET.Element("TestReport")

        for key, value in report_data.items():
            child = ET.SubElement(root, key)
            child.text = str(value)

        tree = ET.ElementTree(root)
        tree.write(xml_path)
        print(f"XML generated and saved to {xml_path}")
        return xml_path

    def edit_word_document(self, output_path: Path, xml_path: Path):
        """
        Edit a Word document with content controls based on the XML data.
        """
        # Load the Word template
        doc = Document(self.template_path)

        # Parse the XML to get data
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Replace content control tags with XML data
        for paragraph in doc.paragraphs:
            for key in root:
                if f"{{{{{key.tag}}}}}" in paragraph.text:  # Match {{tag}}
                    paragraph.text = paragraph.text.replace(f"{{{{{key.tag}}}}}", key.text)

        # Save the updated Word document
        doc.save(output_path)
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

    def generate_report(self, report_id: int, use_cpp: bool = False):
        """
        Generate a formatted report using a template and optionally call a C++ executable.
        """
        # Step 1: Retrieve report data from DataManager
        report_data = self.data_manager.get_test_report(report_id)

        if not report_data:
            raise ValueError(f"No report found for ID {report_id}")

        # Step 2: Generate XML
        xml_path = self.create_xml_from_report(report_data)

        # Step 3: Optionally process XML with C++
        if use_cpp:
            self.call_cpp_for_processing(xml_path)

        # Step 4: Autogenerate output file name
        client_name = report.settings.client_name or "UnknownClient"
        ups_model = report.settings.ups_model or "UnknownModel"
        date_str = datetime.now().strftime("%Y%m%d")
        output_file_name = f"{client_name}_{ups_model}_{report_id}_{date_str}.docx"            
        output_file_path = self.output_path / output_file_name
        # Step 5: Edit the Word template
        self.edit_word_document(output_file_path, xml_path)


if __name__ == "__main__":
    # Initialize DataManager
    data_manager = DataManager()
    report=data_manager.insert_mock_data("Walton","maxgreen","FHR")
    # Initialize ReportGenerator with Pydantic
    report_generator = ReportGenerator(
        data_manager=data_manager,
        template_path=Path("test_report_template.docx")
    )

    # Generate a report
    report_id = report.settings.report_id
    report_generator.generate_report(report_id, use_cpp=False)

