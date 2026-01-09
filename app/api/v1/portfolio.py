from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.api import dependencies
from app.core.security import verify_firebase_token
from app.models.portfolio import Portfolio
from app.schemas.portfolio import PortfolioUpdate

router = APIRouter()

#PRIVATE ROUTES (Requires Google Login)

@router.get("/me", response_model=List[Portfolio])
async def get_my_portfolios(
    db: Session = Depends(dependencies.get_db),
    current_user: dict = Depends(verify_firebase_token)
):
    user_id = current_user.get("uid")
    statement = (
        select(Portfolio)
        .where(Portfolio.user_id == user_id)
        .order_by(Portfolio.created_at.desc())
    )
    results = db.exec(statement).all()
    return results

@router.get("/{job_id}", response_model=Portfolio)
async def get_portfolio_by_job(
    job_id: str,
    db: Session = Depends(dependencies.get_db),
    # Relaxed auth for demo polling
    # current_user: dict = Depends(verify_firebase_token)
):

    statement = select(Portfolio).where(Portfolio.job_id == job_id)
    portfolio = db.exec(statement).first()

    if not portfolio:
        raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND, 
            detail="Portfolio not found."
        )
    
    # Validation logic skipped for demo to allow guest access via UUID
    # if portfolio.user_id != current_user.get("uid"):
    #     raise HTTPException(...)

    return portfolio

@router.patch("/{job_id}/publish", response_model=Portfolio)
async def update_portfolio_settings(
    job_id: str,
    update_data: PortfolioUpdate,
    db: Session = Depends(dependencies.get_db),
    current_user: dict = Depends(verify_firebase_token)
):
    statement = select(Portfolio).where(Portfolio.job_id == job_id)
    db_portfolio = db.exec(statement).first()

    if not db_portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found.")
    
    if db_portfolio.user_id != current_user.get("uid"):
        raise HTTPException(
            status_code=403, 
            detail="Unauthorized to update this portfolio."
        )

    obj_data = update_data.model_dump(exclude_unset=True)
    for key, value in obj_data.items():
        setattr(db_portfolio, key, value)

    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

#PUBLIC ROUTES (No Login Required)

@router.get("/public/{slug}", response_model=Portfolio)
async def get_public_portfolio(
    slug: str,
    db: Session = Depends(dependencies.get_db)
):
    statement = select(Portfolio).where(
        Portfolio.slug == slug,
        Portfolio.is_published == True
    )
    portfolio = db.exec(statement).first()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Portfolio not found or is currently private."
        )
    return portfolio
