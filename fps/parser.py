import base64
import os
import random
import string
import xml.etree.ElementTree as ET


class FPSParser(object):
    def __init__(self, path):
        self.path = path
        self._root = None
        self._parse_result = None

    @property
    def root(self):
        if self._root is None:
            self._root = ET.ElementTree(file=self.path).getroot()
            if self._root.attrib["version"] != "1.0":
                raise ValueError("Unsupported version")
        return self._root

    def parse(self):
        problem = {"title": None, "description": None,
                   "memory_limit": {"unit": None, "value": None},
                   "time_limit": {"unit": None, "value": None},
                   "images": [], "input": None, "output": None, "samples": [],
                   "test_cases": [], "hint": None, "source": None,
                   "spj": None, "solution": None}
        sample_start = True
        test_case_start = True
        for node in self.root:
            if node.tag == "item":
                for item in node:
                    tag = item.tag
                    if tag in ["title", "description", "input", "output", "hint", "source"]:
                        problem[item.tag] = item.text
                    elif tag == "time_limit":
                        unit = item.attrib.get("unit", "s")
                        if unit not in ["s", "ms"]:
                            raise ValueError("Invalid time limit unit")
                        problem["time_limit"]["unit"] = item.attrib.get("unit", "s")
                        value = int(item.text)
                        if value <= 0:
                            raise ValueError("Invalid time limit value")
                        problem["time_limit"]["value"] = value
                    elif tag == "memory_limit":
                        unit = item.attrib.get("unit", "MB")
                        if unit not in ["MB", "KB", "mb", "kb"]:
                            raise ValueError("Invalid memory limit unit")
                        problem["memory_limit"]["unit"] = unit.upper()
                        value = int(item.text)
                        if value <= 0:
                            raise ValueError("Invalid memory limit value")
                        problem["memory_limit"]["value"] = value
                    elif tag == "img":
                        problem["images"].append({"src": None, "blob": None})
                        for child in item:
                            if child.tag == "src":
                                problem["images"][-1]["src"] = child.text
                            elif child.tag == "base64":
                                problem["images"][-1]["blob"] = base64.b64decode(child.text)
                    elif tag == "sample_input":
                        if not sample_start:
                            raise ValueError("Invalid xml, error 'sample_input' tag order")
                        problem["samples"].append({"input": item.text, "output": None})
                        sample_start = False
                    elif tag == "sample_output":
                        if sample_start:
                            raise ValueError("Invalid xml, error 'sample_output' tag order")
                        problem["samples"][-1]["output"] = item.text
                        sample_start = True
                    elif tag == "test_input":
                        if not test_case_start:
                            raise ValueError("Invalid xml, error 'test_input' tag order")
                        problem["test_cases"].append({"input": item.text, "output": None})
                        test_case_start = False
                    elif tag == "test_output":
                        if test_case_start:
                            raise ValueError("Invalid xml, error 'test_output' tag order")
                        problem["test_cases"][-1]["output"] = item.text
                        test_case_start = True

                self._parse_result = problem
                return problem
        raise ValueError("Invalid xml")

    def save_image(self, file_base_path, base_url):
        if not self._parse_result:
            self.parse()
        for item in self._parse_result["images"]:
            name = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(12))
            ext = os.path.splitext(item["src"])[1]
            file_name = name + ext
            with open(os.path.join(file_base_path, file_name), "wb") as f:
                f.write(item["blob"])
            desc = self._parse_result["description"].replace(item["src"], os.path.join(base_url, file_name))
            self._parse_result["description"] = desc
        return self._parse_result

    def save_test_case(self, file_base_path, input_preprocessor=None, output_preprocessor=None):
        if not self._parse_result:
            self.parse()
        for index, item in enumerate(self._parse_result["test_cases"]):
            with open(os.path.join(file_base_path, str(index + 1) + ".in"), "w") as f:
                if input_preprocessor:
                    input_content = input_preprocessor(item["input"])
                else:
                    input_content = item["input"]
                f.write(input_content)
            with open(os.path.join(file_base_path, str(index + 1) + ".out"), "w") as f:
                if output_preprocessor:
                    output_content = output_preprocessor(item["output"])
                else:
                    output_content = item["output"]
                f.write(output_content)


if __name__ == "__main__":
    parser = FPSParser("fps.xml")
    parser.save_image("/tmp", "/static/img")
    parser.save_test_case("/tmp")
