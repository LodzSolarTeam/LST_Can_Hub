##Pre-requirements:
- https://github.com/protocolbuffers/protobuf/releases (latest version linux-aarch_64)
- pip3 install mypy mypy-protobuf

Command to generate python classes with .pyi

```./protoc --python_out=. --mypy_out=. car_frame.proto```
