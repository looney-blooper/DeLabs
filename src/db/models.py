import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    runs = relationship("ModelRun", back_populates="project", cascade="all, delete-orphan")


class ModelRun(Base):
    __tablename__ = 'model_runs'
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    status = Column(String(50), nullable=False, default="pending")# pending, training, completed, failed
    
    # Metadata & Configurations
    hyperparameters = Column(JSON, nullable=True) # e.g., {"lr": 0.001, "batch_size": 64, "epochs": 10}
    architecture_summary = Column(Text, nullable=True) # Text markdown from Architect agent
    
    # Storage Artifact URIs (MinIO links)
    source_code_url = Column(String(512), nullable=True)
    weights_url = Column(String(512), nullable=True)
    validation_report = Column(Text, nullable=True) # Markdown report from Reviewer/QA
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="runs")
    telemetry = relationship("TelemetryData", back_populates="run", cascade="all, delete-orphan")



class TelemetryData(Base):
    __tablename__ = "telemetry_data"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("model_runs.id"), nullable=False)
    epoch = Column(Integer, nullable=False)
    loss = Column(Float, nullable=False)
    val_loss = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    val_accuracy = Column(Float, nullable=True)
    
    # Optional Hardware tracking
    vram_used_gb = Column(Float, nullable=True)
    gpu_temp_c = Column(Float, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    run = relationship("ModelRun", back_populates="telemetry")