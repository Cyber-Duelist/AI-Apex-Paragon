from pydantic import BaseModel, ValidationError

# 1. The blueprint for data coming IN (Creation)
# We don't include 'id' here because SQL automatically generates the ID!
class DocumentCreate(BaseModel):
    title: str
    department: str
    num_pages: int
    high_risk: int
    created_at: str

# 2. The blueprint for data going OUT (Response)
# It inherits everything from DocumentCreate, but adds the 'id' field
# so we can send the full database record back to the user.
class DocumentResponse(DocumentCreate):
    id: int

# 3. The Validation Function
def validate_document(data: dict):
    # The ** unpacks the dictionary and forces it into the strict Pydantic model
    return DocumentCreate(**data)

print("=== VALID DOCUMENT ===")
valid_data = {
    "title": "Merger Agreement",
    "department": "Legal",
    "num_pages": 105,
    "high_risk": 1,
    "created_at": "2024-01-18"
}
try:
    # This should work perfectly
    model = validate_document(valid_data)
    print(model)
except ValidationError as e:
    print(f"ValidationError caught:\n{e}")

print("\n=== INVALID TYPE ===")
invalid_type_data = {
    "title": "Merger Agreement",
    "department": "Legal",
    "num_pages": "twenty",  # <-- STRING INSTEAD OF INTEGER!
    "high_risk": 1,
    "created_at": "2024-01-18"
}
try:
    model = validate_document(invalid_type_data)
    print(model)
except ValidationError as e:
    print("ValidationError caught:")
    print(e)

print("\n=== MISSING FIELD ===")
missing_field_data = {
    # <-- TITLE IS MISSING!
    "department": "Legal",
    "num_pages": 105,
    "high_risk": 1,
    "created_at": "2024-01-18"
}
try:
    model = validate_document(missing_field_data)
    print(model)
except ValidationError as e:
    print("ValidationError caught:")
    print(e)