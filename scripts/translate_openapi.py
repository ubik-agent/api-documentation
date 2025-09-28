import json
import sys
import os
import copy

def process_openapi_spec(base_spec_path, output_dir, languages):
    """
    Processes a base OpenAPI spec to generate language-specific versions.

    Args:
        base_spec_path (str): Path to the base OpenAPI JSON file with x-translations.
        output_dir (str): Directory to save the processed OpenAPI files.
        languages (list): A list of language codes to generate specs for (e.g., ['en', 'fr']).
    """
    try:
        with open(base_spec_path, 'r', encoding='utf-8') as f:
            base_spec = json.load(f)

        for lang in languages:
            spec_copy = copy.deepcopy(base_spec)
            
            # Translate paths
            if 'paths' in spec_copy:
                for path, methods in spec_copy['paths'].items():
                    for method, operation in methods.items():
                        # Translate summary and description if translations exist
                        if lang != 'en' and 'x-translations' in operation and lang in operation['x-translations']:
                            translations = operation['x-translations'][lang]
                            operation['summary'] = translations.get('summary', operation.get('summary'))
                            operation['description'] = translations.get('description', operation.get('description'))
                        
                        # Clean up x-translations from the final output
                        if 'x-translations' in operation:
                            del operation['x-translations']

            # Translate component schema descriptions
            if 'components' in spec_copy and 'schemas' in spec_copy['components']:
                for schema_name, schema_def in spec_copy['components']['schemas'].items():
                    if 'properties' in schema_def:
                        for prop_name, prop_def in schema_def['properties'].items():
                            if lang != 'en' and 'json_schema_extra' in prop_def and 'x-translations' in prop_def['json_schema_extra'] and lang in prop_def['json_schema_extra']['x-translations']:
                                translations = prop_def['json_schema_extra']['x-translations'][lang]
                                if 'description' in translations:
                                    prop_def['description'] = translations['description']
                            
                            # Clean up our custom field from the final output
                            if 'json_schema_extra' in prop_def:
                                del prop_def['json_schema_extra']

            # Define output path
            output_filename = f"openapi.{lang}.json"
            output_path = os.path.join(output_dir, output_filename)

            # Create output directory if it doesn't exist
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(spec_copy, f, ensure_ascii=False, indent=2)
                
            print(f"Successfully generated {lang} spec saved to {output_path}")

    except FileNotFoundError as e:
        print(f"Error: {e}. The base spec file was not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python translate_openapi.py <base_spec_path> <output_dir> <lang1> <lang2> ...", file=sys.stderr)
        sys.exit(1)
    
    base_spec_path = sys.argv[1]
    output_dir = sys.argv[2]
    languages = sys.argv[3:]
    
    process_openapi_spec(base_spec_path, output_dir, languages)
