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
    # Field tambahan yang dikirim frontend & seed data
    rfqId: str = ""
    buyer: str = ""
    supplier: str = ""
    value: float = 0
    currency: str = "USD"
    incoterm: str = "FOB"
    validUntil: str = ""
    margin: float = 0
    notes: str = ""
    costLines: list = Field(default_factory=list)
    status: str = "Draft"


# ---------- Orders ----------
class CreateOrderPayload(BaseModel):
    projectId: str = ""
    quotationId: str = ""
    buyerName: str = ""
    value: float = 0
    incoterm: str = "FOB"
    # Field tambahan yang dikirim frontend & seed data
    buyer: str = ""
    supplier: str = ""
    currency: str = "USD"
    paymentTerms: str = ""
    deliveryWindow: str = ""
    readiness: int = 0
    status: str = "Draft"
    lines: list = Field(default_factory=list)
    checklist: list = Field(default_factory=list)


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


# ---------- Batch actions ----------
class BatchActionPayload(BaseModel):
    ids: list[str] = []


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


class CompareExportAnalysisPayload(BaseModel):
    product_id: str
    country_codes: list[str]


class ReanalyzePayload(BaseModel):
    pass


class RegulationRecommendationsPayload(BaseModel):
    language: str = "id"


# ---------- AI marketing ----------
class GenerateMarketIntelligencePayload(BaseModel):
    productId: str = ""
    product_id: str = ""


class GenerateProductPricingPayload(BaseModel):
    productId: str = ""
    product_id: str = ""
    cogs_per_unit_idr: float
    cogsPerUnitIdr: Optional[float] = None
    target_margin_percent: float = 30
    targetMarginPercent: Optional[float] = None
    target_country_code: str = "JP"
    targetCountryCode: Optional[str] = None


class GenerateCatalogDescriptionPayload(BaseModel):
    is_food_product: Optional[bool] = None
    save_to_catalog: Optional[bool] = False


# ---------- Countries / Regulations / HS codes ----------
class CreateCountryPayload(BaseModel):
    country_code: str
    country_name: str
    region: str = ""


class UpdateCountryPayload(BaseModel):
    country_name: str = ""
    region: str = ""


class CreateRegulationPayload(BaseModel):
    rule_category: str = "Labeling"
    forbidden_keywords: str = ""
    required_specs: str = ""
    description_rule: str = ""


class UpdateRegulationPayload(CreateRegulationPayload):
    pass


class CreateHSCodePayload(BaseModel):
    hs_code: str
    description: str = ""
    description_id: str = ""
    section: str = ""
    keywords: list[str] = Field(default_factory=list)


# ---------- Buyer profiles ----------
class CreateBuyerProfilePayload(BaseModel):
    # Terima BOTH snake_case (referensi lama/tests) dan camelCase (frontend).
    company_name: Optional[str] = None
    companyName: Optional[str] = None
    company_description: Optional[str] = None
    companyDescription: Optional[str] = None
    contact_info: Optional[dict] = None
    contactInfo: Optional[dict] = None
    preferred_product_categories: Optional[list] = None
    preferredProductCategories: Optional[list] = None
    preferred_product_categories_description: Optional[str] = None
    source_countries: Optional[list] = None
    sourceCountries: Optional[list] = None
    source_countries_description: Optional[str] = None
    business_type: Optional[str] = None
    businessType: Optional[str] = None
    business_type_description: Optional[str] = None
    annual_import_volume: Optional[str] = None
    annualImportVolume: Optional[str] = None
    annual_import_volume_description: Optional[str] = None


class UpdateBuyerProfilePayload(CreateBuyerProfilePayload):
    pass


# ---------- Buyer request status ----------
class UpdateBuyerRequestStatusPayload(BaseModel):
    status: str = "Open"
    selected_catalog: str = ""
    selected_catalog_id: str = ""
    umkm: str = ""
    umkm_id: str = ""


# ---------- Forwarder profiles & reviews ----------
class CreateForwarderProfilePayload(BaseModel):
    # Terima BOTH snake_case (referensi lama/tests) dan camelCase (frontend).
    company_name: Optional[str] = None
    companyName: Optional[str] = None
    contact_info: Optional[dict] = None
    contactInfo: Optional[dict] = None
    specialization_routes: Optional[list] = None
    specializationRoutes: Optional[list] = None
    service_types: Optional[list] = None
    serviceTypes: Optional[list] = None


class UpdateForwarderProfilePayload(CreateForwarderProfilePayload):
    pass


class CreateForwarderReviewPayload(BaseModel):
    rating: int = 5
    review_text: str = ""


class UpdateForwarderReviewPayload(CreateForwarderReviewPayload):
    pass


# ---------- Educational ----------
class CreateEducationalModulePayload(BaseModel):
    title: str
    description: str = ""
    order_index: int = 0


class UpdateEducationalModulePayload(CreateEducationalModulePayload):
    pass


