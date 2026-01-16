import pandas as pd
import xgboost as xgb
import shap
import joblib
import os
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import recall_score, precision_score, f1_score, classification_report
from sklearn.preprocessing import OneHotEncoder, StandardScaler, RobustScaler
from sklearn.compose import ColumnTransformer
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

class SettlementPredictor:
    def __init__(self):
        self.model = None
        self.pipeline = None
        self.explainer = None
        self.feature_names = None
        
    def build_pipeline(self):
        # Define features based on Data Generator
        # Numerical: Amount, Volatility. (Hour/Day converted to cat or num? Training as num usually fine for Tree models)
        # We will treat Trade_Hour as numerical for simplicity, or categorical. Let's stick to the prompt's simplicity.
        categorical_features = ['Asset_Class', 'Counterparty_Rating', 'SSI_Status', 'Liquidity_Score', 'Custodian_Location', 'Operation_Type', 'Currency', 'Trade_Day']
        numeric_features = ['Notional_Amount_USD', 'Market_Volatility_Index', 'Trade_Hour']
        
        # Preprocessing steps
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', RobustScaler(), numeric_features), # RobustScaler better for Whales
                ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
            ])
        
        # The Full Pipeline: Preprocess -> Oversample (SMOTE) -> Model
        self.pipeline = ImbPipeline([
            ('preprocessor', preprocessor),
            ('smote', SMOTE(random_state=42, sampling_strategy=0.5)), # Boost minority to 50% ratio
            ('classifier', xgb.XGBClassifier(
                objective='binary:logistic',
                n_estimators=300,
                learning_rate=0.05,
                max_depth=6,
                eval_metric='logloss',
                scale_pos_weight=1, # SMOTE handles the balancing
                random_state=42
            ))
        ])
        
    def train(self, data_path):
        print(f"Loading data from {data_path}...")
        df = pd.read_csv(data_path)
        
        # Drop non-features
        drop_cols = ['IS_FAILED', 'Trade_ID', 'Trade_Date', 'Settlement_Date', 'Counterparty', 'Counterparty_ID', 'ISIN', 'Failure_Prob']
        # Ensure we only drop what exists
        X = df.drop([c for c in drop_cols if c in df.columns], axis=1)
        y = df['IS_FAILED']
        
        print(f"Features: {X.columns.tolist()}")
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
        
        print("Training Model...")
        self.pipeline.fit(X_train, y_train)
        
        # Evaluation
        preds = self.pipeline.predict(X_test)
        report = classification_report(y_test, preds, output_dict=True)
        
        print("\n--- Evaluation Metrics ---")
        print(f"Recall (Catching Failures): {report['1']['recall']:.4f}")
        print(f"Precision: {report['1']['precision']:.4f}")
        print(f"F1 Score: {report['1']['f1-score']:.4f}")
        
        # Save metrics
        os.makedirs('model', exist_ok=True)
        with open('model/metrics.json', 'w') as f:
            json.dump(report, f, indent=4)
            
        return X_test # Return for SHAP
        
    def generate_explanation(self, X_part):
        print("Generating SHAP Explainer...")
        # Extract model and preprocessor
        model_step = self.pipeline.named_steps['classifier']
        preprocessor_step = self.pipeline.named_steps['preprocessor']
        
        # SHAP must operate on transformed data
        X_transformed = preprocessor_step.transform(X_part)
        
        # Get feature names
        try:
            cat_features = preprocessor_step.named_transformers_['cat'].get_feature_names_out()
            # Num features are just the list
            # We need to know the order. ColumnTransformer output order is usually transformers order.
            # Num first, then Cat
            num_features = ['Notional_Amount_USD', 'Market_Volatility_Index', 'Trade_Hour']
            self.feature_names = num_features + list(cat_features)
        except:
             print("Could not extract feature names perfectly.")

        self.explainer = shap.TreeExplainer(model_step)
        # Verify it works on a sample
        # _ = self.explainer.shap_values(X_transformed[:10])

    def save_artifacts(self, path='model/'):
        os.makedirs(path, exist_ok=True)
        # Save the whole pipeline
        joblib.dump(self.pipeline, f'{path}model.joblib') # Keeping model.joblib name for compatibility
        # Save SHAP explainer
        joblib.dump(self.explainer, f'{path}shap_explainer.joblib')
        if self.feature_names:
             joblib.dump(self.feature_names, f'{path}feature_names.joblib')
        print(f"Artifacts saved to {path}")

if __name__ == "__main__":
    predictor = SettlementPredictor()
    predictor.build_pipeline()
    X_test = predictor.train('settlement_data.csv')
    predictor.generate_explanation(X_test)
    predictor.save_artifacts()
