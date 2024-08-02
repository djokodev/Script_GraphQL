import re
import sys


def read_schema(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            cleaned_lines = [line.strip() for line in lines]
            return "\n".join(cleaned_lines)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        sys.exit(1)


def extract_names(schema_text):
    query_pattern = re.compile(r'type Query {[^}]*}')
    mutation_pattern = re.compile(r'type Mutation {[^}]*}')
    
    queries = query_pattern.findall(schema_text)
    mutations = mutation_pattern.findall(schema_text)
    
    query_names = re.findall(r'(\w+)\(', queries[0]) if queries else []
    mutation_names = re.findall(r'(\w+)\(', mutations[0]) if mutations else []
    
    return query_names, mutation_names


def extract_fields(type_name, schema_text):
    type_pattern = re.compile(f'type {type_name} {{(.*?)}}', re.DOTALL)
    field_pattern = re.compile(r'(\w+): (\w+[^!]*)[!]?')
    
    type_body = type_pattern.search(schema_text)
    if not type_body:
        return {}

    fields = {}
    for field_match in field_pattern.finditer(type_body.group(1)):
        field_name = field_match.group(1)
        field_type = field_match.group(2)
        fields[field_name] = field_type
    
    return fields


def generate_query(type_name):
    fields = extract_fields('HomeNode', schema)
    home_item_list_fields = extract_fields('HomeItemNodeConnection', schema)
    
    query = f"query Get{type_name}($id: ID!) {{\n  home(id: $id) {{\n"
    for field in fields:
        query += f"    {field}\n"
    
    query += "    homeItemList {\n"
    query += "      pageInfo {\n        hasNextPage\n        hasPreviousPage\n      }\n"
    query += "      edges {\n        node {\n"
    for field in home_item_list_fields:
        query += f"          {field}\n"
    query += "        }\n      }\n    }\n"
    
    query += "  }\n}"
    query = f"'''\n{query}\n'''"
    return query


def generate_mutation(type_name):
    input_type = f'{type_name}Input'
    payload_type = 'CreateSlideshowItemPayload'
    fields = extract_fields(payload_type, schema)
    
    mutation = f"mutation {type_name}($input: {input_type}!) {{\n  createSlideshowItem(input: $input) {{\n"
    mutation += "    slideshowItem {\n"
    for field in fields:
        mutation += f"      {field}\n"
    mutation += "    }\n"
    mutation += "    message\n"
    mutation += "    clientMutationId\n"
    mutation += "  }\n}"
    mutation = f"'''\n{mutation}\n'''"
    return mutation

schema = read_schema('schema.graphql')

query_names, mutation_names = extract_names(schema)

queries_and_mutations = {}
for query_name in query_names:
    queries_and_mutations[f'{query_name.upper()}'] = generate_query(query_name)

for mutation_name in mutation_names:
    queries_and_mutations[f'{mutation_name.upper()}'] = generate_mutation(mutation_name)

with open('queries.py', 'w', encoding='utf-8') as file:
    for name, value in queries_and_mutations.items():
        if name in [q.upper() for q in query_names]:
            file.write(f"{name} = {value}\n\n")

with open('mutations.py', 'w', encoding='utf-8') as file:
    for name, value in queries_and_mutations.items():
        if name in [m.upper() for m in mutation_names]:
            file.write(f"{name} = {value}\n\n")
