"""Offline regression checks for optional-object serialization; no dataset access."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '04-pipeline'))
from empty_optional_objects_v1_2 import check_objects, has_meaningful_value
from normalized_to_sanity_ndjson_v1_2 import to_sanity_doc

spec = importlib.util.spec_from_file_location('validator', ROOT / '09-schema-transform-repair/validate_sanity_ndjson_v1_2.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

class EmptyObjectTests(unittest.TestCase):
    def transform(self, basis):
        return to_sanity_doc('CostProfile', {'id': 'test', 'living_cost_source_basis': basis}, '2026-09-24T00:00:00Z', 'test')

    def test_empty_bases_omitted(self):
        for value in ({}, {'_type': 'livingCostSourceBasis'},
                      {'kind': None, 'description': ' \t', 'administering_body': ''}, None):
            with self.subTest(value=value):
                self.assertNotIn('living_cost_source_basis', self.transform(value))

    def test_populated_and_incomplete_bases_preserved(self):
        for value in ({'kind': 'not_published', 'description': 'Source says no estimate', 'administering_body': 'University'},
                      {'description': 'Partial source finding'}, {'description': 'UNKNOWN'}):
            result = self.transform(value)['living_cost_source_basis']
            self.assertEqual(result, {**value, '_type': 'livingCostSourceBasis'})

    def test_other_optional_objects(self):
        for entity, field in [('Program', 'testing_policy'), ('ProgramPathway', 'progression_requirement'),
                              ('CostProfile', 'estimated_living_costs_monthly_range')]:
            result = to_sanity_doc(entity, {'id': 'test', field: {}}, 'date', 'school')
            self.assertNotIn(field, result)

    def test_unknown_zero_false_empty_arrays_and_boxes(self):
        for value in ('UNKNOWN', 0, False, []):
            self.assertTrue(has_meaningful_value(value))
        doc = to_sanity_doc('Program', {'id': 'test', 'testing_policy': {'standardized_tests': []}}, 'date', 'school')
        self.assertEqual(doc['testing_policy']['standardized_tests'], [])
        for value in (None, {}, [], False, 0, 'UNKNOWN'):
            doc = to_sanity_doc('VerificationRecord', {'id': 'test', 'proposed_value': value}, 'date', 'school')
            self.assertIn('proposed_value', doc)
        doc = to_sanity_doc('CostProfile', {'id': 'test', 'extension_metadata': {'note': '', 'fields': {'finding': None}}}, 'date', 'school')
        self.assertEqual(doc['extension_metadata']['fields'][0]['value'], 'null')

    def test_required_empty_object_not_removed(self):
        schema = {'$defs': {'sample': {'properties': {'basis': {'type': 'object', 'properties': {}}}, 'required': ['basis']}}}
        doc = {'_type': 'sample', 'basis': {}}
        result, errors = check_objects(doc, omit_empty=True, schema=schema)
        self.assertEqual(result, doc)
        self.assertFalse(errors[0]['optional'])

    def test_validator_rejects_empty_optional_objects(self):
        for value in ({}, {'_type': 'livingCostSourceBasis'}, {'_type': 'livingCostSourceBasis', 'description': ' '}):
            doc = {'_id': 'drafts.costProfile-test', '_type': 'costProfile', 'id': 'test', 'living_cost_source_basis': value}
            with tempfile.TemporaryDirectory() as temp:
                p = Path(temp) / 'fixture.ndjson'
                p.write_text(json.dumps(doc)+'\n', encoding='utf-8')
                _, errors = validator.validate_files([str(p)], str(ROOT / '02-schema-design/evidapath-schema-v1.2.json'))
                self.assertTrue(any('empty optional/nullable object at living_cost_source_basis' in e for e in errors))

    def test_no_input_mutation_and_determinism(self):
        source = {'id': 'test', 'living_cost_source_basis': {'description': None}}
        before = json.dumps(source, sort_keys=True)
        a = to_sanity_doc('CostProfile', source, 'date', 'school')
        b = to_sanity_doc('CostProfile', source, 'date', 'school')
        self.assertEqual(a, b)
        self.assertEqual(json.dumps(source, sort_keys=True), before)

if __name__ == '__main__':
    unittest.main()
