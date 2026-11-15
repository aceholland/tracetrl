import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from pdf_fixture import write_pdf

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT.parents[1] / 'work/official-kit/apctt-participant-kit-0.5.0-cpu'


class AssessmentTests(unittest.TestCase):
    def setUp(self):
        from participant_module.adapter import AssessmentModule
        self.module = AssessmentModule()
        self.checklist = json.loads((ROOT / 'tests/fixtures/checklist.json').read_text(encoding='utf-8'))
        self.module.load({'checklist': self.checklist, 'module': {'settings': {}}, 'compute': {'device': 'cpu'}}, ROOT / 'assets')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def assess(self, pages, more=None, budget=180000):
        root = Path(self.temp.name)
        path = write_pdf(root / 'report.pdf', pages)
        case = {'schema_version': 'apctt-pdf-example-v1', 'checklist_version': self.checklist['version'],
                'case_id': 'TEST-1', 'assessment_target': {'target_id': 'sensor-1', 'type': 'component',
                'description': 'optical sensor'}, 'intended_application': 'water quality monitoring',
                'intended_environment': 'coastal water', 'title': 'Sensor tests', 'assessment_as_of': None,
                'input_profile': 'pdf_report', 'documents': [{'document_id': 'D1', 'title': 'Tests',
                'document_date': None, 'language': 'en', 'page_count': len(pages), 'path': str(path)}]}
        if more:
            path2 = write_pdf(root / 'other.pdf', more)
            case['documents'].append({'document_id': 'D2', 'title': 'Other', 'document_date': None,
                                      'language': 'en', 'page_count': len(more), 'path': str(path2)})
        result = self.module.assess(case, SimpleNamespace(remaining_ms=lambda: budget))
        self.assertEqual(set(result['criterion_status']), {c['criterion_id'] for c in self.checklist['criteria']})
        json.dumps(result, allow_nan=False)
        return result, case

    def test_laboratory_evidence_has_real_page_and_verbatim_span(self):
        text = 'The optical sensor prototype was tested in a laboratory chamber. Measured sensitivity was 95 percent against a requirement of 90 percent.'
        result, _ = self.assess(['A title page.', text])
        self.assertEqual(result['criterion_status']['APCTT-C04'], 'met')
        self.assertEqual(result['predicted_trl'], 4)
        evidence = result['evidence_reference']['APCTT-C04'][0]
        self.assertEqual((evidence['document_id'], evidence['page']), ('D1', 2))
        self.assertIn(' '.join(evidence['supporting_span'].split()), text)

    def test_future_testing_does_not_establish_maturity(self):
        result, _ = self.assess(['We plan to test the optical sensor prototype in the laboratory next year.'])
        self.assertEqual(result['criterion_status']['APCTT-C04'], 'insufficient evidence')
        self.assertEqual(result['assessment_status'], 'abstained')

    def test_trl_assertion_is_not_technical_evidence(self):
        result, _ = self.assess(['The optical sensor is TRL 9.'])
        self.assertEqual(result['assessment_status'], 'abstained')
        self.assertEqual(result['criterion_status']['APCTT-C09'], 'insufficient evidence')

    def test_unrelated_technology_does_not_establish_target_readiness(self):
        result, _ = self.assess(['A turbine prototype was tested in a laboratory chamber with excellent results.'])
        self.assertEqual(result['criterion_status']['APCTT-C04'], 'insufficient evidence')

    def test_explicit_non_testing_is_not_met(self):
        result, _ = self.assess(['The optical sensor prototype has not been tested in a laboratory environment.'])
        self.assertEqual(result['criterion_status']['APCTT-C04'], 'not met')

    def test_operation_requires_success_and_duration(self):
        result, _ = self.assess(['The final optical sensor system operated successfully in actual coastal field operations for 18 months.'])
        self.assertEqual(result['criterion_status']['APCTT-C09'], 'met')
        self.assertEqual(result['predicted_trl'], 9)

    def test_incomplete_operational_claim_is_not_trl_nine(self):
        result, _ = self.assess(['The optical sensor system was installed in the field.'])
        self.assertNotEqual(result['predicted_trl'], 9)

    def test_conflicting_evidence_abstains(self):
        result, _ = self.assess(['The optical sensor prototype was tested in a laboratory chamber. Measurements showed 95 percent accuracy.'],
                              ['The optical sensor prototype has not been tested in a laboratory environment.'])
        self.assertEqual(result['assessment_status'], 'abstained')
        self.assertEqual(result['abstention_reason'], 'conflicting evidence')

    def test_multiple_documents_preserve_evidence_identity(self):
        result, _ = self.assess(['Unrelated introduction.'], ['The optical sensor prototype was tested in a laboratory chamber. Measurements showed 95 percent accuracy.'])
        self.assertEqual(result['evidence_reference']['APCTT-C04'][0]['document_id'], 'D2')

    def test_ids_are_supplied_and_unknown_criteria_are_not_guessed(self):
        self.checklist = copy.deepcopy(self.checklist)
        for n, criterion in enumerate(self.checklist['criteria']):
            criterion['criterion_id'] = f'NEW-{n}'
        self.checklist['criteria'].append({'criterion_id': 'CUSTOM', 'description': 'Certified underwater acoustic compatibility.'})
        self.module.load({'checklist': self.checklist, 'module': {'settings': {}}}, ROOT / 'assets')
        result, _ = self.assess(['The optical sensor prototype was tested in a laboratory chamber. Measurements showed 95 percent accuracy.'])
        self.assertEqual(result['criterion_status']['NEW-3'], 'met')
        self.assertEqual(result['criterion_status']['CUSTOM'], 'insufficient evidence')

    def test_blank_pdf_abstains(self):
        result, _ = self.assess([''])
        self.assertEqual(result['assessment_status'], 'abstained')

    def test_exhausted_budget_abstains_without_completed_claims(self):
        result, _ = self.assess(['The optical sensor prototype was tested in a laboratory chamber.'], budget=500)
        self.assertEqual(result['assessment_status'], 'abstained')

    def test_default_does_not_import_torch(self):
        import sys
        self.assess(['The optical sensor prototype was tested in a laboratory chamber.'])
        self.assertNotIn('torch', sys.modules)

    def test_adjacent_unrelated_experiment_is_not_target_evidence(self):
        result, _ = self.assess(['The optical sensor is being developed. The turbine prototype was tested in a laboratory chamber and measured accuracy was 95 percent.'])
        self.assertEqual(result['criterion_status']['APCTT-C04'], 'insufficient evidence')

    def test_negated_successful_operation_is_not_a_success(self):
        result, _ = self.assess(['The final optical sensor system was not successfully operated in actual coastal field operations for 18 months.'])
        self.assertNotEqual(result['predicted_trl'], 9)
        self.assertNotEqual(result['criterion_status']['APCTT-C09'], 'met')

    def test_scheduled_laboratory_test_is_not_an_achieved_result(self):
        result, _ = self.assess(['The optical sensor prototype is scheduled to be tested in a laboratory chamber for accuracy.'])
        self.assertEqual(result['criterion_status']['APCTT-C04'], 'insufficient evidence')

    def test_unknown_description_with_trl_number_is_not_assumed_official(self):
        self.checklist['criteria'].append({'criterion_id': 'CUSTOM', 'description': 'Certified acoustic compatibility (TRL 4).'})
        result, _ = self.assess(['The optical sensor prototype was tested in a laboratory chamber. Measurements showed 95 percent accuracy.'])
        self.assertEqual(result['criterion_status']['CUSTOM'], 'insufficient evidence')

    def test_wrong_operating_environment_is_not_target_environment_proof(self):
        result, _ = self.assess(['The final optical sensor system operated successfully in actual dry desert field operations for 18 months.'])
        self.assertNotEqual(result['predicted_trl'], 9)

    def test_image_only_report_prevents_complete_assessment(self):
        root = Path(self.temp.name)
        path = write_pdf(root / 'scan.pdf', [''], image_only=True)
        case = {'schema_version': 'apctt-pdf-example-v1', 'case_id': 'SCAN', 'assessment_target':
                {'target_id': 'sensor-1', 'type': 'component', 'description': 'optical sensor'},
                'documents': [{'document_id': 'D1', 'page_count': 1, 'path': str(path)}]}
        result = self.module.assess(case, SimpleNamespace(remaining_ms=lambda:180000))
        self.assertEqual(result['assessment_status'], 'abstained')
        self.assertTrue(all('extraction' in s.lower() or 'text' in s.lower() for s in result['missing_evidence'].values()))

    def test_missing_results_does_not_establish_laboratory_validation(self):
        result, _ = self.assess(['The optical sensor prototype was tested in a laboratory but no measurements or results were obtained.'])
        self.assertEqual(result['criterion_status']['APCTT-C04'], 'insufficient evidence')

    def test_reporting_failed_requirements_still_satisfies_reporting_criterion(self):
        result, _ = self.assess(['The optical sensor prototype was tested in a laboratory. Measured sensitivity was 60 percent and failed the requirement of 90 percent.'])
        self.assertEqual(result['criterion_status']['APCTT-C10'], 'met')

    def test_conflict_retains_inspectable_citations_from_both_reports(self):
        result, _ = self.assess(['The optical sensor prototype was tested in a laboratory chamber. Measurements showed 95 percent accuracy.'],
                              ['The optical sensor prototype has not been tested in a laboratory environment.'])
        evidence = result['evidence_reference']['APCTT-C04']
        self.assertEqual({x['document_id'] for x in evidence}, {'D1', 'D2'})


if __name__ == '__main__':
    unittest.main()
