#!/usr/bin/env python3

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# copyright: 2013 to the present, california institute of technology.
# all rights reserved. united states government sponsorship acknowledged.
# any commercial use must be negotiated with the office of technology transfer
# at the california institute of technology.
# 
# this software may be subject to u.s. export control laws. by accepting this
# software, the user agrees to comply with all applicable u.s. export laws and
# regulations. user has the responsibility to obtain export licenses,  or other
# export authority as may be required before exporting such information to
# foreign countries or providing access to foreign persons.
# 
# installation and use of this software is restricted by a license agreement
# between the licensee and the california institute of technology. it is the
# user's responsibility to abide by the terms of the license agreement.
#
# Author: Piyush Agram
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from collections import OrderedDict
import xml.etree.ElementTree as ET

class Component(OrderedDict):
    '''
    Class for storing component information.
    '''
    def __init__(self, name=None,data=None):

        if name in [None, '']:
            raise Exception('Component must have a name')

        self.name = name

        if data is None:
            self.data = OrderedDict()
        elif isinstance(data, OrderedDict):
            self.data = data
        elif isinstance(data, dict):
            self.data = OrderedDict()
            for key, val in data.items():
                self.data[key] = val
        else:
            raise Exception('Component data in __init__ should be a dict or ordereddict')
            

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self,key,value):
        if not isinstance(key, str):
            raise Exception('Component key must be a string')

        self.data[key] = value

    def toXML(self):
        '''
        Creates an XML element from the component.
        '''
        root = ET.Element('component')
        root.attrib['name'] = self.name

        for key, val in self.data.items():
            if isinstance(val, Catalog):
                compSubEl = ET.SubElement(root, 'component')
                compSubEl.attrib['name'] = key
                ET.SubElement(compSubEl, 'catalog').text = str(val.xmlname)

            elif isinstance(val, Component):
                if key != val.name:
                    print('WARNING: dictionary name and Component name dont match')
                    print('Proceeding with Component name')
                root.append(val.toXML())

            elif (isinstance(val,dict) or isinstance(val, OrderedDict)):
                obj = Component(name=key, data=val)
                root.append(obj.toXML())

            elif (not isinstance(val, dict)) and (not isinstance(val, OrderedDict)):
                propSubEl = ET.SubElement(root,'property')
                propSubEl.attrib['name'] = key
                ET.SubElement(propSubEl, 'value').text = str(val)

        return root

    def writeXML(self, filename, root='dummy', noroot=False):
        '''
        Write the component information to an XML file.
        '''
        if root in [None, '']:
            raise Exception('Root name cannot be blank')

        if noroot:
            fileRoot = self.toXML()
        else:
            fileRoot = ET.Element(root)

            ####Convert component to XML
            root = self.toXML()
            fileRoot.append(root)

        print(fileRoot)

        indentXML(fileRoot)

        ####Write file
        etObj = ET.ElementTree(fileRoot)
        etObj.write(filename, encoding='unicode') 

class Catalog(object):
    '''
    Class for storing catalog key.
    '''
    def __init__(self, name):
        self.xmlname = name

def indentXML(elem, depth = None,last = None):
    if depth == None:
        depth = [0]
    if last == None:
        last = False
    tab =u' '*4
    if(len(elem)):
        depth[0] += 1
        elem.text = u'\n' + (depth[0])*tab
        lenEl = len(elem)
        lastCp = False
        for i in range(lenEl):
            if(i == lenEl - 1):
                lastCp = True
            indentXML(elem[i],depth,lastCp)
        if(not last):
            elem.tail = u'\n' + (depth[0])*tab
        else:
            depth[0] -= 1
            elem.tail = u'\n' + (depth[0])*tab
    else:
        if(not last):
            elem.tail = u'\n' + (depth[0])*tab
        else:
            depth[0] -= 1
            elem.tail = u'\n' + (depth[0])*tab
