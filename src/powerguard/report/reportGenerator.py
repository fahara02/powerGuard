from typing import Optional
from pydantic import BaseModel, Field, field_validator
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET
import subprocess
from docx import Document
from data.data_manager import DataManager  # Replace with actual DataManager implementation


class ReportGenerator(BaseModel):
    """
    ReportGenerator class for generating formatted Word reports using Pydantic.
    """
    data_manager: DataManager
    template_path: Path

    @field_validator("template_path")
    def validate_template_path(cls, value: Path) -> Path:
        """
        Ensure the template path exists and is a file.
        """
        if not value.exists() or not value.is_file():
            raise ValueError(f"Template file not found: {value}")
        return value

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
        client_name = report_data.get("clientName", "UnknownClient").replace(" ", "_")
        ups_model = report_data.get("upsModel", "UnknownModel").replace(" ", "_")
        date_str = datetime.now().strftime("%Y%m%d")
        output_file_name = f"{client_name}_{ups_model}_{report_id}_{date_str}.docx"
        output_path = Path.cwd() / output_file_name

        # Step 5: Edit the Word template
        self.edit_word_document(output_path, xml_path)


if __name__ == "__main__":
    # Initialize DataManager
    data_manager = DataManager()

    # Initialize ReportGenerator with Pydantic
    report_generator = ReportGenerator(
        data_manager=data_manager,
        template_path=Path("test_report_template.docx")
    )

    # Generate a report
    report_id = 42
    report_generator.generate_report(report_id, use_cpp=True)

