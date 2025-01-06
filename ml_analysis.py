import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
from config import DATA_DIR
import os

class MLAnalyzer:
    def __init__(self, data_file):
        print("📊 Loading data for ML analysis...")
        self.df = pd.read_csv(data_file)
        self.prepare_features()
        
    def prepare_features(self):
        """Prepare features for ML"""
        numerical_cols = ['volume', 'density', 'nsites', 'formation_energy_per_atom']
        categorical_cols = ['crystal_system', 'metal', 'chalcogen']
        
        # Drop rows with missing values
        self.df = self.df.dropna(subset=numerical_cols + ['band_gap'])
        
        # Create feature matrix
        X_numeric = self.df[numerical_cols]
        X_categorical = pd.get_dummies(self.df[categorical_cols])
        self.X = pd.concat([X_numeric, X_categorical], axis=1)
        self.y = self.df['band_gap']
        
        print(f"\nFeatures used: {', '.join(self.X.columns)}")
        print(f"Target: band_gap")
        print(f"\nTotal samples: {len(self.X)}")
        
    def analyze_predictions(self, y_true, y_pred, set_name):
        """Analyze prediction quality"""
        mse = mean_squared_error(y_true, y_pred)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)  # Using r2_score directly
        
        print(f"\n{set_name} Metrics:")
        print(f"Mean Squared Error: {mse:.3f}")
        print(f"Mean Absolute Error: {mae:.3f}")
        print(f"R² Score: {r2:.3f}")
        
        # Plot predictions vs actual
        plt.figure(figsize=(8, 8))
        plt.scatter(y_true, y_pred, alpha=0.5)
        plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
        plt.xlabel('Actual Band Gap (eV)')
        plt.ylabel('Predicted Band Gap (eV)')
        plt.title(f'{set_name} Predictions vs Actual')
        plt.tight_layout()
        plt.savefig(os.path.join(DATA_DIR, f'predictions_{set_name.lower()}.png'))
        plt.close()
    
    def train_model(self):
        """Train and evaluate Random Forest model"""
        # Split data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )
        
        # Scale features
        self.scaler = StandardScaler()
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_test_scaled = self.scaler.transform(self.X_test)
        
        # Cross-validation
        print("\n🔄 Performing 5-fold cross-validation...")
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        cv_scores = cross_val_score(self.model, self.X_train_scaled, self.y_train, cv=5)
        print(f"Cross-validation scores: {cv_scores}")
        print(f"Average CV score: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        # Train final model
        print("\n🤖 Training final model...")
        self.model.fit(self.X_train_scaled, self.y_train)
        
        # Make predictions
        train_pred = self.model.predict(self.X_train_scaled)
        test_pred = self.model.predict(self.X_test_scaled)
        
        # Analyze predictions
        self.analyze_predictions(self.y_train, train_pred, "Training")
        self.analyze_predictions(self.y_test, test_pred, "Test")
        
        # Feature importance
        self.feature_importance = pd.DataFrame({
            'feature': self.X.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Plot feature importance
        plt.figure(figsize=(12, 6))
        top_n = min(10, len(self.feature_importance))
        sns.barplot(data=self.feature_importance.head(top_n), 
                   x='importance', y='feature')
        plt.title('Top Features for Band Gap Prediction')
        plt.tight_layout()
        plt.savefig(os.path.join(DATA_DIR, 'feature_importance.png'))
        plt.close()
        
        return self.feature_importance

if __name__ == "__main__":
    # Get the most recent data file
    data_files = [f for f in os.listdir(DATA_DIR) if f.startswith('chalcogenides_')]
    if not data_files:
        raise FileNotFoundError("No data files found!")
    latest_file = max(data_files)
    data_path = os.path.join(DATA_DIR, latest_file)
    
    # Run analysis
    analyzer = MLAnalyzer(data_path)
    feature_importance = analyzer.train_model()
    print("\n🔍 Top 5 most important features:")
    print(feature_importance.head())