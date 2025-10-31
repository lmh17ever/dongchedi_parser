"""
Parsing parameters from Dongchedi vehicle configuration page
and translate it

Author: lmh17ever
version: 3.0
Data: 27.10.2025
"""

import json
import requests

from bs4 import BeautifulSoup

from constants import SPECIAL_REPLACEMENTS, RESPONSE_TIMEOUT
from parameters_values_translation import values_translation


def get_html_elements(url):
    """Make request, parse and look for needed elements"""
    page = requests.get(url, timeout=RESPONSE_TIMEOUT).text
    soup = BeautifulSoup(page, 'html.parser')
    names_elements = soup.find_all(attrs={'data-row-anchor': True})
    return names_elements

def get_and_translate_parameter_name(parameter_element, names_dict):
    """Get parameter element text and translate it"""
    parameter_label = parameter_element.find_next(
        'label', {'class': 'cell_label__ZtXlw cell_has-wiki__18Gae'})
    if parameter_label:
        parameter_name = parameter_label.get_text()
        print(parameter_name)
        if parameter_name in names_dict and names_dict[parameter_name][1]:
            validated_parameter_name = names_dict[parameter_name][0]
            return validated_parameter_name
    return False

def validate_value(value, empty_parameters_flag):
    """Replace or delete inappropriate symbols"""
    if '○' in value:
        return 'option'
    if value == '':
        if empty_parameters_flag == 1:
            return '-'
        return False
    for find, replace in SPECIAL_REPLACEMENTS.items():
        validated_value = value.replace(find, replace)
    return validated_value

def get_validate_and_translate_value(parameter_element, empty_parameters_flag):
    """Get and check parameter value for something could be replaced and translate"""
    parameter_value = ''
    parameter_values_divs = parameter_element.find_all(
        'div', {'class': 'cell_normal__37nRi'})
    if not parameter_values_divs:
        return False
    for parameter_value_div in parameter_values_divs:
        parameter_value_text = parameter_value_div.get_text()
        validated_value = validate_value(parameter_value_text, empty_parameters_flag)
        if not validated_value:
            return False
        if validated_value == 'option':
            continue
        if validated_value in values_translation:
            parameter_value += values_translation[validated_value] + ', '
        else:
            parameter_value += parameter_value_text + ', '
    parameter_value = parameter_value.rstrip(', ')
    return parameter_value


def get_data(url):
    """Get url configuration page, parse parameters and translate it"""
    with open('config.json', 'r', encoding='utf-8'
              ) as config_json, open('test_names_translation.json', 'r', encoding='utf-8'
                                     ) as names_json:
        config = json.load(config_json)
        names_dict = json.load(names_json)
        result = ''
        all_names_parameters = get_html_elements(url)
        for parameter in all_names_parameters:
            parameter_name = get_and_translate_parameter_name(parameter, names_dict)
            if not parameter_name:
                continue
            parameter_value = get_validate_and_translate_value(
                parameter, config['with_empty_parameters'])
            if not parameter_value:
                continue
            print(parameter_value)
            result += f'{parameter_name}: {parameter_value}\n'
        return result
