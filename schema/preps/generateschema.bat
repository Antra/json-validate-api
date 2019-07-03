@echo off
openapi2jsonschema file:swagger.json -o temp --prefix=""
move temp\_definitions.json schema.json
rmdir temp /Q/S