from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.core.config import settings
from app.core.security import hash_password, verify_password, create_token
from app.core.deps import current_user, roles
from app.db.base import Base
from app.db.session import engine, get_db
from app.models import User, HotspotReport, CollectionJob, MarketListing, SaleOffer
from app.schemas.common import RegisterIn, LoginIn, UserOut, ReportIn, ReportStatusIn, ListingIn, OfferIn, OfferStatusIn

app = FastAPI(title="TakaLink API", version="1.0.0", description="Waste reporting, collection coordination and recycling marketplace API")
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin], allow_credentials=True, allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])
Base.metadata.create_all(bind=engine)
COOKIE_NAME = "takalink_session"
def set_session(response: Response, token: str):
    response.set_cookie(COOKIE_NAME, token, httponly=True, secure=settings.cookie_secure, samesite=settings.cookie_samesite, max_age=settings.token_expire_minutes*60, path="/")
def public_report(r):
    return {"id":r.id,"title":r.title,"description":r.description,"waste_type":r.waste_type,"severity":r.severity,"status":r.status,"latitude":r.latitude,"longitude":r.longitude,"image_url":r.image_url,"estimated_kg":r.estimated_kg,"actual_kg":r.actual_kg,"created_by":r.created_by,"assigned_to":r.assigned_to,"created_at":r.created_at.isoformat() if r.created_at else None}
def public_listing(x):
    return {"id":x.id,"title":x.title,"material":x.material,"description":x.description,"price_per_kg":x.price_per_kg,"min_kg":x.min_kg,"location":x.location,"buyer_id":x.buyer_id,"buyer_name":x.buyer.name if x.buyer else "Buyer","active":x.active,"created_at":x.created_at.isoformat() if x.created_at else None}
def public_offer(o):
    return {"id":o.id,"listing_id":o.listing_id,"listing_title":o.listing.title if o.listing else "Listing","seller_id":o.seller_id,"seller_name":o.seller.name if o.seller else "Seller","buyer_id":o.listing.buyer_id if o.listing else None,"quantity_kg":o.quantity_kg,"proposed_price_per_kg":o.proposed_price_per_kg,"status":o.status,"notes":o.notes,"created_at":o.created_at.isoformat() if o.created_at else None}
@app.get("/health")
def health(): return {"status":"ok","service":"takalink-api"}
@app.get("/")
def root(): return {"name":"TakaLink API","docs":"/docs","health":"/health"}

@app.post("/api/auth/register", response_model=UserOut, status_code=201)
def register(data: RegisterIn, response: Response, db: Session=Depends(get_db)):
    email=data.email.lower().strip()
    if db.scalar(select(User).where(User.email==email)): raise HTTPException(409,"An account with this email already exists")
    user=User(name=data.name.strip(),email=email,password_hash=hash_password(data.password),role=data.role,phone=data.phone,organization=data.organization,service_area=data.service_area)
    db.add(user); db.commit(); db.refresh(user); set_session(response,create_token(user.id,user.role)); return user
@app.post("/api/auth/login", response_model=UserOut)
def login(data: LoginIn, response: Response, db: Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.email==data.email.lower().strip()))
    if not user or not verify_password(data.password,user.password_hash): raise HTTPException(401,"Incorrect email or password")
    if not user.active: raise HTTPException(403,"This account is suspended")
    set_session(response,create_token(user.id,user.role)); return user
