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
├── ml/               # Model training and evaluation
│   ├── predict.py    # Standalone prediction script
│   ├── train_mobilenet_v2_100epochs.py
│   ├── src/          # Training & evaluation modules
│   └── notebooks/    # Jupyter notebooks
├── weights/          # Model weight files
│   └── anode_mobilenet_v2.keras
├── tests/            # Test suite
└── docs/             # Architecture, API reference, validation study
```

## Requirements

| Requirement | Version | Note |
|---|---|---|
| Python | **3.10 – 3.12** | TensorFlow 2.16 does not support Python 3.13 or newer |
| Node.js | LTS | `pnpm` is installed automatically if missing |

> **Python version matters.** If `python --version` reports 3.13 or later, the
> TensorFlow install will fail and the backend will start but return HTTP 503 on
> every inspection. Install Python 3.12 and make sure it is the one on your PATH.

## Quick Start (Zero-Config)

We've provided automated startup scripts that handle all dependencies and environment setup automatically. You do not need to configure anything manually!

1. **Get the code** — either clone the repository:
   ```bash
   git clone https://github.com/Tonailhan/ac-inspect.git
   cd ac-inspect
   ```
   …or unzip the project folder if it was sent to you directly.

   > If you are **sending** this project as a zip, exclude `backend/venv312/` and
   > `frontend/node_modules/`. They are machine-specific and add gigabytes;
   > `start.bat` recreates both on first run.

2. **Run the Project**:
   - **Windows**: Double-click `start.bat` or run it in the terminal:
     ```cmd
     start.bat
     ```


*The script will automatically create virtual environments, install Python & Node dependencies, start both servers, and open your browser to `http://localhost:3000`.*

3. **Stop the Project**:
   - **Windows**: Double-click `stop.bat`


> **Note for developers**: You must have **Python 3.10–3.12** and **Node.js (LTS)**
> installed on your machine. The scripts will install `pnpm` automatically if you
> don't have it. First run downloads TensorFlow (~600 MB) and the Node packages,
> so it needs an internet connection and several minutes; subsequent runs start
> offline in seconds.

### If inspections return an error

The backend starts even when the model cannot be loaded, so that the failure is
visible rather than silent. Check `http://localhost:5001/api/health`:

- `"model_loaded": true` — the model is fine; the problem is elsewhere.
- `"model_loaded": false` — TensorFlow or the weights file failed to load. The
  usual cause is an unsupported Python version (see Requirements above). If the
  environment was created by an older version of `start.bat`, delete
  `backend\venv312` and run it again; otherwise re-run the install by hand to
  see the full error:

  ```cmd
  cd backend
  venv312\Scripts\python.exe -m pip install -r requirements.txt
  ```

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
