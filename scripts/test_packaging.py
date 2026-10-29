"""Regression checks for the Agent Plugins packaging and discovery contract."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "validate_content", Path(__file__).with_name("validate-content.py")
)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)
REPO = validator.ROOT


class PackagingTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.manifest = json.loads((REPO / "plugin.json").read_text())
        self.write_manifest()
        self.agent = self.root / validator.AGENT_DIRECTORY / "github-skills-orchestrator.agent.md"
        self.agent.parent.mkdir(parents=True)
        self.agent.write_text((REPO / validator.AGENT_DIRECTORY / self.agent.name).read_text())
        for skill in validator.RENAMED_SKILLS.values():
            path = self.root / "skills" / skill / "SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_text(f"---\nname: {skill}\ndescription: Test skill.\n---\n")
        (self.root / "evals").mkdir()
        (self.root / "evals/evals.json").write_text("[]")
        root_patch = patch.object(validator, "ROOT", self.root)
        root_patch.start()
        self.addCleanup(root_patch.stop)
        validator.failures.clear()

    def write_manifest(self):
        (self.root / "plugin.json").write_text(json.dumps(self.manifest))

    def check_packaging(self):
        validator.check_manifest()
        validator.check_agents()
        validator.check_skill_discovery()
        validator.check_lifecycle_topology()

    def assert_failure(self, text):
        self.assertTrue(
            any(text in failure for failure in validator.failures),
            validator.failures,
        )

    def test_compliant_package_discovers_one_agent_and_five_skills(self):
        self.check_packaging()
        self.assertEqual([], validator.failures)

    def test_schema_identifier_is_required_and_exact(self):
        for schema in (None, "https://example.com/plugin.schema.json"):
            with self.subTest(schema=schema):
                validator.failures.clear()
                self.manifest["$schema"] = schema
                self.write_manifest()
                validator.check_manifest()
                self.assert_failure("$schema must be")

    def test_component_path_arrays_are_not_core_manifest_fields(self):
        for field in ("agents", "skills"):
            with self.subTest(field=field):
                validator.failures.clear()
                self.manifest[field] = [f"./{field}"]
                self.write_manifest()
                validator.check_manifest()
                self.assert_failure(f"unknown top-level field '{field}'")
                del self.manifest[field]

    def test_missing_or_malformed_manifest_fails_explicitly(self):
        (self.root / "plugin.json").unlink()
        validator.check_manifest()
        self.assert_failure("cannot read root plugin.json")
        for text in ("{", "[]"):
            with self.subTest(text=text):
                validator.failures.clear()
                (self.root / "plugin.json").write_text(text)
                validator.check_manifest()
                self.assertTrue(validator.failures)

    def test_legacy_manifest_cannot_shadow_root_manifest(self):
        legacy = self.root / ".github/plugin/plugin.json"
        legacy.parent.mkdir(parents=True)
        legacy.write_text(json.dumps(self.manifest))
        validator.check_manifest()
        self.assert_failure("remove legacy manifest")

    def test_invalid_metadata_is_rejected(self):
        for field, value in (
            ("name", "Invalid--Name"),
            ("version", 301),
            ("description", ""),
            ("author", {"unknown": "value"}),
            ("keywords", ["valid", 1]),
            ("extensions", {"com.github.copilot": []}),
        ):
            with self.subTest(field=field):
                validator.failures.clear()
                original = self.manifest.copy()
                self.manifest[field] = value
                self.write_manifest()
                validator.check_manifest()
                self.assertTrue(validator.failures)
                self.manifest = original

    def test_orchestrator_in_legacy_directory_is_not_discovered(self):
        legacy = self.root / "agents" / self.agent.name
        legacy.parent.mkdir()
        self.agent.rename(legacy)
        self.check_packaging()
        self.assert_failure("no agent files found in com.github.copilot/agents/")
        self.assert_failure("legacy agents/ is not discovered")

    def test_missing_skill_entry_point_is_rejected(self):
        (self.root / "skills/github-skills-outline/SKILL.md").unlink()
        self.check_packaging()
        self.assert_failure("missing SKILL.md")
        self.assert_failure("expected exactly the five lifecycle skills")

    def test_nested_skill_is_not_a_discoverable_replacement(self):
        skill = self.root / "skills/github-skills-outline/SKILL.md"
        nested = skill.parent / "nested/SKILL.md"
        nested.parent.mkdir()
        skill.rename(nested)
        self.check_packaging()
        self.assert_failure("missing SKILL.md")
        self.assert_failure("expected exactly the five lifecycle skills")

    def test_skill_name_and_description_are_checked(self):
        skill = self.root / "skills/github-skills-outline/SKILL.md"
        skill.write_text("---\nname: wrong-name\ndescription: ''\n---\n")
        validator.check_skill_discovery()
        self.assert_failure("field 'description' must be a non-empty string")
        self.assert_failure("name must match skill directory")

    def test_valid_yaml_frontmatter_formats_are_accepted(self):
        for path, name, check in (
            (self.root / "skills/github-skills-outline/SKILL.md",
             "github-skills-outline", validator.check_skill_discovery),
            (self.agent, "github-skills-orchestrator", validator.check_agents),
        ):
            for description in (
                "description:\n  A valid indented description.",
                "description: >-\n  A folded description\n  over two lines.",
                "description: |\n  A literal description.\n  Another line.",
                'description: "Quoted: description" # comment',
                "description: A plain description. # comment",
            ):
                with self.subTest(path=path, description=description):
                    validator.failures.clear()
                    path.write_text(f'---\nname: "{name}" # comment\n{description}\n---\n')
                    check()
                    self.assertEqual([], validator.failures)

    def test_invalid_yaml_frontmatter_is_reported(self):
        for path, check in (
            (self.root / "skills/github-skills-outline/SKILL.md", validator.check_skill_discovery),
            (self.agent, validator.check_agents),
        ):
            for block, expected in (
                ("name: [unclosed", "frontmatter does not parse"),
                ("- name: nested\n- description: nested", "frontmatter must be a YAML mapping"),
                ("null", "frontmatter must be a YAML mapping"),
                ("metadata:\n  name: nested\n  description: nested", "missing required field 'name'"),
            ):
                with self.subTest(path=path, block=block):
                    validator.failures.clear()
                    path.write_text(f"---\n{block}\n---\n")
                    check()
                    self.assert_failure(expected)

    def test_frontmatter_fields_must_be_nonempty_strings(self):
        for path, check in (
            (self.root / "skills/github-skills-outline/SKILL.md", validator.check_skill_discovery),
            (self.agent, validator.check_agents),
        ):
            for field in ("name", "description"):
                for value in ("null", "42", "true", "[]", "{}", "''", "'   '", "|"):
                    with self.subTest(path=path, field=field, value=value):
                        validator.failures.clear()
                        other = "description" if field == "name" else "name"
                        path.write_text(f"---\n{field}: {value}\n{other}: valid-string\n---\n")
                        check()
                        self.assert_failure(f"field '{field}' must be a non-empty string")

    def test_missing_skills_directory_reports_failure(self):
        empty = self.root / "empty"
        empty.mkdir()
        with patch.object(validator, "ROOT", empty):
            validator.check_skill_discovery()
        self.assert_failure("missing skills/ directory")

    def test_components_cannot_resolve_outside_plugin_root(self):
        for component, check in (
            (self.root / "plugin.json", validator.check_manifest),
            (self.agent, validator.check_agents),
            (self.root / "skills/github-skills-outline/SKILL.md", validator.check_skill_discovery),
        ):
            with self.subTest(component=component):
                validator.failures.clear()
                original = component.read_bytes()
                with tempfile.TemporaryDirectory() as external:
                    target = Path(external) / component.name
                    target.write_bytes(original)
                    component.unlink()
                    component.symlink_to(target)
                    try:
                        check()
                        self.assert_failure("path must resolve within the plugin root")
                    finally:
                        component.unlink()
                        component.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
