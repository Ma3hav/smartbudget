# 🏦 SmartBudget - AI-Powered Expense Tracking System

![SmartBudget Logo](frontend/assets/logo.png)

A comprehensive expense tracking and budget management application powered by Machine Learning for intelligent financial insights and predictions.

## ✨ Features

### Core Features
- 📊 **Expense Tracking** - Track all your expenses with detailed categorization
- 💰 **Budget Management** - Set and monitor monthly budgets per category
- 🎯 **Savings Goals** - Create and track financial goals with progress monitoring
- 📈 **Visual Analytics** - Interactive charts and graphs for spending insights
- 🔔 **Smart Alerts** - Budget warnings and anomaly detection notifications

### AI/ML Features
- 🤖 **Expense Prediction** - ML-powered forecasting of future expenses
- 🔍 **Anomaly Detection** - Automatic detection of unusual spending patterns
- 💡 **Smart Insights** - Personalized recommendations based on spending habits
- 📊 **Trend Analysis** - Identify spending patterns and trends over time
- 🎯 **Budget Optimization** - AI-suggested budget allocations using 50/30/20 rule

## 🏗️ Architecture

### Technology Stack

**Backend:**
- Flask 3.0.0 (Python web framework)
- MongoDB (Database)
- JWT (Authentication)
- Scikit-learn (Machine Learning)
- Pandas & NumPy (Data processing)

**Frontend:**
- HTML5, CSS3, JavaScript (ES6+)
- Chart.js (Data visualization)
- Responsive design with CSS Grid/Flexbox

**Machine Learning:**
- Gradient Boosting Regressor for expense forecasting
- Z-score based anomaly detection
- Statistical analysis for insights generation

## 📁 Project Structure

```
SmartBudget/
├── backend/
│   ├── app.py                 # Flask application factory
│   ├── config.py              # Configuration settings
│   ├── init_db.py             # Database initialization
│   ├── models/                # Data models
│   │   ├── user_model.py
│   │   ├── expense_model.py
│   │   ├── category_model.py
│   │   ├── alert_model.py
│   │   └── savings_model.py
│   ├── routes/                # API endpoints
│   │   ├── auth_routes.py
│   │   ├── expense_routes.py
│   │   ├── category_routes.py
│   │   ├── alert_routes.py
│   │   ├── savings_routes.py
│   │   └── ml_routes.py
│   ├── services/              # Business logic
│   │   ├── auth_service.py
│   │   ├── expense_service.py
│   │   ├── category_service.py
│   │   ├── alert_service.py
│   │   └── savings_service.py
│   ├── ml/                    # Machine Learning modules
│   │   ├── forecasting.py
│   │   ├── anomaly_detection.py
│   │   └── insights.py
│   └── utils/                 # Utilities
│       ├── db_connection.py
│       ├── jwt_utils.py
│       └── validation.py
├── frontend/
│   ├── index.html             # Login/Signup page
│   ├── dashboard.html         # Main dashboard
│   ├── add_expense.html       # Add expense form
│   ├── insights.html          # ML insights page
│   ├── goals.html             # Savings goals page
│   ├── css/                   # Stylesheets
│   │   ├── theme.css
│   │   ├── style.css
│   │   └── dashboard.css
│   └── js/                    # JavaScript files
│       ├── api.js
│       ├── auth.js
│       ├── chart.js
│       ├── expense.js
│       └── insights.js
├── tests/                     # Test files
├── docs/                      # Documentation & diagrams
├── run.py                     # Application entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- MongoDB 4.4+
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/smartbudget.git
cd smartbudget
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 4: Configure Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your configuration
# Update MongoDB URI, secret keys, etc.
```

### Step 5: Initialize Database
```bash
python backend/init_db.py
```

This will:
- Create necessary collections
- Set up indexes
- Create default admin and demo users

**Default Users:**
- Admin: `admin@smartbudget.com` / `Admin@123`
- Demo: `demo@smartbudget.com` / `Demo@123`

### Step 6: Train ML Model (Optional)
```bash
python backend/ml/train_model.py
```

### Step 7: Start the Server
```bash
python run.py
```

The API will be available at `http://localhost:5000`

### Step 8: Open Frontend
Open `frontend/index.html` in your browser or use a local server:

```bash
# Using Python's built-in server
cd frontend
python -m http.server 5500

# Then visit http://localhost:5500
```

## 🔌 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "Password@123"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "Password@123"
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <token>
```

### Expense Endpoints

#### Create Expense
```http
POST /api/expenses/
Authorization: Bearer <token>
Content-Type: application/json

