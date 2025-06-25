from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from sqlalchemy.orm import Session, sessionmaker
from models import Business, engine
from schemas import BusinessCreate, BusinessUpdate, BusinessResponse, TrainRequest, RecommendationResponse
from recommender import AutoMLRecommender, load_off_dataset_light
import os
import shutil
import pickle
import logging
from datetime import datetime

router = APIRouter(prefix="/businesses", tags=["businesses"])
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def setup_business_logger(business_id: int):
    logger = logging.getLogger(f"business_{business_id}")
    logger.setLevel(logging.INFO)
    project_dir = f"projects/{business_id}"
    log_file = f"{project_dir}/logs.txt"
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger


@router.post("/", response_model=BusinessResponse)
async def create_business(business: BusinessCreate, db: Session = Depends(get_db)):
    db_business = Business(**business.dict())
    db.add(db_business)
    db.commit()
    db.refresh(db_business)

    project_dir = f"projects/{db_business.id}"
    os.makedirs(project_dir, exist_ok=True)

    logger = setup_business_logger(db_business.id)
    logger.info(f"Business created: {business.name}")

    return db_business


@router.put("/{business_id}", response_model=BusinessResponse)
async def update_business(business_id: int, business: BusinessUpdate, db: Session = Depends(get_db)):
    db_business = db.query(Business).filter(Business.id == business_id).first()
    if not db_business:
        raise HTTPException(status_code=404, detail="Business not found")

    update_data = business.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_business, key, value)

    db.commit()
    db.refresh(db_business)

    logger = setup_business_logger(business_id)
    logger.info(f"Business updated: {update_data}")

    return db_business


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(business_id: int, db: Session = Depends(get_db)):
    db_business = db.query(Business).filter(Business.id == business_id).first()
    if not db_business:
        raise HTTPException(status_code=404, detail="Business not found")
    return db_business


@router.delete("/{business_id}", response_model=dict)
async def delete_business(business_id: int, db: Session = Depends(get_db)):
    db_business = db.query(Business).filter(Business.id == business_id).first()
    if not db_business:
        raise HTTPException(status_code=404, detail="Business not found")

    db.delete(db_business)
    db.commit()

    project_dir = f"projects/{business_id}"
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)

    return {"status": "business deleted"}


@router.get("/", response_model=list[BusinessResponse])
async def list_businesses(db: Session = Depends(get_db)):
    businesses = db.query(Business).all()
    return businesses


@router.get("/{business_id}/status", response_model=dict)
async def get_business_status(business_id: int, db: Session = Depends(get_db)):
    db_business = db.query(Business).filter(Business.id == business_id).first()
    if not db_business:
        raise HTTPException(status_code=404, detail="Business not found")

    status = {
        "business_id": business_id,
        "name": db_business.name,
        "has_data": os.path.exists(f"projects/{business_id}/data.jsonl.gz"),
        "has_model": os.path.exists(f"projects/{business_id}/model.pkl")
    }
    return status


@router.delete("/{business_id}/data", response_model=dict)
async def clear_business_data(business_id: int, db: Session = Depends(get_db)):
    db_business = db.query(Business).filter(Business.id == business_id).first()
    if not db_business:
        raise HTTPException(status_code=404, detail="Business not found")

    project_dir = f"projects/{business_id}"
    data_path = f"{project_dir}/data.jsonl.gz"
    model_path = f"{project_dir}/model.pkl"

    deleted_files = []
    if os.path.exists(data_path):
        os.remove(data_path)
        deleted_files.append("data.jsonl.gz")
    if os.path.exists(model_path):
        os.remove(model_path)
        deleted_files.append("model.pkl")

    logger = setup_business_logger(business_id)
    logger.info(f"Business data cleared: {deleted_files}")

    return {"status": "data cleared", "deleted_files": deleted_files}