class CreateEducationalArticlePayload(BaseModel):
    module_id: str = ""
    title: str
    content: str = ""
    video_url: str = ""
    file_url: str = ""
    order_index: int = 0


class UpdateEducationalArticlePayload(CreateEducationalArticlePayload):
    pass


# ---------- Chat sessions ----------
class CreateChatSessionPayload(BaseModel):
    title: str = ""


class RenameChatSessionPayload(BaseModel):
    title: str


class SendChatPayload(BaseModel):
    text: str


# ---------- Catalog images / variants ----------
class AddCatalogImagePayload(BaseModel):
    image_url: str = ""
    alt_text: str = ""
    sort_order: int = 0
    is_primary: bool = False


class UpdateCatalogImagePayload(AddCatalogImagePayload):
    pass


class AddVariantTypePayload(BaseModel):
    type_code: str = "custom"
    type_name: str
    sort_order: int = 0
    options: list[str] = Field(default_factory=list)


class UpdateVariantTypePayload(BaseModel):
    type_code: str = "custom"
    type_name: str = ""
    sort_order: Optional[int] = None


class AddVariantOptionPayload(BaseModel):
    option_name: str
    sort_order: int = 0
    is_available: bool = True


class UpdateVariantOptionPayload(AddVariantOptionPayload):
    pass


# ---------- Dashboard ----------
class RegisterAdminPayload(BaseModel):
    email: EmailStr
    password: str
    full_name: str = "Admin"
    admin_code: str = ""


# ---------- Product update / override ----------
class UpdateProductPayload(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    origin: Optional[str] = None
    description: Optional[str] = None
    material_composition: Optional[str] = None
    production_technique: Optional[str] = None
    finishing_type: Optional[str] = None
    quality_specs: Optional[dict] = None
    packaging: Optional[str] = None
    dimensions_l_w_h: Optional[dict] = None
    weight_net: Optional[float] = None
    weight_gross: Optional[float] = None
    netWeight: Optional[str] = None
    grossWeight: Optional[str] = None
    moq: Optional[str] = None
    leadTime: Optional[str] = None
    hs: Optional[str] = None
    hs_code: Optional[str] = None
    sku: Optional[str] = None
    name_english_b2b: Optional[str] = None
    description_english_b2b: Optional[str] = None
    marketing_highlights: Optional[list] = None


# ---------- Costing update / create detail ----------
class CreateCostingPayload(BaseModel):
    title: str
    destination: str
    projectId: str = ""
    productId: str = ""
    incoterm: str = "FOB"
    targetMargin: float = 20
    margin: Optional[float] = None
    # Fields untuk kalkulasi nyata
    cogs_per_unit_idr: Optional[float] = None
    cogsPerUnitIdr: Optional[float] = None
    packing_cost_idr: Optional[float] = None
    packingCostIdr: Optional[float] = None
    distance_km: Optional[float] = 200
    distanceKm: Optional[float] = None
    product_volume_m3: Optional[float] = 0
    productWeightKg: Optional[float] = 0


class UpdateCostingPayload(BaseModel):
    title: Optional[str] = None
    destination: Optional[str] = None
    incoterm: Optional[str] = None
    margin: Optional[float] = None
    cogs_per_unit_idr: Optional[float] = None
    cogsPerUnitIdr: Optional[float] = None
    packing_cost_idr: Optional[float] = None
    packingCostIdr: Optional[float] = None
    distance_km: Optional[float] = None
    distanceKm: Optional[float] = None
    product_volume_m3: Optional[float] = None
    productWeightKg: Optional[float] = None
    exchange_rate: Optional[float] = None


# ---------- Catalog create/update ----------
class CreateCatalogPayload(BaseModel):
    title: str
    targetMarket: str
    moq: str
    productId: str = ""
    projectId: str = ""
    leadTime: str = ""
    priceRange: str = ""
    description: Optional[str] = ""
    highlights: Optional[list] = None
    specifications: Optional[list] = None
    tags: Optional[list] = None
    display_name: Optional[str] = None
    marketing_description: Optional[str] = None
    min_order_quantity: Optional[float] = None
    unit_type: Optional[str] = "pcs"
    base_price_exw: Optional[float] = None
    lead_time_days: Optional[int] = 14
    available_stock: Optional[int] = 0


class UpdateCatalogPayload(BaseModel):
    title: Optional[str] = None
    targetMarket: Optional[str] = None
    moq: Optional[str] = None
    leadTime: Optional[str] = None
    priceRange: Optional[str] = None
    description: Optional[str] = None
    highlights: Optional[list] = None
    specifications: Optional[list] = None
    tags: Optional[list] = None
    is_published: Optional[bool] = None
    export_description: Optional[str] = None
    technical_specs: Optional[list] = None
    safety_info: Optional[list] = None
    lead_time_days: Optional[int] = None
    available_stock: Optional[int] = None
    min_order_quantity: Optional[float] = None
    unit_type: Optional[str] = None
    base_price_exw: Optional[float] = None


# ---------- Users delete ----------
class DeleteUserPayload(BaseModel):
    pass