@app.post("/api/auth/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME,path="/",secure=settings.cookie_secure,httponly=True,samesite=settings.cookie_samesite); return {"message":"Logged out"}
@app.get("/api/auth/me", response_model=UserOut)
def me(user: User=Depends(current_user)): return user

@app.get("/api/reports")
def list_reports(status_filter: str|None=None, db: Session=Depends(get_db)):
    q=select(HotspotReport).order_by(HotspotReport.created_at.desc())
    if status_filter: q=q.where(HotspotReport.status==status_filter)
    return [public_report(r) for r in db.scalars(q.limit(500)).all()]
@app.post("/api/reports", status_code=201)
def create_report(data: ReportIn, db: Session=Depends(get_db), user: User=Depends(current_user)):
    r=HotspotReport(**data.model_dump(),created_by=user.id); db.add(r); db.flush(); db.add(CollectionJob(report_id=r.id)); db.commit(); db.refresh(r); return public_report(r)
@app.get("/api/reports/{report_id}")
def get_report(report_id:int, db:Session=Depends(get_db)):
    r=db.get(HotspotReport,report_id)
    if not r: raise HTTPException(404,"Report not found")
    return public_report(r)
@app.patch("/api/reports/{report_id}")
def update_report(report_id:int,data:ReportStatusIn,db:Session=Depends(get_db),user:User=Depends(current_user)):
    r=db.get(HotspotReport,report_id)
    if not r: raise HTTPException(404,"Report not found")
    if user.role!="admin" and r.created_by!=user.id and r.assigned_to!=user.id: raise HTTPException(403,"Only the reporter, assigned collector or admin can update this report")
    if data.status=="verified" and user.role!="admin": raise HTTPException(403,"Only an admin can verify a collection")
    if data.status=="claimed" and user.role!="collector" and user.role!="admin": raise HTTPException(403,"Only collectors can claim reports")
    r.status=data.status; db.commit(); db.refresh(r); return public_report(r)

@app.get("/api/jobs")
def list_jobs(db:Session=Depends(get_db),user:User=Depends(current_user)):
    q=select(CollectionJob).order_by(CollectionJob.id.desc())
    if user.role=="collector": q=q.where((CollectionJob.status=="open")|(CollectionJob.collector_id==user.id))
    elif user.role not in ("admin",): q=q.join(HotspotReport).where(HotspotReport.created_by==user.id)
    return [{"id":j.id,"report_id":j.report_id,"report":public_report(j.report),"collector_id":j.collector_id,"status":j.status,"actual_kg":j.actual_kg,"proof_image_url":j.proof_image_url,"notes":j.notes} for j in db.scalars(q).all()]
@app.post("/api/jobs/{job_id}/claim")
def claim_job(job_id:int,db:Session=Depends(get_db),user:User=Depends(roles("collector","admin"))):
    j=db.get(CollectionJob,job_id)
    if not j: raise HTTPException(404,"Job not found")
    if j.status!="open" and j.collector_id!=user.id: raise HTTPException(409,"This job is no longer available")
    j.collector_id=user.id; j.status="claimed"; j.claimed_at=datetime.now(timezone.utc); j.report.status="claimed"; j.report.assigned_to=user.id; db.commit(); return {"message":"Job claimed","job_id":j.id,"status":j.status}
@app.post("/api/jobs/{job_id}/proof")
def submit_proof(job_id:int,payload:dict,db:Session=Depends(get_db),user:User=Depends(roles("collector","admin"))):
    j=db.get(CollectionJob,job_id)
    if not j: raise HTTPException(404,"Job not found")
    if user.role!="admin" and j.collector_id!=user.id: raise HTTPException(403,"Only the assigned collector can submit proof")
    kg=payload.get("actual_kg")
    if kg is None or not isinstance(kg,(int,float)) or kg<0: raise HTTPException(422,"actual_kg must be a non-negative number")
    j.actual_kg=float(kg); j.proof_image_url=payload.get("proof_image_url"); j.notes=payload.get("notes"); j.material_breakdown=str(payload.get("material_breakdown") or ""); j.status="collected"; j.completed_at=datetime.now(timezone.utc); j.report.actual_kg=float(kg); j.report.status="collected"; db.commit(); return {"message":"Proof submitted for review","status":j.status,"actual_kg":j.actual_kg}

@app.get("/api/listings")
def list_listings(material:str|None=None,db:Session=Depends(get_db)):
    q=select(MarketListing).where(MarketListing.active==True).order_by(MarketListing.created_at.desc())
    if material: q=q.where(MarketListing.material.ilike(f"%{material}%"))
    return [public_listing(x) for x in db.scalars(q.limit(500)).all()]
@app.post("/api/listings",status_code=201)
def create_listing(data:ListingIn,db:Session=Depends(get_db),user:User=Depends(roles("buyer","admin"))):
    x=MarketListing(**data.model_dump(),buyer_id=user.id); db.add(x); db.commit(); db.refresh(x); return public_listing(x)
@app.get("/api/listings/{listing_id}")
def get_listing(listing_id:int,db:Session=Depends(get_db)):
    x=db.get(MarketListing,listing_id)
    if not x: raise HTTPException(404,"Listing not found")
    return public_listing(x)
@app.post("/api/offers",status_code=201)
def create_offer(data:OfferIn,db:Session=Depends(get_db),user:User=Depends(roles("producer","collector","admin"))):
    listing=db.get(MarketListing,data.listing_id)
    if not listing or not listing.active: raise HTTPException(404,"Active listing not found")
    if listing.buyer_id==user.id: raise HTTPException(400,"You cannot make an offer on your own listing")
    if data.quantity_kg<listing.min_kg: raise HTTPException(422,f"Minimum quantity is {listing.min_kg} kg")
    o=SaleOffer(**data.model_dump(),seller_id=user.id); db.add(o); db.commit(); db.refresh(o); return public_offer(o)
@app.get("/api/offers/mine")
def my_offers(db:Session=Depends(get_db),user:User=Depends(current_user)):
    q=select(SaleOffer).join(MarketListing).where((SaleOffer.seller_id==user.id)|(MarketListing.buyer_id==user.id)).order_by(SaleOffer.created_at.desc())
    return [public_offer(o) for o in db.scalars(q).all()]
@app.patch("/api/offers/{offer_id}")
def update_offer(offer_id:int,data:OfferStatusIn,db:Session=Depends(get_db),user:User=Depends(current_user)):
    o=db.get(SaleOffer,offer_id)
    if not o: raise HTTPException(404,"Offer not found")
    is_buyer=o.listing.buyer_id==user.id
    is_seller=o.seller_id==user.id
    if user.role!="admin" and not is_buyer and not is_seller: raise HTTPException(403,"You are not part of this offer")
    if data.status in ("accepted","rejected") and not is_buyer and user.role!="admin": raise HTTPException(403,"Only the buyer can accept or reject")
    if data.status=="paid" and not is_buyer and user.role!="admin": raise HTTPException(403,"Only the buyer can record payment")
    if data.status=="delivered" and not is_seller and user.role!="admin": raise HTTPException(403,"Only the seller can mark delivery")
    o.status=data.status; db.commit(); db.refresh(o); return public_offer(o)

@app.get("/api/dashboard/summary")
def dashboard_summary(db:Session=Depends(get_db),user:User=Depends(current_user)):
    if user.role=="admin":
        return {"reports":db.scalar(select(func.count(HotspotReport.id))) or 0,"open_jobs":db.scalar(select(func.count(CollectionJob.id)).where(CollectionJob.status=="open")) or 0,"listings":db.scalar(select(func.count(MarketListing.id)).where(MarketListing.active==True)) or 0,"users":db.scalar(select(func.count(User.id))) or 0,"verified_kg":db.scalar(select(func.coalesce(func.sum(HotspotReport.actual_kg),0)).where(HotspotReport.status=="verified")) or 0}
    reports=db.scalar(select(func.count(HotspotReport.id)).where(HotspotReport.created_by==user.id)) or 0
    offers=db.scalar(select(func.count(SaleOffer.id)).where(SaleOffer.seller_id==user.id)) or 0
    jobs=db.scalar(select(func.count(CollectionJob.id)).where(CollectionJob.collector_id==user.id)) or 0
    listings=db.scalar(select(func.count(MarketListing.id)).where(MarketListing.buyer_id==user.id,MarketListing.active==True)) or 0
    return {"reports":reports,"offers":offers,"jobs":jobs,"listings":listings,"role":user.role}
@app.get("/api/admin/overview")
def admin_overview(db:Session=Depends(get_db),user:User=Depends(roles("admin"))):
    users=db.scalars(select(User).order_by(User.created_at.desc()).limit(100)).all()
    reports=db.scalars(select(HotspotReport).order_by(HotspotReport.created_at.desc()).limit(100)).all()
    return {"users":[{"id":u.id,"name":u.name,"email":u.email,"role":u.role,"active":u.active,"created_at":u.created_at.isoformat()} for u in users],"reports":[public_report(r) for r in reports]}
