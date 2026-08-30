import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.tests.test_feature_engine import test_haversine_distance, test_feature_computation
from backend.tests.test_policy_engine import test_policy_engine_escalation
from backend.tests.test_api import test_root_endpoint, test_metrics_endpoint, test_risk_evaluate_flow, test_policies_endpoint
from backend.tests.test_ml_pipeline import TestMLPipelineAudit
from backend.tests.test_synthetic_data import TestSyntheticDataGenerator
from backend.tests.test_leakage_checks import TestDataLeakageChecker
from backend.tests.test_split import TestDatasetSplitter
from backend.tests.test_model_registry import TestModelRegistry
from backend.tests.test_calibrator import TestProbabilityCalibrator
from backend.tests.test_evaluator import TestModelEvaluator
from backend.tests.test_datasets import TestDatasetsModule
from backend.tests.test_public_preprocessor import TestPublicPreprocessor
from backend.tests.test_public_training import TestPublicTraining
from backend.tests.test_public_calibration import TestPublicCalibration
from backend.tests.test_public_evaluation import TestPublicEvaluation
from backend.tests.test_public_explainability import TestPublicExplainability

class TestPayGuardBackend(unittest.TestCase):
    def test_haversine(self):
        test_haversine_distance()

    def test_feature_engine(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from backend.app.database import Base
        from backend.app.models import User, Merchant
        
        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        user = User(id="usr_test", email="test@example.com", name="Test User", home_country="US", home_lat=40.7128, home_lon=-74.0060)
        merchant = Merchant(id="mer_test", name="Test Merchant", category_code="5411", mcc_risk_tier=2, country="US")
        session.add(user)
        session.add(merchant)
        session.commit()

        test_feature_computation(session)
        session.close()

    def test_policy_engine(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from backend.app.database import Base
        from backend.app.services.policy_engine import policy_engine

        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        policy_engine.seed_default_policies(session)
        test_policy_engine_escalation(session)
        session.close()

    def test_api_routes(self):
        test_root_endpoint()
        test_metrics_endpoint()
        test_risk_evaluate_flow()
        test_policies_endpoint()

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestPayGuardBackend))
    suite.addTests(loader.loadTestsFromTestCase(TestMLPipelineAudit))
    suite.addTests(loader.loadTestsFromTestCase(TestSyntheticDataGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestDataLeakageChecker))
    suite.addTests(loader.loadTestsFromTestCase(TestDatasetSplitter))
    suite.addTests(loader.loadTestsFromTestCase(TestModelRegistry))
    suite.addTests(loader.loadTestsFromTestCase(TestProbabilityCalibrator))
    suite.addTests(loader.loadTestsFromTestCase(TestModelEvaluator))
    suite.addTests(loader.loadTestsFromTestCase(TestDatasetsModule))
    suite.addTests(loader.loadTestsFromTestCase(TestPublicPreprocessor))
    suite.addTests(loader.loadTestsFromTestCase(TestPublicTraining))
    suite.addTests(loader.loadTestsFromTestCase(TestPublicCalibration))
    suite.addTests(loader.loadTestsFromTestCase(TestPublicEvaluation))
    suite.addTests(loader.loadTestsFromTestCase(TestPublicExplainability))
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())
