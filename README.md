# OpenERP

Enterprise resource planning (ERP/CRM) system for small and medium businesses, developed with Python and a modern web interface.

## 🚀 Features

- **Inventory Management**: Complete control of products, stock, suppliers and raw materials
- **Bill of Materials (BOM)**: Material list management and production calculation
- **Production Planning (MRP)**: Automatic calculation of manufacturable products based on inventory
- **Financial Management**: Revenue and cost recording with expense categorization
- **Sales**: Complete sales history with real-time tracking
- **Business Intelligence**: Dashboard with KPIs, financial metrics and product analysis
- **Excel Export**: Report generation and complete data export
- **Google Sheets Integration**: Optional synchronization with Google Sheets

## 📋 Requirements

- Python 3.8 or higher
- Operating system: Windows, macOS or Linux

## 🛠️ Installation

### Installation from source code

1. Clone the repository:
```bash
git clone https://github.com/Silverx1242/OpenERP.git
cd OpenERP
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

## 📦 Download executables

You can download pre-built executables from the [Releases](https://github.com/Silverx1242/OpenERP/releases) section.

### macOS
- Download the `.dmg` or `.app.zip` file from releases
- For `.dmg`: Open the file and drag the application to the Applications folder
- For `.app.zip`: Extract and drag `OpenERP.app` to the Applications folder

## 🔧 Configuration

### Database

The application uses SQLite as the local database. The `erp_data.db` file is automatically created in the execution directory the first time the application is started.

### Google Sheets Integration (Optional)

To enable synchronization with Google Sheets:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Sheets and Google Drive APIs
4. Create a service account
5. Download the JSON credentials file
6. Save it as `service_account.json` in the project root
7. Share your Google Sheet with the service account email

## 📖 Usage

### Inventory Management

- **Add Products**: Navigate to "Inventory" and complete the form with product data
- **Product Types**:
  - `final`: Finished products for sale
  - `hijo`: Raw materials/components
  - `padre`: Sub-assemblies
  - `otro`: Other expenses or categories

### Bill of Materials (BOM)

- Define material lists for composite products
- The system automatically calculates total cost based on components
- Use production calculation (MRP) to know how many products you can manufacture

### Finance

- Record revenue and costs
- Categorize costs for better analysis
- View financial summaries in the dashboard

### Data Export

- Use the "Export to Excel" button to generate a complete file with all sections
- Files are saved in:
  - Windows/Linux: Current directory
  - macOS (from .app): `~/Documents/OpenERP/`

## 🏗️ Building from source code

### macOS

To build a `.app` executable on macOS:

```bash
# Install build dependencies
pip install pyinstaller

# Convert icon to .icns format (if necessary)
# Option 1: Use iconutil (requires .iconset)
# Option 2: Use convert (ImageMagick)

# Build the application
pyinstaller --name="OpenERP" \
  --windowed \
  --onedir \
  --icon=assets/icono.icns \
  --add-data="app/ui:app/ui" \
  --add-data="assets:assets" \
  --osx-bundle-identifier="com.openerp.erp" \
  main.py
```

### GitHub Actions

The repository includes a GitHub Actions workflow that automatically builds the application for macOS when a release tag is created:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The workflow will run automatically and generate artifacts in the Actions section.

## 📁 Project Structure

```
openerp/
├── app/
│   ├── __init__.py
│   ├── database.py          # SQLite database management
│   ├── excel_export.py      # Excel export
│   ├── g_sheets.py          # Google Sheets integration
│   └── ui/
│       └── index.html        # Web interface
├── assets/
│   ├── icono.ico           # Application icon (Windows)
│   └── icono.icns          # Application icon (macOS)
├── .github/
│   └── workflows/
│       └── build-macos.yml  # Workflow to build macOS .app
├── main.py                 # Main entry point
├── requirements.txt        # Project dependencies
├── .gitignore             # Files ignored by Git
└── README.md              # This file
```

## 🤝 Contributing

Contributions are welcome. Please:

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is under the MIT License - see the LICENSE file for more details.

## 🙏 Acknowledgments

- [pywebview](https://github.com/r0x0r/pywebview) - Framework for native web interfaces
- [openpyxl](https://openpyxl.readthedocs.io/) - Excel file manipulation
- [Tailwind CSS](https://tailwindcss.com/) - Utility CSS framework
- [Chart.js](https://www.chartjs.org/) - Interactive charts

## 📧 Contact

For questions or suggestions, open an issue in the repository.

---

Developed with ❤️ for SMEs
