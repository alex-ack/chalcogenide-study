import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GroupShuffleSplit
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, r2_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import os
from config import DATA_DIR

class MLModel:
    def __init__(self, filename):
        self.filepath = os.path.join(DATA_DIR, filename)
        self.df = pd.read_csv(self.filepath)
        self.scaler = StandardScaler()

    def preprocess_data(self, drop_energy=True):
        print("\n🔄 Preprocessing Data...")

        # Drop non-numeric columns, except for 'chemsys'
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        self.df = self.df[numeric_cols]

        # Handle missing values by filling with mean
        self.df.fillna(self.df.mean(), inplace=True)

        # Feature selection
        self.features = ['volume', 'density', 'nsites']
        if not drop_energy:
            self.features.append('formation_energy_per_atom')
        self.target_band_gap = 'band_gap'
        self.target_class = 'is_semiconductor'

        # Add a binary column for classification (1 if band_gap > 0)
        self.df[self.target_class] = (self.df['band_gap'] > 0).astype(int)

        # Standardize features
        X = self.df[self.features]
        X_scaled = self.scaler.fit_transform(X)
        return X_scaled

    def train_regression_model(self, X_scaled):
        print("\n📈 Training Regression Model for Band Gap Prediction...")
        y = self.df[self.target_band_gap]

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

        # Model training
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Predictions
        y_pred = model.predict(X_test)

        # Evaluation
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        print(f"MSE: {mse:.4f}")
        print(f"R²: {r2:.4f}")

        # Feature importance
        importances = model.feature_importances_
        importance_df = pd.DataFrame({'Feature': self.features, 'Importance': importances}).sort_values(by='Importance', ascending=False)
        print("\nFeature Importances:")
        print(importance_df)

        return model

    def train_classification_model(self, X_scaled):
        print("\n📊 Training Classification Model for Metal vs Semiconductor...")
        y = self.df[self.target_class]

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

        # Model training
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Predictions
        y_pred = model.predict(X_test)

        # Evaluation
        print(classification_report(y_test, y_pred))
        cm = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.title('Confusion Matrix')
        plt.savefig(f"{DATA_DIR}/confusion_matrix.png")
        plt.close()

        return model

if __name__ == "__main__":
    filename = "chalcogenides_latest.csv"
    ml_model = MLModel(filename)

    # Test without formation energy
    print("\n--- Model Without Formation Energy ---")
    X_scaled_no_energy = ml_model.preprocess_data(drop_energy=True)
    reg_model_no_energy = ml_model.train_regression_model(X_scaled_no_energy)
    clf_model_no_energy = ml_model.train_classification_model(X_scaled_no_energy)

    # Test with formation energy
    print("\n--- Model With Formation Energy ---")
    X_scaled_with_energy = ml_model.preprocess_data(drop_energy=False)
    reg_model_with_energy = ml_model.train_regression_model(X_scaled_with_energy)
    clf_model_with_energy = ml_model.train_classification_model(X_scaled_with_energy)
