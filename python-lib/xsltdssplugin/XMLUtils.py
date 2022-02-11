# -*- coding: utf-8 -*-
"""Main module : XML file wrapping, XSLT transformation & schema validation"""

from datetime import datetime
import os
import sys

import cchardet
import lxml.etree as ET
from lxml.etree import XMLParser

class FormatException(ValueError):
    """Custom exception raised when the XSLT stylesheet, Schema and/or XML format is invalid"""
    pass

class XML:
    """Wrapper class for XML file"""
    def __init__(self, source, role=None):
        self.source_path = source
        self.source_filename = os.path.basename(self.source_path)
        self.parser = XMLParser(huge_tree=True)
        try:
            self.source_parse = ET.parse(self.source_path, parser=self.parser)
        except ET.XMLSyntaxError:
            if role == "XSLT":
                raise FormatException(
                "Error XSLT version : check version XSLT 1.0"
                )
            elif role == "Schema":
                raise FormatException(
                "Error Schema validation : check Schema file (DTD or RelaxNG only)"
                )
            else:
                raise FormatException(
                f"Failed to parse source document : {self.source_filename} | Error log : {sys.exc_info()[1]}"
                )
                
class Schema(XML):
    """Wrapper class for validation schema file (RelaxNG, DTD)"""
    def __init__(self, src_schema, role="Schema"):
        super().__init__(src_schema, role)
        self.schema_parsed = self.source_parse
        self.schema_path = self.source_path
        _, self.extension = os.path.splitext(self.schema_path)
        if self.extension.lower() == ".rng":
            self.schema_in = ET.RelaxNG(self.schema_parsed)
        elif self.extension.lower() == ".dtd":
            self.schema_in = ET.DTD(self.schema_parsed)
        else:
            print("[SCHEMA ERROR] Check if the schema is RelaxNG or DTD")
                
class XSLTTransformation(XML):
    """Class performs XSLT transformation"""
    def __init__(self, source, xslt_stylesheet, output_path, init_params, role=None):
        super().__init__(source, role)
        self.source_dom_parsed = self.source_parse
        self.source_filename = self.source_filename 
        self.transform = ET.XSLT(xslt_stylesheet)
        self.init_params = init_params
        self.static_params = {k:ET.XSLT.strparam(v) for k,v in self.init_params['custom_param'].items()}
        self.params = {**self.static_params, **self._get_dynamic_params()}
        self.output_path = output_path
        try :
            self.prefix = init_params['prefix'] 
        except KeyError: 
            self.prefix = "new_"
        
    def _get_dynamic_params(self) -> dict:
        """Returns dictionary with date and filename to embed in new XML, if this params is selected"""
        dynamics = {}
        if self.init_params['date_param']:
            now = datetime.now()
            dynamics['datenow'] = ET.XSLT.strparam(now.strftime("%d/%m/%Y %H:%M:%S"))
        if self.init_params['filename_param']:
            dynamics['filename'] = ET.XSLT.strparam(self.source_filename)
        return dynamics 
    
    def _apply_XSLT_transformation(self) -> None:
        """Apply XSLT transformation and write a new XML file in output folder"""
        try:
            new_dom = self.transform(self.source_dom_parsed, **self.params)
            new_dom.write(f'{self.output_path}/{self.prefix}{self.source_filename}', pretty_print=True, xml_declaration = True, encoding="utf-8")
            print(f"[XSLT INFO] : XSLT transformation with {self.source_filename} done")
        except:
            print(f"[XSLT ERROR] : XSLT transformation failed with {self.source_filename}")
            
class SchemaValidation(XML):
    """Class performs schema validation"""
    def __init__(self, source, schema_in, role=None):
        super().__init__(source, role)
        self.source_dom_parsed = self.source_parse
        self.source_filename = self.source_filename 
        self.schema_in = schema_in
        
    def _validator(self) -> None:
        """Apply validation of new XML against a predifined schema and return a success or a fail message in log activity"""
        if self.schema_in(self.source_dom_parsed):
            print(f"✅ Document {self.source_filename} is valid")
        else:
            print(f"❌ Document {self.source_filename} is invalid")
            try:
                self.schema_in.assertValid(self.source_dom_parsed)
            except ET.DocumentInvalid:
                print(f'Error log : {sys.exc_info()[1]}')
                