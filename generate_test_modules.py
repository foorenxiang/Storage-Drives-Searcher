from pathlib import Path
from from_root import from_root
from icecream import ic
from typing import Union, List

SOURCE_PACKAGES = ["src"]


def generate_source_package_paths() -> List[Path]:
    source_package_paths = [Path(folder) for folder in SOURCE_PACKAGES]
    return source_package_paths


def generate_source_module_paths(source_package_paths: Path) -> List[Path]:
    source_module_paths: List[Path] = list()
    [
        source_module_paths.extend(source_package_path.glob("*/*.py"))
        for source_package_path in source_package_paths
    ]
    return source_module_paths


def generate_test_module_paths(source_module_paths: List[Path]) -> List[Path]:
    test_module_paths = []
    for path in source_module_paths:
        if path.name == "__init__.py":
            test_module_paths.append(
                Path("tests")
                / path.parent.relative_to(tuple(path.parents)[-1])
                / f"test_{path.parent.name}.py"
            )
            continue
        test_module_paths.append(
            Path("tests")
            / path.parent.relative_to(tuple(path.parents)[-1])
            / f"test_{path.name}"
        )
    return test_module_paths


def create_test_subdirectories(test_module_paths):
    for path in test_module_paths:
        from_root(path.parent, mkdirs=True)


def generate_test_modules(source_module_paths, test_module_paths: List[Path]):
    for source_path, test_module_path in zip(source_module_paths, test_module_paths):
        with open(source_path, "r") as fp:
            file_contents = fp.readlines()

        detected_functions_declarations = [
            line.split("def ")[1].split(":")[0]
            for line in file_contents
            if line.startswith("def ")
        ]
        detected_class_declarations = [
            line.split("class ")[1].split("(")[0].split(":")[0]
            if "(" in line
            else line.split("class ")[1].split(":")[0]
            for line in file_contents
            if line.startswith("class ")
        ]

        with open(test_module_path, "w") as fp:
            fp.writelines(f"# LINK {source_path}:1\n" f"\n")
            if not any((detected_functions_declarations, detected_class_declarations)):
                fp.writelines(
                    f"def {test_module_path.stem}():\n"
                    f"    raise NotImplementedError\n"
                    f"\n"
                )
            for function_declaration in detected_functions_declarations:
                function_name = function_declaration.split("(")[0]
                fp.writelines(
                    f"def test_{function_name}():\n"
                    f"    raise NotImplementedError\n"
                    f"    {function_declaration}\n"
                    f"\n"
                )

            for class_declaration in detected_class_declarations:
                fp.writelines(
                    f"def test_{class_declaration}():\n"
                    f"    raise NotImplementedError\n"
                    f"    object_to_test = {class_declaration}()\n"
                    f"\n"
                )


if __name__ == "__main__":
    source_package_paths = generate_source_package_paths()
    source_module_paths = generate_source_module_paths(source_package_paths)
    test_module_paths = generate_test_module_paths(source_module_paths)
    create_test_subdirectories(test_module_paths)
    generate_test_modules(source_module_paths, test_module_paths)
