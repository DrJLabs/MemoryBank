#!/usr/bin/env python3
"""
PHASE 5: Advanced AI Integration & Predictive Analytics
Enterprise-grade AI system with machine learning models, real-time processing,
anomaly detection, predictive maintenance, and intelligent forecasting.
"""

import sys
import json
import sqlite3
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# ML and AI libraries (with graceful fallbacks)
try:
    from sklearn.ensemble import RandomForestRegressor, IsolationForest
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, r2_score
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  Machine Learning libraries not available. Install: pip install scikit-learn numpy")

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    plt.style.use('seaborn-v0_8')
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False

class PredictionModel(Enum):
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    ENSEMBLE = "ensemble"

class AnomalyType(Enum):
    PERFORMANCE = "performance"
    USAGE_PATTERN = "usage_pattern"
    GROWTH_RATE = "growth_rate"
    RESOURCE_CONSUMPTION = "resource_consumption"

@dataclass
class PredictionResult:
    model_type: str
    predictions: List[float]
    confidence_intervals: List[Tuple[float, float]]
    model_accuracy: float
    feature_importance: Dict[str, float]
    forecast_horizon_days: int

@dataclass
class AnomalyDetection:
    anomalies: List[Dict[str, Any]]
    anomaly_scores: List[float]
    threshold: float
    detection_model: str

