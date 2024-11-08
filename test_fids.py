import pefile, re, sys, requests

model_endpoint = 'http://localhost:5000/predict'

def get_features(file_path):
    # Extract header information
    PEfile = pefile.PE(file_path)
    feature_vector = [PEfile.OPTIONAL_HEADER.DATA_DIRECTORY[6].Size, PEfile.OPTIONAL_HEADER.DATA_DIRECTORY[6].VirtualAddress, PEfile.OPTIONAL_HEADER.MajorImageVersion, PEfile.OPTIONAL_HEADER.MajorOperatingSystemVersion, PEfile.OPTIONAL_HEADER.DATA_DIRECTORY[0].VirtualAddress,
                      PEfile.OPTIONAL_HEADER.DATA_DIRECTORY[0].Size, PEfile.OPTIONAL_HEADER.DATA_DIRECTORY[12].VirtualAddress, PEfile.OPTIONAL_HEADER.DATA_DIRECTORY[2].Size, PEfile.OPTIONAL_HEADER.MajorLinkerVersion, PEfile.FILE_HEADER.NumberOfSections, PEfile.OPTIONAL_HEADER.SizeOfStackReserve, PEfile.OPTIONAL_HEADER.DllCharacteristics]

    machine_type = PEfile.FILE_HEADER.Machine
    num_sections = len(PEfile.sections)
    entry_point = PEfile.OPTIONAL_HEADER.AddressOfEntryPoint
    feature_vector.extend([machine_type, num_sections,  entry_point])

    # Extract section information
    section_info = [section.SizeOfRawData for section in PEfile.sections]
    feature_vector += section_info

    # Extract ASCII and Unicode strings
    with open(file_path, 'rb') as f:
        data = f.read()
    ascii_strings = re.findall(b'[ -~]{4,}', data)
    unicode_strings = re.findall(b'[\x20-\x7E\x80-\xFE]{4,}', data)
    feature_vector.extend([len(ascii_strings), len(unicode_strings)])

    # Extract import information
    imports = {}
    for entry in PEfile.DIRECTORY_ENTRY_IMPORT:
        try:
            dll_name = entry.dll.decode('utf-8')
            imports[dll_name] = [func.name.decode(
                'utf-8') for func in entry.imports]
        except:
            dll_name = entry.dll
    feature_vector.extend(list(imports.keys()))

    return feature_vector


# data = get_features(sys.argv[1])

# features = [float(data[i]) for i in range(7)]

# prediction = requests.post(model_endpoint, json={'inputs': features}).json()[
#     'prediction']

# print(f"File {sys.argv[1]} is {prediction}")
