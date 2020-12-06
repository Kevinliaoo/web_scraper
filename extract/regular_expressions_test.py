import re 


text = 'Destinations: Argentina exports mostly to Brazil ($11B), China ($4.34B), United States ($4.23B), Chile ($3.05B), and Vietnam ($2.08B), and imports mostly from Brazil ($15B), China ($10.8B), United States ($8.21B), Germany ($3.47B), and Paraguay ($1.73B).'

export_re = 'Destinations: .+? exports mostly to '
import_re = ', and imports mostly from '
export_statement = re.findall(r'{}'.format(export_re), text)[0]
import_statement = re.findall(r'{}'.format(import_re), text)[0]
export_start_index = text.find(export_statement)
import_start_index = text.find(import_statement)

export_goods = text[export_start_index+len(export_statement):import_start_index]
import_goods = text[import_start_index+len(import_statement):-1]

print(export_goods)
print(import_goods)