class AdvancedAIPredictiveSystem:
    """
    Enterprise-grade AI system with machine learning models for predictive analytics,
    real-time processing, anomaly detection, and intelligent forecasting.
    """
    
    def __init__(self, data_path: str = "growth_analysis.db"):
        self.data_path = data_path
        self.models = {}
        self.scalers = {}
        self.prediction_cache = {}
        self.anomaly_detectors = {}
        
        # Configuration (must be before ML initialization)
        self.config = {
            "prediction_horizon_days": 90,
            "anomaly_threshold": 0.1,
            "model_retrain_days": 7,
            "confidence_level": 0.95,
            "min_data_points": 5,
            "feature_selection_threshold": 0.05
        }
        
        # Initialize ML models if available
        if ML_AVAILABLE:
            self._initialize_ml_models()
        
        self._setup_ai_database()

    def _setup_ai_database(self):
        """Setup AI-specific database tables"""
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            # AI Predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    model_type TEXT NOT NULL,
                    prediction_horizon_days INTEGER,
                    predictions TEXT,  -- JSON array of predictions
                    confidence_intervals TEXT,  -- JSON array of confidence intervals
                    model_accuracy REAL,
                    feature_importance TEXT,  -- JSON object
                    actual_vs_predicted TEXT  -- JSON for validation
                )
            """)
            
            # Anomaly Detection table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    anomaly_type TEXT NOT NULL,
                    anomaly_score REAL,
                    description TEXT,
                    severity TEXT,
                    resolved BOOLEAN DEFAULT FALSE,
                    metadata TEXT  -- JSON
                )
            """)
            
            # AI Model Performance table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_model_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    accuracy REAL,
                    mae REAL,
                    r2_score REAL,
                    training_data_points INTEGER,
                    performance_metadata TEXT  -- JSON
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Database setup error: {e}")

    def _initialize_ml_models(self):
        """Initialize machine learning models"""
        if not ML_AVAILABLE:
            return
        
        # Regression models for predictions
        self.models['linear'] = LinearRegression()
        self.models['random_forest'] = RandomForestRegressor(
            n_estimators=100, random_state=42, max_depth=10
        )
        
        # Anomaly detection models
        self.anomaly_detectors['isolation_forest'] = IsolationForest(
            contamination=self.config['anomaly_threshold'],
            random_state=42
        )
        
        # Scalers for feature normalization
        self.scalers['standard'] = StandardScaler()

    def generate_intelligent_predictions(self, target_metric: str = "memory_count",
                                       horizon_days: int = 90) -> PredictionResult:
        """
        Generate intelligent predictions using multiple ML models and ensemble methods.
        """
        if not ML_AVAILABLE:
            return self._fallback_statistical_prediction(target_metric, horizon_days)
        
        # Get historical data
        data = self._get_historical_data()
        if len(data) < self.config['min_data_points']:
            return self._fallback_statistical_prediction(target_metric, horizon_days)
        
        # Prepare features and target
        X, y, feature_names = self._prepare_ml_features(data, target_metric)
        
        if len(X) < self.config['min_data_points']:
            return self._fallback_statistical_prediction(target_metric, horizon_days)
        
        # Train ensemble of models
        predictions = {}
        accuracies = {}
        feature_importances = {}
        
        # Linear Regression
        try:
            X_scaled = self.scalers['standard'].fit_transform(X)
            self.models['linear'].fit(X_scaled, y)
            
            # Generate future features
            future_X = self._generate_future_features(X, horizon_days)
            future_X_scaled = self.scalers['standard'].transform(future_X)
            
            linear_pred = self.models['linear'].predict(future_X_scaled)
            predictions['linear'] = linear_pred
            
            # Cross-validation accuracy
            if len(X) > 4:
                X_train, X_test, y_train, y_test = train_test_split(
                    X_scaled, y, test_size=0.2, random_state=42
                )
                self.models['linear'].fit(X_train, y_train)
                y_pred = self.models['linear'].predict(X_test)
                accuracies['linear'] = r2_score(y_test, y_pred)
            else:
                accuracies['linear'] = 0.5
            
        except Exception as e:
            print(f"⚠️  Linear model error: {e}")
            predictions['linear'] = np.zeros(horizon_days)
            accuracies['linear'] = 0.0
        
        # Random Forest
        try:
            self.models['random_forest'].fit(X, y)
            
            future_X = self._generate_future_features(X, horizon_days)
            rf_pred = self.models['random_forest'].predict(future_X)
            predictions['random_forest'] = rf_pred
            
            # Feature importance
            importance = self.models['random_forest'].feature_importances_
            feature_importances = dict(zip(feature_names, importance))
            
            # Cross-validation accuracy
            if len(X) > 4:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
                self.models['random_forest'].fit(X_train, y_train)
                y_pred = self.models['random_forest'].predict(X_test)
                accuracies['random_forest'] = r2_score(y_test, y_pred)
            else:
                accuracies['random_forest'] = 0.5
                
        except Exception as e:
            print(f"⚠️  Random Forest error: {e}")
            predictions['random_forest'] = np.zeros(horizon_days)
            accuracies['random_forest'] = 0.0
        
        # Ensemble prediction (weighted average based on accuracy)
        total_weight = sum(accuracies.values()) or 1.0
        weights = {model: acc / total_weight for model, acc in accuracies.items()}
        
        ensemble_pred = np.zeros(horizon_days)
        for model, pred in predictions.items():
            if weights[model] > 0:
                ensemble_pred += weights[model] * pred
        
        # Calculate confidence intervals
        confidence_intervals = self._calculate_confidence_intervals(
            predictions, ensemble_pred, self.config['confidence_level']
        )
        
        # Overall model accuracy
        overall_accuracy = max(accuracies.values()) if accuracies else 0.0
        
        result = PredictionResult(
            model_type="ensemble",
            predictions=ensemble_pred.tolist(),
            confidence_intervals=confidence_intervals,
            model_accuracy=overall_accuracy,
            feature_importance=feature_importances,
            forecast_horizon_days=horizon_days
        )
        
        # Store prediction in database
        self._store_prediction(result)
        
        return result

    def _get_historical_data(self) -> List[Dict[str, Any]]:
        """Get historical data for ML training"""
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            # Check if memory_metrics table exists, fallback to simulated data
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memory_metrics'")
            if not cursor.fetchone():
                conn.close()
                return self._generate_sample_data()
            
            cursor.execute("""
                SELECT timestamp, memory_count, api_response_time_ms, system_cpu_percent,
                       system_memory_percent, disk_usage_percent
                FROM memory_metrics 
                ORDER BY timestamp
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            data = []
            for row in rows:
                data.append({
                    'timestamp': row[0],
                    'memory_count': row[1] or 0,
                    'api_response_time': row[2] or 0,
                    'cpu_percent': row[3] or 0,
                    'memory_percent': row[4] or 0,
                    'disk_percent': row[5] or 0
                })
            
            # If no useful data (all zeros), generate sample data for demonstration
            if not data or all(d['memory_count'] == 0 and d['api_response_time'] == 0 for d in data):
                print("📊 No meaningful data found, generating sample data for AI demonstration...")
                return self._generate_sample_data()
            
            return data
        except Exception as e:
            print(f"⚠️  Data loading error: {e}")
            print("📊 Generating sample data for AI demonstration...")
            return self._generate_sample_data()

    def _generate_sample_data(self) -> List[Dict[str, Any]]:
        """Generate realistic sample data for AI demonstration"""
        import random
        from datetime import datetime, timedelta
        
        data = []
        base_time = datetime.now() - timedelta(days=30)
        
        # Generate 30 days of realistic data
        for i in range(30):
            timestamp = (base_time + timedelta(days=i)).isoformat()
            
            # Simulate realistic memory growth with some noise
            base_memory = 20 + i * 0.5  # Gradual growth
            memory_noise = random.gauss(0, 2)  # Random variation
            memory_count = max(0, base_memory + memory_noise)
            
            # Simulate API response times with occasional spikes
            base_api_time = 150 + random.gauss(0, 30)
            if random.random() < 0.1:  # 10% chance of spike
                base_api_time *= 3
            
            # Simulate system resources
            cpu_base = 25 + random.gauss(0, 10)
            memory_base = 55 + random.gauss(0, 8)
            disk_base = 48 + random.gauss(0, 5)
            
            data.append({
                'timestamp': timestamp,
                'memory_count': round(memory_count, 1),
                'api_response_time': max(50, round(base_api_time)),
                'cpu_percent': max(5, min(95, round(cpu_base, 1))),
                'memory_percent': max(30, min(90, round(memory_base, 1))),
                'disk_percent': max(40, min(80, round(disk_base, 1)))
            })
        
        return data

    def _prepare_ml_features(self, data: List[Dict], target_metric: str) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare features and target for ML models"""
        
        features = []
        targets = []
        
        feature_names = [
            'day_of_week', 'hour_of_day', 'days_since_start',
            'cpu_percent', 'memory_percent', 'disk_percent',
            'api_response_time', 'rolling_avg_3', 'rolling_avg_7',
            'growth_rate_1d', 'growth_rate_7d'
        ]
        
        for i, point in enumerate(data):
            try:
                # Parse timestamp
                dt = datetime.fromisoformat(point['timestamp'].replace('Z', '+00:00'))
                
                # Time-based features
                day_of_week = dt.weekday()
                hour_of_day = dt.hour
                days_since_start = i
                
                # System metrics
                cpu = point.get('cpu_percent', 0)
                memory = point.get('memory_percent', 0)
                disk = point.get('disk_percent', 0)
                api_time = point.get('api_response_time', 0)
                
                # Rolling averages
                start_idx = max(0, i - 3)
                rolling_3 = np.mean([data[j].get(target_metric, 0) for j in range(start_idx, i + 1)])
                
                start_idx = max(0, i - 7)
                rolling_7 = np.mean([data[j].get(target_metric, 0) for j in range(start_idx, i + 1)])
                
                # Growth rates
                growth_1d = 0
                growth_7d = 0
                if i > 0:
                    prev_val = data[i-1].get(target_metric, 0)
                    curr_val = point.get(target_metric, 0)
                    if prev_val > 0:
                        growth_1d = (curr_val - prev_val) / prev_val
                
                if i > 7:
                    prev_val = data[i-7].get(target_metric, 0)
                    curr_val = point.get(target_metric, 0)
                    if prev_val > 0:
                        growth_7d = (curr_val - prev_val) / prev_val
                
                feature_vector = [
                    day_of_week, hour_of_day, days_since_start,
                    cpu, memory, disk, api_time,
                    rolling_3, rolling_7, growth_1d, growth_7d
                ]
                
                features.append(feature_vector)
                targets.append(point.get(target_metric, 0))
                
            except Exception as e:
                continue
        
        return np.array(features), np.array(targets), feature_names

    def _generate_future_features(self, historical_X: np.ndarray, horizon_days: int) -> np.ndarray:
        """Generate features for future time points"""
        if len(historical_X) == 0:
            return np.zeros((horizon_days, 11))  # 11 features
        
        last_point = historical_X[-1].copy()
        future_features = []
        
        for day in range(1, horizon_days + 1):
            future_point = last_point.copy()
            
            # Update time-based features
            future_point[2] += day  # days_since_start
            
            # Simulate realistic future values based on trends
            if len(historical_X) > 7:
                # Use recent trend for system metrics
                recent_trend = np.mean(historical_X[-7:], axis=0) - np.mean(historical_X[-14:-7], axis=0) if len(historical_X) > 14 else np.zeros(len(last_point))
                future_point[3:7] += recent_trend[3:7] * 0.1  # Small trend continuation
                
                # Keep rolling averages relatively stable
                future_point[7:9] = last_point[7:9]  # rolling averages
                
                # Moderate growth rates
                future_point[9:11] *= 0.95  # Decay growth rates
            
            future_features.append(future_point)
        
        return np.array(future_features)

    def _calculate_confidence_intervals(self, predictions: Dict[str, np.ndarray], 
                                      ensemble_pred: np.ndarray, 
                                      confidence_level: float) -> List[Tuple[float, float]]:
        """Calculate confidence intervals for predictions"""
        
        intervals = []
        
        # Calculate prediction variance across models
        pred_matrix = np.array(list(predictions.values()))
        
        for i in range(len(ensemble_pred)):
            if len(pred_matrix) > 1:
                std_dev = np.std(pred_matrix[:, i])
                margin = 1.96 * std_dev  # 95% confidence interval approximation
            else:
                margin = abs(ensemble_pred[i] * 0.2)  # 20% margin as fallback
            
            lower = max(0, ensemble_pred[i] - margin)
            upper = ensemble_pred[i] + margin
            intervals.append((lower, upper))
        
        return intervals

    def detect_anomalies(self, metric_types: List[str] = None) -> AnomalyDetection:
        """
        Detect anomalies using isolation forest and statistical methods
        """
        if metric_types is None:
            metric_types = ['memory_count', 'api_response_time', 'cpu_percent', 'memory_percent']
        
        data = self._get_historical_data()
        if len(data) < 10:  # Need sufficient data for anomaly detection
            return AnomalyDetection([], [], 0.1, "insufficient_data")
        
        # Prepare data for anomaly detection
        feature_matrix = []
        timestamps = []
        
        for point in data:
            try:
                features = [
                    point.get('memory_count', 0),
                    point.get('api_response_time', 0),
                    point.get('cpu_percent', 0),
                    point.get('memory_percent', 0),
                    point.get('disk_percent', 0)
                ]
                feature_matrix.append(features)
                timestamps.append(point['timestamp'])
            except:
                continue
        
        if len(feature_matrix) < 10:
            return AnomalyDetection([], [], 0.1, "insufficient_features")
        
        feature_matrix = np.array(feature_matrix)
        
        # Detect anomalies
        anomalies = []
        anomaly_scores = []
        
        if ML_AVAILABLE:
            # ML-based anomaly detection
            try:
                # Fit isolation forest
                isolation_forest = IsolationForest(
                    contamination=self.config['anomaly_threshold'],
                    random_state=42
                )
                anomaly_labels = isolation_forest.fit_predict(feature_matrix)
                scores = isolation_forest.score_samples(feature_matrix)
                
                for i, (label, score) in enumerate(zip(anomaly_labels, scores)):
                    if label == -1:  # Anomaly detected
                        anomaly_data = {
                            'timestamp': timestamps[i],
                            'type': self._classify_anomaly_type(feature_matrix[i]),
                            'score': abs(score),
                            'values': feature_matrix[i].tolist(),
                            'description': self._describe_anomaly(feature_matrix[i], feature_matrix)
                        }
                        anomalies.append(anomaly_data)
                        anomaly_scores.append(abs(score))
                
                # Store anomalies in database
                self._store_anomalies(anomalies)
                
                return AnomalyDetection(anomalies, anomaly_scores, self.config['anomaly_threshold'], "isolation_forest")
                
            except Exception as e:
                print(f"⚠️  ML anomaly detection error: {e}")
        
        # Statistical fallback
        return self._statistical_anomaly_detection(feature_matrix, timestamps)

    def _classify_anomaly_type(self, feature_values: np.ndarray) -> str:
        """Classify the type of anomaly based on feature values"""
        memory_count, api_time, cpu, memory, disk = feature_values
        
        if api_time > 1000:  # High API response time
            return AnomalyType.PERFORMANCE.value
        elif cpu > 80 or memory > 90 or disk > 95:  # High resource usage
            return AnomalyType.RESOURCE_CONSUMPTION.value
        elif memory_count > 100:  # Unusual memory growth
            return AnomalyType.GROWTH_RATE.value
        else:
            return AnomalyType.USAGE_PATTERN.value

    def _describe_anomaly(self, anomaly_values: np.ndarray, all_values: np.ndarray) -> str:
        """Generate human-readable description of the anomaly"""
        memory_count, api_time, cpu, memory, disk = anomaly_values
        
        # Calculate percentiles for comparison
        percentiles = np.percentile(all_values, [75, 90, 95], axis=0)
        
        descriptions = []
        
        if memory_count > percentiles[2][0]:  # 95th percentile
            descriptions.append(f"Extremely high memory count: {memory_count:.0f}")
        elif api_time > percentiles[1][1]:  # 90th percentile
            descriptions.append(f"High API response time: {api_time:.0f}ms")
        elif cpu > percentiles[1][2]:
            descriptions.append(f"High CPU usage: {cpu:.1f}%")
        elif memory > percentiles[1][3]:
            descriptions.append(f"High memory usage: {memory:.1f}%")
        elif disk > percentiles[1][4]:
            descriptions.append(f"High disk usage: {disk:.1f}%")
        
        return " | ".join(descriptions) if descriptions else "Unusual pattern detected"

    def _statistical_anomaly_detection(self, feature_matrix: np.ndarray, 
                                     timestamps: List[str]) -> AnomalyDetection:
        """Fallback statistical anomaly detection using z-scores"""
        anomalies = []
        anomaly_scores = []
        
        # Calculate z-scores
        means = np.mean(feature_matrix, axis=0)
        stds = np.std(feature_matrix, axis=0)
        
        threshold = 2.5  # Z-score threshold
        
        for i, values in enumerate(feature_matrix):
            z_scores = np.abs((values - means) / (stds + 1e-8))  # Add small epsilon to avoid division by zero
            max_z = np.max(z_scores)
            
            if max_z > threshold:
                anomaly_data = {
                    'timestamp': timestamps[i],
                    'type': self._classify_anomaly_type(values),
                    'score': max_z,
                    'values': values.tolist(),
                    'description': self._describe_anomaly(values, feature_matrix)
                }
                anomalies.append(anomaly_data)
                anomaly_scores.append(max_z)
        
        return AnomalyDetection(anomalies, anomaly_scores, threshold, "statistical_zscore")

    def _fallback_statistical_prediction(self, target_metric: str, horizon_days: int) -> PredictionResult:
        """Fallback prediction using simple statistical methods"""
        data = self._get_historical_data()
        
        if not data:
            return PredictionResult(
                model_type="fallback_zero",
                predictions=[0.0] * horizon_days,
                confidence_intervals=[(0.0, 0.0)] * horizon_days,
                model_accuracy=0.0,
                feature_importance={},
                forecast_horizon_days=horizon_days
            )
        
        # Extract target values
        values = [point.get(target_metric, 0) for point in data]
        
        # Simple linear trend
        if len(values) >= 2:
            x = np.arange(len(values))
            z = np.polyfit(x, values, 1)
            
            # Predict future values
            future_x = np.arange(len(values), len(values) + horizon_days)
            predictions = np.polyval(z, future_x)
            
            # Simple confidence intervals (±20%)
            confidence_intervals = [(max(0, p * 0.8), p * 1.2) for p in predictions]
            
            # Calculate simple accuracy (R-squared for linear fit)
            predicted_historical = np.polyval(z, x)
            accuracy = 1 - (np.sum((values - predicted_historical) ** 2) / 
                           (np.sum((values - np.mean(values)) ** 2) + 1e-8))
            accuracy = max(0, min(1, accuracy))
        else:
            # Constant prediction
            avg_value = np.mean(values) if values else 0
            predictions = [avg_value] * horizon_days
            confidence_intervals = [(max(0, avg_value * 0.8), avg_value * 1.2)] * horizon_days
            accuracy = 0.5
        
        return PredictionResult(
            model_type="statistical_linear",
            predictions=predictions.tolist() if hasattr(predictions, 'tolist') else predictions,
            confidence_intervals=confidence_intervals,
            model_accuracy=accuracy,
            feature_importance={'trend': 1.0},
            forecast_horizon_days=horizon_days
        )

    def generate_ai_optimization_recommendations(self) -> Dict[str, Any]:
        """Generate AI-powered optimization recommendations"""
        
        # Get predictions and anomalies
        predictions = self.generate_intelligent_predictions()
        anomalies = self.detect_anomalies()
        
        recommendations = {
            'timestamp': datetime.now().isoformat(),
            'ai_insights': [],
            'predictive_recommendations': [],
            'anomaly_based_recommendations': [],
            'system_health_score': 0.0,
            'priority_actions': []
        }
        
        # Predictive recommendations
        if predictions.model_accuracy > 0.6:
            max_predicted = max(predictions.predictions) if predictions.predictions else 0
            if max_predicted > 100:  # High growth predicted
                recommendations['predictive_recommendations'].append({
                    'type': 'capacity_scaling',
                    'priority': 'high',
                    'description': f'Predicted memory count will reach {max_predicted:.0f} in {predictions.forecast_horizon_days} days',
                    'action': 'Prepare capacity scaling and optimize memory usage',
                    'confidence': predictions.model_accuracy
                })
        
        # Anomaly-based recommendations
        if len(anomalies.anomalies) > 0:
            recent_anomalies = [a for a in anomalies.anomalies 
                              if datetime.fromisoformat(a['timestamp'].replace('Z', '+00:00')) > 
                              datetime.now() - timedelta(days=7)]
            
            if recent_anomalies:
                recommendations['anomaly_based_recommendations'].append({
                    'type': 'anomaly_investigation',
                    'priority': 'medium',
                    'description': f'{len(recent_anomalies)} anomalies detected in the last 7 days',
                    'action': 'Investigate anomaly patterns and implement monitoring',
                    'anomaly_types': list(set(a['type'] for a in recent_anomalies))
                })
        
        # AI-powered insights
        if ML_AVAILABLE and predictions.feature_importance:
            top_features = sorted(predictions.feature_importance.items(), 
                                key=lambda x: x[1], reverse=True)[:3]
            recommendations['ai_insights'].append({
                'insight_type': 'feature_importance',
                'description': 'Key factors influencing system behavior',
                'top_factors': [{'factor': f, 'importance': round(i, 3)} for f, i in top_features]
            })
        
        # Calculate system health score
        health_score = self._calculate_ai_health_score(predictions, anomalies)
        recommendations['system_health_score'] = health_score
        
        # Priority actions based on AI analysis
        if health_score < 0.7:
            recommendations['priority_actions'].append('System health requires attention - implement monitoring')
        if predictions.model_accuracy < 0.5:
            recommendations['priority_actions'].append('Collect more data for better predictions')
        if len(anomalies.anomalies) > 5:
            recommendations['priority_actions'].append('Address recurring anomalies')
        
        return recommendations

    def _calculate_ai_health_score(self, predictions: PredictionResult, 
                                 anomalies: AnomalyDetection) -> float:
        """Calculate overall system health score using AI insights"""
        score = 1.0
        
        # Prediction accuracy factor
        score *= predictions.model_accuracy
        
        # Anomaly factor
        recent_anomalies = len([a for a in anomalies.anomalies 
                              if datetime.fromisoformat(a['timestamp'].replace('Z', '+00:00')) > 
                              datetime.now() - timedelta(days=7)])
        anomaly_penalty = min(0.5, recent_anomalies * 0.1)
        score *= (1 - anomaly_penalty)
        
        # Growth stability factor
        if predictions.predictions:
            growth_variance = np.var(predictions.predictions)
            if growth_variance > 100:  # High variance indicates instability
                score *= 0.8
        
        return round(max(0.0, min(1.0, score)), 3)

    def _store_prediction(self, prediction: PredictionResult):
        """Store prediction results in database"""
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ai_predictions 
                (timestamp, model_type, prediction_horizon_days, predictions, 
                 confidence_intervals, model_accuracy, feature_importance)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                prediction.model_type,
                prediction.forecast_horizon_days,
                json.dumps(prediction.predictions),
                json.dumps(prediction.confidence_intervals),
                prediction.model_accuracy,
                json.dumps(prediction.feature_importance)
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️  Error storing prediction: {e}")

    def _store_anomalies(self, anomalies: List[Dict[str, Any]]):
        """Store detected anomalies in database"""
        try:
            conn = sqlite3.connect(self.data_path)
            cursor = conn.cursor()
            
            for anomaly in anomalies:
                cursor.execute("""
                    INSERT INTO ai_anomalies 
                    (timestamp, anomaly_type, anomaly_score, description, severity, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    anomaly['timestamp'],
                    anomaly['type'],
                    anomaly['score'],
                    anomaly['description'],
                    'medium',  # Default severity
                    json.dumps(anomaly)
                ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️  Error storing anomalies: {e}")

    def run_comprehensive_ai_analysis(self) -> Dict[str, Any]:
        """Run comprehensive AI analysis combining all Phase 5 capabilities"""
        
        print("🤖 PHASE 5: Advanced AI Integration & Predictive Analytics")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # 1. Generate predictions
        print("📈 Generating intelligent predictions...")
        predictions = self.generate_intelligent_predictions()
        
        # 2. Detect anomalies
        print("🔍 Detecting anomalies...")
        anomalies = self.detect_anomalies()
        
        # 3. Generate recommendations
        print("💡 Generating AI-powered recommendations...")
        recommendations = self.generate_ai_optimization_recommendations()
        
        # 4. Create visualizations if possible
        charts_created = []
        if PLOTTING_AVAILABLE:
            charts_created = self._create_ai_visualizations(predictions, anomalies)
        
        analysis_duration = (datetime.now() - start_time).total_seconds()
        
        results = {
            'analysis_timestamp': start_time.isoformat(),
            'analysis_duration_seconds': analysis_duration,
            'ml_available': ML_AVAILABLE,
            'plotting_available': PLOTTING_AVAILABLE,
            'predictions': {
                'model_type': predictions.model_type,
                'forecast_horizon_days': predictions.forecast_horizon_days,
                'model_accuracy': predictions.model_accuracy,
                'predictions_summary': {
                    'min': min(predictions.predictions) if predictions.predictions else 0,
                    'max': max(predictions.predictions) if predictions.predictions else 0,
                    'trend': 'increasing' if len(predictions.predictions) > 1 and 
                            predictions.predictions[-1] > predictions.predictions[0] else 'stable'
                }
            },
            'anomalies': {
                'total_detected': len(anomalies.anomalies),
                'detection_model': anomalies.detection_model,
                'recent_anomalies': len([a for a in anomalies.anomalies 
                                       if datetime.fromisoformat(a['timestamp'].replace('Z', '+00:00')) > 
                                       datetime.now() - timedelta(days=7)])
            },
            'recommendations': recommendations,
            'charts_created': charts_created,
            'system_status': {
                'health_score': recommendations['system_health_score'],
                'priority_actions_count': len(recommendations['priority_actions']),
                'ai_insights_count': len(recommendations['ai_insights'])
            }
        }
        
        # Store comprehensive results
        self._store_comprehensive_results(results)
        
        return results

    def _create_ai_visualizations(self, predictions: PredictionResult, 
                                anomalies: AnomalyDetection) -> List[str]:
        """Create AI analysis visualizations"""
        if not PLOTTING_AVAILABLE:
            return []
        
        charts_created = []
        
        try:
            # Create charts directory
            import os
            os.makedirs('growth_reports/ai_charts', exist_ok=True)
            
            # 1. Predictions chart
            if predictions.predictions:
                plt.figure(figsize=(12, 6))
                days = list(range(1, len(predictions.predictions) + 1))
                
                plt.plot(days, predictions.predictions, 'b-', linewidth=2, label='Predicted Values')
                
                # Add confidence intervals
                if predictions.confidence_intervals:
                    lower = [ci[0] for ci in predictions.confidence_intervals]
                    upper = [ci[1] for ci in predictions.confidence_intervals]
                    plt.fill_between(days, lower, upper, alpha=0.3, color='blue', label='Confidence Interval')
                
                plt.title(f'AI Predictions ({predictions.model_type}) - Accuracy: {predictions.model_accuracy:.3f}')
                plt.xlabel('Days Ahead')
                plt.ylabel('Predicted Value')
                plt.legend()
                plt.grid(True, alpha=0.3)
                
                chart_path = 'growth_reports/ai_charts/ai_predictions.png'
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                plt.close()
                charts_created.append(chart_path)
            
            # 2. Feature importance chart
            if predictions.feature_importance:
                plt.figure(figsize=(10, 6))
                features = list(predictions.feature_importance.keys())
                importance = list(predictions.feature_importance.values())
                
                plt.barh(features, importance)
                plt.title('AI Model Feature Importance')
                plt.xlabel('Importance Score')
                plt.tight_layout()
                
                chart_path = 'growth_reports/ai_charts/feature_importance.png'
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                plt.close()
                charts_created.append(chart_path)
            
            # 3. Anomaly timeline
            if anomalies.anomalies:
                plt.figure(figsize=(12, 6))
                
                timestamps = [datetime.fromisoformat(a['timestamp'].replace('Z', '+00:00')) 
                             for a in anomalies.anomalies]
                scores = [a['score'] for a in anomalies.anomalies]
                
                plt.scatter(timestamps, scores, c=scores, cmap='Reds', s=50)
                plt.colorbar(label='Anomaly Score')
                plt.title(f'Anomaly Detection Timeline ({anomalies.detection_model})')
                plt.xlabel('Timestamp')
                plt.ylabel('Anomaly Score')
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                chart_path = 'growth_reports/ai_charts/anomaly_timeline.png'
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                plt.close()
                charts_created.append(chart_path)
                
        except Exception as e:
            print(f"⚠️  Visualization error: {e}")
        
        return charts_created

    def _store_comprehensive_results(self, results: Dict[str, Any]):
        """Store comprehensive AI analysis results"""
        try:
            filename = f"growth_reports/ai_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"📄 Results saved to: {filename}")
        except Exception as e:
            print(f"⚠️  Error saving results: {e}")


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Phase 5: Advanced AI Integration & Predictive Analytics')
    parser.add_argument('--predict', action='store_true', help='Generate predictions only')
    parser.add_argument('--anomalies', action='store_true', help='Detect anomalies only')
    parser.add_argument('--recommend', action='store_true', help='Generate recommendations only')
    parser.add_argument('--comprehensive', action='store_true', help='Run comprehensive AI analysis')
    parser.add_argument('--horizon', type=int, default=90, help='Prediction horizon in days')
    
    args = parser.parse_args()
    
    # Initialize AI system
    ai_system = AdvancedAIPredictiveSystem()
    
    if args.predict:
        predictions = ai_system.generate_intelligent_predictions(horizon_days=args.horizon)
        print(f"🔮 Predictions generated: {len(predictions.predictions)} days")
        print(f"📊 Model accuracy: {predictions.model_accuracy:.3f}")
        print(f"🎯 Model type: {predictions.model_type}")
        
    elif args.anomalies:
        anomalies = ai_system.detect_anomalies()
        print(f"🚨 Anomalies detected: {len(anomalies.anomalies)}")
        print(f"🔍 Detection model: {anomalies.detection_model}")
        
    elif args.recommend:
        recommendations = ai_system.generate_ai_optimization_recommendations()
        print(f"💡 Health score: {recommendations['system_health_score']}")
        print(f"⚡ Priority actions: {len(recommendations['priority_actions'])}")
        
    else:  # Default: comprehensive analysis
        results = ai_system.run_comprehensive_ai_analysis()
        
        print("\n🎯 PHASE 5 ANALYSIS COMPLETE")
        print("=" * 40)
        print(f"⏱️  Duration: {results['analysis_duration_seconds']:.1f}s")
        print(f"🤖 ML Available: {'✅' if results['ml_available'] else '❌'}")
        print(f"📊 Health Score: {results['system_status']['health_score']}")
        print(f"🔮 Predictions: {results['predictions']['predictions_summary']['trend']}")
        print(f"🚨 Anomalies: {results['anomalies']['total_detected']} detected")
        print(f"💡 Recommendations: {results['system_status']['ai_insights_count']} insights")
        print(f"📈 Charts: {len(results['charts_created'])} created")
        
        if results['recommendations']['priority_actions']:
            print("\n🚨 PRIORITY ACTIONS:")
            for action in results['recommendations']['priority_actions']:
                print(f"  • {action}")

if __name__ == "__main__":
    main() 