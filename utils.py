import xml.etree.ElementTree as ET

tree = ET.parse('Data-SNCF/geographie_WPY.xml')
root = tree.getroot()

print(tree)
print(root.tag)
print(root.attrib)
for child in root:
    print(child.tag, child.attrib)
# print([elem.tag for elem in root.iter()])
print(tree.find("grillesHoraire").get("Ouverture"))