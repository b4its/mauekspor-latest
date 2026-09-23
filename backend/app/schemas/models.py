"""Pydantic request models untuk tiap payload yang dikirim frontend."""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------
class LoginPayload(BaseModel):
    email: EmailStr
    password: str


class RegisterPayload(LoginPayload):
    name: str
    role: str = Field(default="Exporter")
    organization: str = ""


# ---------- Products ----------
class CreateProductPayload(BaseModel):
    name: str
    category: str
    origin: str
    packaging: Optional[str] = None
    netWeight: Optional[str] = None
    grossWeight: Optional[str] = None
    moq: Optional[str] = None
    leadTime: Optional[str] = None


# ---------- Trade projects ----------
class CreateTradeProjectPayload(BaseModel):
    name: str
    country: str
    projectType: str = "Exporter-led"
    product: str = ""
    buyer: str = ""
    incoterm: str = ""
    targetValue: Optional[float] = None
    eta: Optional[str] = None


# ---------- Business profiles ----------
class CreateBusinessProfilePayload(BaseModel):
    companyName: str
    address: str = ""
    productionCapacity: Optional[str] = None
    yearEstablished: Optional[int] = None
    certifications: list[str] = Field(default_factory=list)
    status: str = "Draft"
    owner: str = ""
    readiness: int = 20


class UpdateCertificationsPayload(BaseModel):
    certifications: list[str]


# ---------- Buyers ----------
class CreateBuyerPayload(BaseModel):
    name: str
    country: str
    segment: str = ""
    interestedProducts: list[str] = Field(default_factory=list)


class LogBuyerContactPayload(BaseModel):
    note: str


# ---------- Buyer requests ----------
class CreateBuyerRequestPayload(BaseModel):
    subject: str
    destination: str
    quantity: str
    buyerId: str = ""
    productId: str = ""
    deadline: str = ""
    requirements: list[str] = Field(default_factory=list)


# ---------- Forwarders ----------
class CreateForwarderPayload(BaseModel):
    name: str
    coverage: str = ""
    mode: str = "Ocean"
    contact: str = ""


# ---------- Catalogs ----------
class CreateCatalogPayload(BaseModel):
    title: str
    targetMarket: str
    moq: str
    productId: str = ""
    projectId: str = ""
    leadTime: str = ""
    priceRange: str = ""


# ---------- Costing ----------
class CreateCostingPayload(BaseModel):
    title: str
    destination: str
    projectId: str = ""
    productId: str = ""
    incoterm: str = "FOB"
    targetMargin: float = 20
    margin: Optional[float] = None


# ---------- Markets ----------
class CreateMarketPayload(BaseModel):
    country: str
    productId: str = ""
    projectId: str = ""
    entryStrategy: str = ""


# ---------- RFQ ----------
class CreateRFQPayload(BaseModel):
    destination: str
    projectId: str = ""
    productId: str = ""
    buyerName: str = ""
    buyer: str = ""
    product: str = ""
    quantity: str = ""
    deadline: str = ""
    incoterm: str = ""


class ShortlistRFQPayload(BaseModel):
    supplier: str


# ---------- Quotations ----------
class CreateQuotationPayload(BaseModel):
    projectId: str = ""
    productId: str = ""
    buyerName: str = ""
    incoterm: str = "FOB"
    validUntil: str = ""


# ---------- Orders ----------
class CreateOrderPayload(BaseModel):
    projectId: str = ""
    quotationId: str = ""
    buyerName: str = ""
    value: float = 0
    incoterm: str = "FOB"


# ---------- Compliance ----------
class UploadComplianceEvidencePayload(BaseModel):
    requirementId: str = ""
    description: str = ""
    fileUrl: str = ""


# ---------- Documents ----------
class GenerateDocumentPayload(BaseModel):
    type: str = "Commercial Invoice"
    projectId: str = ""
    data: dict = {}


# ---------- Payments ----------
class MarkPaymentReceivedPayload(BaseModel):
    amount: Optional[float] = None
    method: Optional[str] = None


# ---------- Tasks ----------
class AssignTaskPayload(BaseModel):
    owner: str


# ---------- Calendar ----------
class CreateCalendarEventPayload(BaseModel):
    title: str
    date: str
    type: str = "Task"
    projectId: str = ""
    owner: str = ""
    description: str = ""


# ---------- Team ----------
class InviteTeamMemberPayload(BaseModel):
    email: EmailStr
    role: str = "Operations"


class RoleUpdatePayload(BaseModel):
    role: str


# ---------- Messages ----------
class SendMessagePayload(BaseModel):
    body: str


# ---------- Support ----------
class CreateSupportTicketPayload(BaseModel):
    subject: str
    category: str = "Question"
    description: str = ""


# ---------- Templates ----------
class CreateTemplatePayload(BaseModel):
    title: str
    category: str = "Document"
    description: str = ""


# ---------- Files ----------
class UploadFilePayload(BaseModel):
    name: str
    type: str = "Document"
    projectId: str = ""


# ---------- API Keys ----------
class CreateApiKeyPayload(BaseModel):
    name: str
    scopes: list[str] = Field(default_factory=list)


# ---------- Billing ----------
class ChangePlanPayload(BaseModel):
    plan: str


# ---------- Integrations ----------
class IntegrationActionPayload(BaseModel):
    account_id: Optional[str] = None


# ---------- Chat ----------
class SendChatPayload(BaseModel):
    text: str


# ---------- Audit ----------
class AuditExportPayload(BaseModel):
    format: str = "csv"


# ---------- Export analysis ----------
class CreateExportAnalysisPayload(BaseModel):
    productId: str
    destination: str