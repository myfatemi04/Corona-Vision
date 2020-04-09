def table_to_csv(table):
    output_rows = []
    for table_row in table.findAll('tr'):
        columns = table_row.findAll('td')
        output_row = []
        for column in columns:
            output_row.append(column.text)
        output_rows.append(output_row)

def get_elem(soup, selector_chain):
	elem = soup
	for selector in selector_chain:
		elem = elem.select(selector['selector'])
		if 'index' not in selector:
			return elem
		elem = elem[selector['index']]
	
	return elem

def get_field(soup, selector_chain):
	return get_elem(soup, selector_chain).text