@router.post("/{business_id}/upload-data")
async def upload_data(business_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    db_business = db.query(Business).filter(Business.id == business_id).first()
    if not db_business:
        raise HTTPException(status_code=404, detail="Business not found")

    project_dir = f"projects/{business_id}"
    file_path = f"{project_dir}/data.jsonl.gz"

    logger = setup_business_logger(business_id)

    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        logger.info(f"Data uploaded: {file.filename}")
    except Exception as e:
        logger.error(f"Data upload error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Data upload error: {str(e)}")

    return {"status": "data uploaded", "file_path": file_path}


@router.post("/{business_id}/train", response_model=dict)
async def train_model(business_id: int, req: TrainRequest, db: Session = Depends(get_db)):
    db_business = db.query(Business).filter(Business.id == business_id).first()
    if not db_business:
        raise HTTPException(status_code=404, detail="Business not found")

    data_path = f"projects/{business_id}/data.jsonl.gz"
    if not os.path.exists(data_path):
        raise HTTPException(
            status_code=400, detail="No data uploaded for this business")

    logger = setup_business_logger(business_id)

    try:
        tab, text, labels, df = load_off_dataset_light(
            data_path, n_samples=req.n_samples)
    except Exception as e:
        logger.error(f"Data loading error: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Data loading error: {str(e)}")

    try:
        if req.use_tabular and (tab is None or len(tab) == 0):
            raise ValueError("Нет табличных данных для обучения")
        if req.use_text and (text is None or len(text) == 0):
            raise ValueError("Нет текстовых данных для обучения")
        mm = AutoMLRecommender(
            use_tabular=req.use_tabular, use_text=req.use_text)
        mm.fit(
            tabular=tab if req.use_tabular else None,
            text=text if req.use_text else None,
            y=labels,
            n_neighbors=req.n_neighbors
        )
    except Exception as e:
        logger.error(f"Training error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Training error: {str(e)}")

    model_path = f"projects/{business_id}/model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump({"model": mm, "df": df, "labels": labels}, f)

    logger.info(
        f"Model trained: n_samples={req.n_samples}, modalities={req.use_tabular, req.use_text}")

    return {"status": "trained", "items_loaded": len(df), "modalities": {"tabular": req.use_tabular, "text": req.use_text}}


@router.get("/{business_id}/recommend/{item_idx}", response_model=RecommendationResponse)
async def get_recommendations(business_id: int, item_idx: int, k: int = 5, db: Session = Depends(get_db)):
    db_business = db.query(Business).filter(Business.id == business_id).first()
    if not db_business:
        raise HTTPException(status_code=404, detail="Business not found")

    model_path = f"projects/{business_id}/model.pkl"
    if not os.path.exists(model_path):
        raise HTTPException(status_code=400, detail="Model not trained yet")

    logger = setup_business_logger(business_id)

    try:
        with open(model_path, "rb") as f:
            data = pickle.load(f)
            mm = data["model"]
            df = data["df"]

        if item_idx < 0 or item_idx >= len(df):
            raise HTTPException(status_code=404, detail="Invalid item index")

        rec_idx = mm.recommend(item_idx, k=k)
        recs = [{"index": int(i), "product_name": df.loc[i, 'product_name']}
                for i in rec_idx]
    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Recommendation error: {str(e)}")

    return {"query_index": item_idx, "product_name": df.loc[item_idx, 'product_name'], "recommendations": recs}


@router.get("/{business_id}/items", response_model=list[dict])
async def list_items(business_id: int, limit: int = 20, db: Session = Depends(get_db)):
    db_business = db.query(Business).filter(Business.id == business_id).first()
    if not db_business:
        raise HTTPException(status_code=404, detail="Business not found")

    model_path = f"projects/{business_id}/model.pkl"
    if not os.path.exists(model_path):
        raise HTTPException(status_code=400, detail="No data loaded")

    with open(model_path, "rb") as f:
        df = pickle.load(f)["df"]

    return [{"index": int(i), "product_name": v} for i, v in zip(df.index[:limit], df['product_name'][:limit])]


@router.get("/{business_id}/metrics", response_model=dict)
async def get_metrics(business_id: int, k: int = 5, db: Session = Depends(get_db)):
    db_business = db.query(Business).filter(Business.id == business_id).first()
    if not db_business:
        raise HTTPException(status_code=404, detail="Business not found")

    model_path = f"projects/{business_id}/model.pkl"
    if not os.path.exists(model_path):
        raise HTTPException(status_code=400, detail="Model not trained yet")

    logger = setup_business_logger(business_id)

    try:
        with open(model_path, "rb") as f:
            data = pickle.load(f)
            mm = data["model"]
            labels = data["labels"]

        d, idxs = mm.nn.kneighbors(mm.X_, n_neighbors=k+1)
        idxs = idxs[:, 1:]
        p = mm.precision_at_k(labels, idxs, k=k)
        r = mm.recall_at_k(labels, idxs, k=k)
        mapk = mm.map_at_k(labels, idxs, k=k)
        mrrk = mm.mrr_at_k(labels, idxs, k=k)
        div = mm.diversity_at_k(idxs, k=k)
    except Exception as e:
        logger.error(f"Metrics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Metrics error: {str(e)}")

    return {
        "precision_at_k": float(p),
        "recall_at_k": float(r),
        "map_at_k": float(mapk),
        "mrr_at_k": float(mrrk),
        "diversity_at_k": float(div),
        "k": k
    }
