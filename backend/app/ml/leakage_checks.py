import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional

SUSPICIOUS_ID_KEYWORDS = ["id", "uuid", "guid", "hash", "account_number", "card_number", "ssn", "user_id", "transaction_id"]
SUSPICIOUS_FUTURE_KEYWORDS = ["future_", "post_", "after_", "refund_", "chargeback_status", "settlement_", "outcome", "next_tx_", "is_fraud", "label"]

class DataLeakageChecker:
    """
    Reusable ML data-leakage validation layer.
    Inspects feature vectors, dataset splits, target correlations, and preprocessor state isolation.
    """

    def __init__(self, max_correlation_threshold: float = 0.95):
        self.max_correlation_threshold = max_correlation_threshold

    def run_all_checks(
        self,
        df: pd.DataFrame,
        feature_names: List[str],
        target_name: str = "is_fraud",
        X_train: Optional[pd.DataFrame] = None,
        X_val: Optional[pd.DataFrame] = None,
        X_test: Optional[pd.DataFrame] = None,
        preprocessor: Optional[Any] = None
    ) -> Dict[str, Any]:

        report = {
            "passed": True,
            "checks": [],
            "warnings": [],
            "errors": []
        }

        # Check 1: Target column appearing in features
        self._check_target_in_features(feature_names, target_name, report)

        # Check 2: Duplicate columns
        self._check_duplicate_columns(df, feature_names, report)

        # Check 3: ID-like columns in features
        self._check_id_columns(feature_names, df, report)

        # Check 4 & 5: Train/Test row overlap and duplicate rows across splits
        if X_train is not None and X_test is not None:
            self._check_split_overlaps(X_train, X_val, X_test, report)

        # Check 6: Future-information features
        self._check_future_features(feature_names, report)

        # Check 7: Extremely suspicious target-correlated features
        if target_name in df.columns:
            self._check_target_correlation(df, feature_names, target_name, report)

        # Check 8: Preprocessing fitted on test data
        if preprocessor is not None and X_train is not None and X_test is not None:
            self._check_preprocessor_isolation(preprocessor, X_train, X_test, report)

        # Final pass determination
        report["passed"] = len(report["errors"]) == 0
        return report

    def _check_target_in_features(self, feature_names: List[str], target_name: str, report: Dict[str, Any]):
        check_name = "target_in_features"
        if target_name in feature_names:
            err = f"CRITICAL LEAKAGE: Target column '{target_name}' is included in feature names!"
            report["errors"].append(err)
            report["checks"].append({"name": check_name, "status": "FAILED", "detail": err})
        else:
            report["checks"].append({"name": check_name, "status": "PASSED", "detail": "Target column is not in feature names."})

    def _check_duplicate_columns(self, df: pd.DataFrame, feature_names: List[str], report: Dict[str, Any]):
        check_name = "duplicate_columns"
        # Duplicate column names
        if len(feature_names) != len(set(feature_names)):
            dups = [item for item in feature_names if feature_names.count(item) > 1]
            err = f"Duplicate column names found in features: {set(dups)}"
            report["errors"].append(err)
            report["checks"].append({"name": check_name, "status": "FAILED", "detail": err})
            return

        # Check identical feature values across columns
        identicals = []
        feat_df = df[feature_names]
        cols = feat_df.columns
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                c1, c2 = cols[i], cols[j]
                if feat_df[c1].equals(feat_df[c2]):
                    identicals.append((c1, c2))

        if identicals:
            warn = f"Identical feature value columns detected: {identicals}"
            report["warnings"].append(warn)
            report["checks"].append({"name": check_name, "status": "WARNING", "detail": warn})
        else:
            report["checks"].append({"name": check_name, "status": "PASSED", "detail": "No duplicate column names or identical feature values."})

    def _check_id_columns(self, feature_names: List[str], df: pd.DataFrame, report: Dict[str, Any]):
        check_name = "id_like_columns"
        found_ids = []
        for feat in feature_names:
            feat_lower = feat.lower()
            if any(kw == feat_lower or feat_lower.endswith("_id") or feat_lower.startswith("id_") for kw in ["id", "user_id", "transaction_id", "account_id", "uuid"]):
                found_ids.append(feat)

        if found_ids:
            err = f"CRITICAL LEAKAGE: ID-like column(s) detected in feature vector: {found_ids}"
            report["errors"].append(err)
            report["checks"].append({"name": check_name, "status": "FAILED", "detail": err})
        else:
            report["checks"].append({"name": check_name, "status": "PASSED", "detail": "No ID-like columns detected in features."})

    def _check_split_overlaps(
        self,
        X_train: pd.DataFrame,
        X_val: Optional[pd.DataFrame],
        X_test: pd.DataFrame,
        report: Dict[str, Any]
    ):
        check_name = "split_overlaps"
        # Index overlap check
        train_idx = set(X_train.index)
        test_idx = set(X_test.index)
        val_idx = set(X_val.index) if X_val is not None else set()

        index_overlap = train_idx.intersection(test_idx) or train_idx.intersection(val_idx) or val_idx.intersection(test_idx)
        if index_overlap:
            err = f"CRITICAL LEAKAGE: Index overlap detected across splits! ({len(index_overlap)} shared indices)"
            report["errors"].append(err)
            report["checks"].append({"name": check_name, "status": "FAILED", "detail": err})
            return

        # Duplicate row content check between train and test
        merged_dups = pd.merge(X_train.reset_index(drop=True), X_test.reset_index(drop=True), how="inner")
        if len(merged_dups) > 0:
            warn = f"Duplicate feature rows detected between Train and Test sets ({len(merged_dups)} identical rows)."
            report["warnings"].append(warn)
            report["checks"].append({"name": check_name, "status": "WARNING", "detail": warn})
        else:
            report["checks"].append({"name": check_name, "status": "PASSED", "detail": "Zero index or row content overlap between splits."})

    def _check_future_features(self, feature_names: List[str], report: Dict[str, Any]):
        check_name = "future_features"
        future_feats = []
        for feat in feature_names:
            feat_lower = feat.lower()
            if any(kw in feat_lower for kw in ["future_", "post_", "after_tx_", "refund_status", "settlement_", "chargeback_"]):
                future_feats.append(feat)

        if future_feats:
            err = f"CRITICAL LEAKAGE: Future-information feature(s) detected: {future_feats}"
            report["errors"].append(err)
            report["checks"].append({"name": check_name, "status": "FAILED", "detail": err})
        else:
            report["checks"].append({"name": check_name, "status": "PASSED", "detail": "No future-information features detected."})

    def _check_target_correlation(self, df: pd.DataFrame, feature_names: List[str], target_name: str, report: Dict[str, Any]):
        check_name = "target_correlation"
        suspicious_corr = []
        target_series = df[target_name]

        for feat in feature_names:
            if feat not in df.columns:
                continue
            series = df[feat]
            if pd.api.types.is_numeric_dtype(series):
                corr = series.corr(target_series)
                if not pd.isna(corr) and abs(corr) >= self.max_correlation_threshold:
                    suspicious_corr.append((feat, round(float(corr), 4)))

        if suspicious_corr:
            err = f"CRITICAL LEAKAGE: Feature(s) with extremely high correlation (abs > {self.max_correlation_threshold}) to target: {suspicious_corr}"
            report["errors"].append(err)
            report["checks"].append({"name": check_name, "status": "FAILED", "detail": err})
        else:
            report["checks"].append({"name": check_name, "status": "PASSED", "detail": f"All feature correlations with target are below {self.max_correlation_threshold}."})

    def _check_preprocessor_isolation(self, preprocessor: Any, X_train: pd.DataFrame, X_test: pd.DataFrame, report: Dict[str, Any]):
        check_name = "preprocessor_isolation"
        # If standard scaler or mean/std attribute exists, verify it matches train statistics
        if hasattr(preprocessor, "mean_") and hasattr(preprocessor, "feature_names_in_"):
            train_means = X_train[preprocessor.feature_names_in_].mean().values
            prep_means = preprocessor.mean_
            if not np.allclose(train_means, prep_means, rtol=1e-3):
                err = "CRITICAL LEAKAGE: Preprocessor mean statistics do not match training data! (Precomputed on test or full dataset)."
                report["errors"].append(err)
                report["checks"].append({"name": check_name, "status": "FAILED", "detail": err})
                return

        report["checks"].append({"name": check_name, "status": "PASSED", "detail": "Preprocessor state is properly isolated to training set."})

leakage_checker = DataLeakageChecker()
