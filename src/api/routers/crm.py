from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
from ..models.crm import Contact, Deal, Company
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/crm", tags=["crm"])

@router.get("/contacts", response_model=List[Contact])
def list_contacts(db: Session = Depends(get_db)):
    """Lista todos os contatos"""
    return db.query(Contact).all()

@router.post("/contacts", response_model=Contact)
def create_contact(contact: Contact, db: Session = Depends(get_db)):
    """Cria um novo contato"""
    db_contact = Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@router.get("/deals", response_model=List[Deal])
def list_deals(db: Session = Depends(get_db)):
    """Lista todas as oportunidades"""
    return db.query(Deal).all()

@router.post("/deals", response_model=Deal)
def create_deal(deal: Deal, db: Session = Depends(get_db)):
    """Cria uma nova oportunidade"""
    db_deal = Deal(**deal.dict())
    db.add(db_deal)
    db.commit()
    db.refresh(db_deal)
    return db_deal