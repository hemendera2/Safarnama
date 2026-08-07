# Safarnama 🗺️ - India's Travel Knowledge Graph

Safarnama is a professional-grade travel intelligence platform that structures India's offbeat travel data into a **Knowledge Graph**.

## 🧠 Knowledge Graph Architecture
Unlike standard travel databases, Safarnama treats every destination as a node in a massive travel graph:
- **Nodes**: Places, Lakes, Waterfalls, Trails, Villages, and Activity Hubs.
- **Edges (Relationships)**: 
  - `Near`: Geospatial proximity edges.
  - `Recommended Together`: Curated multi-stop intelligence.
  - `Alternative`: Smart discovery of less-crowded hidden gems.
  - `Connected Route`: Structural routing data for itineraries.

## 🌟 Product Differentiators
- **Intelligent Discovery**: The discovery engine uses graph weights and seasonal signals to recommend the best hidden alternatives.
- **Advanced Metadata**: Rich destination intelligence including history, interesting facts, and infrastructure status (Parking, Network, Safety).
- **Geospatial Intelligence**: Radius search and bounding-box optimizations ready for PostGIS scaling.
- **Trust & Provenance**: Data is assigned a confidence score and source attribution, ensuring a verified discovery experience.
- **Operational Excellence**: >90% backend coverage, structured JSON logging, and a robust deduplication ingestion pipeline.

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.11+
- Virtual Environment

### 2. Installation
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Initialize Knowledge Graph
```bash
export PYTHONPATH=$PYTHONPATH:.
alembic upgrade head
python3 src/db/seed_v2.py
```

### 4. Run API
```bash
export PYTHONPATH=$PYTHONPATH:.
python3 main.py
```

## 🛠️ Tech Stack
- **Backend**: Python 3.11, Flask, SQLAlchemy 2.0 (Relational + Graph model).
- **Security**: JWT Auth, RBAC, Talisman, Rate Limiting.
- **DevOps**: Alembic, Pytest, Prometheus, Structured Logging.
