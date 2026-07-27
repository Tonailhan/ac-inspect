# Anode Cover Inspector

AI-powered visual inspection system for anode cover quality control at Press Metal Bintulu. The system analyzes images of anode covers to detect defects and evaluate powder thickness levels.

## Features
- Upload anode cover images for automated inspection
- Binary classification: OK (standard met) or NG (defect detected)
- Confidence scoring for each inspection
- Real-time processing via REST API
- Modern web interface with drag & drop upload

## Project Structure
```
ac-inspect/
├── backend/          # FastAPI backend API
│   ├── app.py        # Main API server
│   └── requirements.txt
├── frontend/         # Next.js frontend
│   ├── app/          # Next.js app router pages
│   └── components/   # React components
├── ml/               # Model training scripts
│   ├── predict.py    # Standalone prediction script
│   ├── src/          # Training & evaluation modules
│   └── notebooks/    # Jupyter notebooks
├── weights/          # Model weight files
│   └── anode_classifier_v1.h5
├── tests/            # Test suite
└── scripts/          # Utility scripts
```

## Quick Start (Zero-Config)

We've provided automated startup scripts that handle all dependencies and environment setup automatically. You do not need to configure anything manually!

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Tonailhan/ac-inspect.git
   cd ac-inspect
   ```

2. **Run the Project**:
   - **Windows**: Double-click `start.bat` or run it in the terminal:
     ```cmd
     start.bat
     ```


*The script will automatically create virtual environments, install Python & Node dependencies, start both servers, and open your browser to `http://localhost:3000`.*

3. **Stop the Project**:
   - **Windows**: Double-click `stop.bat`


> **Note for developers**: You must have **Python 3.10+** and **Node.js (LTS)** installed on your machine. The scripts will install `pnpm` automatically if you don't have it.

## Usage

1. **Upload Image**: Drag & drop or click to upload an anode cover photo (works on PC, Mobile, and Tablet).
2. **AI Analysis**: The model analyzes the image in seconds.
3. **Get Results**: View inspection result (OK/NG) with confidence score.
4. **Technical Finding**: Review detailed findings and recommended actions.

### Mobile & Tablet Access (Plant Wi-Fi)

You can easily access this tool from any smartphone or tablet on the same Wi-Fi network:

1. Connect your phone to the **exact same Wi-Fi network or Hotspot** as the PC running this application.
2. Find the PC's IPv4 address (e.g., `192.168.1.50` or `172.20.10.2`).
3. On your phone's browser, type the address followed by `:3000` (e.g., `http://192.168.1.50:3000`).
4. Save it as a bookmark for instant access on the floor!

## Deployment

The project is designed to run locally on a workstation or a dedicated plant server.

- **Frontend**: Next.js 16 (served via Node.js). It proxies API requests automatically to the backend.
- **Backend**: FastAPI with Uvicorn. Ensure the trained model file (`.h5` or `.keras`) is placed in the `weights/` directory before starting the server.

## Technical Details

### Frontend Stack
- **Framework**: Next.js 16
- **Package Manager**: pnpm
- **UI Components**: shadcn/ui (Radix UI + Tailwind CSS)
- **Animations**: Framer Motion

### Backend Stack
- **Framework**: FastAPI
- **ASGI Server**: Uvicorn
- **Image Processing**: OpenCV, Pillow, NumPy
- **Validation**: Pydantic
- **Machine Learning**: TensorFlow / Keras (MobileNetV2)
- **API Documentation**: Automatic OpenAPI docs available at `/api/docs`

### Model
- **Task**: Binary classification (OK vs NG)
- **Input Size**: 224x224x3 RGB images
- **Output**: OK/NG with confidence score

### System Design
- **Architecture**: REST API with separate frontend/backend
- **Security**: CORS, HTTPS, input validation, security headers

**IMPORTANT**: This tool is for operational guidance only. AI-detected defects must be physically verified by a qualified technician or potline supervisor. Always follow Press Metal Bintulu Standard Operating Procedures (SOP) for maintenance tasks.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

---

**Built for Press Metal Bintulu anode cover inspection**

For questions or support, please open an issue on GitHub.
