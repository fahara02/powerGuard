import os
import subprocess
import xml.etree.ElementTree as ET
from docx import Document
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from pathlib import Path


class ReportGenerator:
    def __init__(self, data_manager):
        """
        Initialize the ReportGenerator with an instance of DataManager.
        """
        self.data_manager = data_manager

    def create_xml_from_report(self, report_data, xml_path="report_data.xml"):
        """
        Generate an XML file from the report data.
        Args:
            report_data (dict): A dictionary containing report data.
            xml_path (str): The path to save the generated XML file.
        """
        root = ET.Element("TestReport")

        for key, value in report_data.items():
            child = ET.SubElement(root, key)
            child.text = str(value)

        tree = ET.ElementTree(root)
        tree.write(xml_path)
        print(f"XML generated and saved to {xml_path}")
        return xml_path

    def edit_word_document(self, template_path, output_path, xml_path):
        """
        Edit a Word document with content controls based on the XML data.
        Args:
            template_path (str): Path to the Word template with content controls.
            output_path (str): Path to save the generated Word document.
            xml_path (str): Path to the XML file containing report data.
        """
        # Load the Word template
        doc = Document(template_path)

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

    def call_cpp_for_processing(self, xml_path, cpp_executable="process_report"):
        """
        Call a C++ executable to process the XML data.
        Args:
            xml_path (str): Path to the XML file.
            cpp_executable (str): Path to the C++ executable.
        """
        if not Path(cpp_executable).exists():
            raise FileNotFoundError(f"C++ executable '{cpp_executable}' not found.")

        # Call the C++ executable with the XML file as an argument
        subprocess.run([cpp_executable, xml_path], check=True)
        print("C++ processing completed.")

    def generate_report(self, report_id, template_path, output_path, use_cpp=False):
        """
        Generate a formatted report using a template and optionally call a C++ executable.
        Args:
            report_id (int): ID of the report to generate.
            template_path (str): Path to the Word template with content controls.
            output_path (str): Path to save the generated Word document.
            use_cpp (bool): Whether to call a C++ executable for processing.
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

        # Step 4: Edit the Word template
        self.edit_word_document(template_path, output_path, xml_path)