{
  "amount": 45.50,
  "category": "Food",
  "payment_type": "Credit Card",
  "date": "2024-11-27T12:00:00Z",
  "notes": "Lunch at cafe",
  "tags": ["lunch", "restaurant"]
}
```

#### Get Expenses
```http
GET /api/expenses/?page=1&limit=50
Authorization: Bearer <token>
```

Query Parameters:
- `page` - Page number (default: 1)
- `limit` - Items per page (default: 50)
- `category` - Filter by category
- `start_date` - Start date (ISO format)
- `end_date` - End date (ISO format)
- `min_amount` - Minimum amount
- `max_amount` - Maximum amount

#### Get Statistics
```http
GET /api/expenses/statistics
Authorization: Bearer <token>
```

### ML Endpoints

#### Get Expense Forecast
```http
GET /api/ml/forecast
Authorization: Bearer <token>
```

Returns 30-day expense predictions with confidence intervals.

#### Detect Anomalies
```http
GET /api/ml/anomalies?monthly_budget=3000
Authorization: Bearer <token>
```

#### Get Insights
```http
GET /api/ml/insights
Authorization: Bearer <token>
```

#### Financial Health Score
```http
GET /api/ml/financial-health?income=5000&savings=10000
Authorization: Bearer <token>
```

### Category Endpoints

#### Create Category
```http
POST /api/categories/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Coffee",
  "icon": "coffee",
  "color": "#A52A2A",
  "budget_limit": 100
}
```

### Savings Goals Endpoints

#### Create Goal
```http
POST /api/savings/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Emergency Fund",
  "target_amount": 10000,
  "deadline": "2025-12-31T00:00:00Z",
  "description": "Build 6-month emergency fund"
}
```

#### Add Savings
```http
POST /api/savings/<goal_id>/transaction
Authorization: Bearer <token>
Content-Type: application/json

{
  "action": "add",
  "amount": 500,
  "notes": "Monthly savings"
}
```

## 🧪 Testing

### Run Unit Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_expense_logic.py -v
```

### Test with Coverage
```bash
pytest tests/ --cov=backend --cov-report=html
```

### API Testing
Use the provided `tests/test_api.http` file with REST Client extension in VS Code.

## 🤖 Machine Learning Models

### Expense Forecasting
- **Algorithm:** Gradient Boosting Regressor
- **Features:** Day of week, day of month, month, rolling averages, lag features
- **Output:** 30-day expense predictions with confidence intervals
- **Training:** Automatically retrains with new data

### Anomaly Detection
- **Method:** Z-score statistical analysis
- **Detects:** 
  - Unusual transaction amounts
  - Category spending anomalies
  - Transaction frequency anomalies
  - Budget overrun risks

### Insights Generation
- **Analysis Types:**
  - Spending patterns by day/time
  - Category-wise breakdown
  - Saving opportunities
  - Budget recommendations (50/30/20 rule)
  - Financial health scoring

## 📊 Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  email: String (unique),
  name: String,
  password_hash: String,
  profile: {
    monthly_income: Number,
    monthly_budget: Number,
    currency: String,
    timezone: String
  },
  settings: {
    email_notifications: Boolean,
    budget_alerts: Boolean,
    weekly_reports: Boolean,
    theme: String
  },
  created_at: DateTime,
  updated_at: DateTime
}
```

### Expenses Collection
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  amount: Number,
  category: String,
  payment_type: String,
  date: DateTime,
  notes: String,
  tags: [String],
  receipt_url: String,
  created_at: DateTime,
  updated_at: DateTime
}
```

### Categories Collection
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  name: String,
  icon: String,
  color: String,
  budget_limit: Number,
  is_default: Boolean,
  created_at: DateTime,
  updated_at: DateTime
}
```

### Savings Goals Collection
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  title: String,
  target_amount: Number,
  saved_amount: Number,
  deadline: DateTime,
  description: String,
  priority: String,
  status: String,
  created_at: DateTime,
  updated_at: DateTime,
  completed_at: DateTime
}
```

### Alerts Collection
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  alert_type: String,
  title: String,
  message: String,
  priority: String,
  is_read: Boolean,
  metadata: Object,
  created_at: DateTime,
  read_at: DateTime
}
```

## 🔒 Security Features

- **JWT Authentication** - Secure token-based authentication
- **Password Hashing** - Werkzeug secure password hashing
- **Input Validation** - Marshmallow schema validation
- **SQL Injection Protection** - MongoDB parameterized queries
- **CORS Configuration** - Controlled cross-origin access
- **Rate Limiting** - API endpoint protection

## 🎨 UI/UX Features

- **Responsive Design** - Mobile-first approach
- **Dark Theme** - Cherry red color scheme
- **Interactive Charts** - Real-time data visualization
- **Progressive Enhancement** - Works without JavaScript
- **Accessibility** - WCAG 2.1 compliant
- **Fast Loading** - Optimized assets

## 🚧 Development Roadmap

### Phase 1 (Current)
- ✅ Core expense tracking
- ✅ Budget management
- ✅ ML-powered forecasting
- ✅ Anomaly detection
- ✅ Smart insights

### Phase 2 (Planned)
- [ ] Receipt OCR scanning
- [ ] Bank account integration
- [ ] Multi-currency support
- [ ] Recurring expense automation
- [ ] Export to Excel/PDF
- [ ] Email/SMS notifications
- [ ] Mobile app (React Native)

### Phase 3 (Future)
- [ ] Investment tracking
- [ ] Tax planning assistance
- [ ] Bill payment reminders
- [ ] Collaborative budgets (family/team)
- [ ] Advanced ML models (LSTM/Transformers)
- [ ] Voice assistant integration

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards
- Follow PEP 8 for Python code
- Use ESLint for JavaScript
- Write unit tests for new features
- Update documentation

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- Flask documentation and community
- Scikit-learn for ML algorithms
- Chart.js for beautiful visualizations
- MongoDB for flexible data storage
- All contributors and testers

---

**Made with ❤️ by SmartBudget Team**