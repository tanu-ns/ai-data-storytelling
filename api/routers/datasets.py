import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Dataset, Tenant
from ..dependencies import get_current_tenant
from ..services import storage, eda
from ..agents import insights as insights_agent
from ..agents import storyteller
from ..services import rag, llm_client
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/datasets", tags=["datasets"])

@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    if not tenant:
        raise HTTPException(status_code=400, detail="Tenant context required")

    dataset_id = uuid.uuid4()
    object_name = f"{tenant.id}/{dataset_id}.csv"
    
    # Upload to MinIO
    try:
        s3_path = storage.upload_file(file, object_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage error: {str(e)}")

    # Run Analysis
    analysis_result = eda.analyze_dataset(s3_path)

    # Save to DB
    new_dataset = Dataset(
        id=dataset_id,
        name=file.filename,
        file_path=s3_path,
        tenant_id=tenant.id,
        meta_info=analysis_result
    )
    db.add(new_dataset)
    db.commit()
    db.refresh(new_dataset)

    return new_dataset

@router.get("/", response_model=List[dict])
async def list_datasets(
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    if not tenant:
        raise HTTPException(status_code=400, detail="Tenant context required")
    
    datasets = db.query(Dataset).filter(Dataset.tenant_id == tenant.id).all()
    # Pydantic is stricter, but for MVP returning ORM dicts
    return [{"id": str(d.id), "name": d.name, "created_at": d.created_at} for d in datasets]

@router.get("/{dataset_id}")
async def get_dataset(
    dataset_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id, 
        Dataset.tenant_id == tenant.id
    ).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    return {
        "id": str(dataset.id),
        "name": dataset.name,
        "created_at": dataset.created_at,
        "meta_info": dataset.meta_info,
        "insights": dataset.insights,
        "story": dataset.story
    }

@router.post("/{dataset_id}/insights")
async def create_dataset_insights(
    dataset_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id, 
        Dataset.tenant_id == tenant.id
    ).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    if not dataset.meta_info:
        raise HTTPException(status_code=400, detail="Dataset not analyzed yet")

    # Generate Insights
    generated = await insights_agent.generate_insights(dataset.meta_info)
    
    dataset.insights = generated
    db.commit()
    db.refresh(dataset)
    
    # Index Insights for RAG
    try:
        texts = [f"Insight: {i['title']}. {i['description']}" for i in generated]
        metas = [{"source": "insight"} for _ in range(len(texts))]
        rag.index_text(str(dataset.id), texts, metas)
    except Exception as e:
        print(f"Indexing failed: {e}")

    return generated

@router.post("/{dataset_id}/story")
async def create_dataset_story(
    dataset_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id, 
        Dataset.tenant_id == tenant.id
    ).first()
    
    if not dataset or not dataset.insights:
        raise HTTPException(status_code=400, detail="Insights required before story generation")

    # Generate Story
    story = await storyteller.generate_story(dataset.name, dataset.insights)
    
    dataset.story = story
    db.commit()
    db.refresh(dataset)
    
    # Index Story for RAG
    try:
        # Split story by paragraphs approximately
        paragraphs = [p for p in story.split('\n\n') if p.strip()]
        metas = [{"source": "story"} for _ in range(len(paragraphs))]
        rag.index_text(str(dataset.id), paragraphs, metas)
    except Exception as e:
         print(f"Indexing failed: {e}")

    return {"story": story}

class ChatRequest(BaseModel):
    message: str

@router.post("/{dataset_id}/chat")
async def chat_dataset(
    dataset_id: uuid.UUID,
    req: ChatRequest,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id, 
        Dataset.tenant_id == tenant.id
    ).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        # RAG Retrieval
        try:
            context_docs = rag.search(str(dataset.id), req.message)
            context_str = "\n---\n".join(context_docs)
        except Exception as e:
            print(f"RAG Search failed: {e}")
            context_str = ""
        
        # LLM Generation
        client = llm_client.get_llm_client()
        
        prompt = f"""
        You are an AI assistant helping a user understand a dataset.
        
        Relevant Context from analysis:
        {context_str}
        
        User Question: {req.message}
        
        Answer the question based on the context provided. If the context doesn't have the answer, use your general knowledge but mention that the specific data wasn't found in the index.
        """
        
        answer = await client.generate(prompt)
        return {"response": answer}
    except Exception as e:
        print(f"Chat Endpoint Error: {e}")
        return {"response": "I encountered an error processing your request. Please try again."}
