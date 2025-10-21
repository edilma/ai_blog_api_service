from qdrant_client import QdrantClient

# Connect to your running Qdrant instance
client = QdrantClient("localhost", port=6333)

COLLECTION_NAME = "data/processed/20251020-182510_Kholer bathtub UNI-PS18310_Spec.json" # IMPORTANT: Change this to your actual collection name

# Fetch a few points without any filtering
points = client.scroll(
    collection_name=COLLECTION_NAME,
    limit=5,
    with_payload=True,
    with_vectors=False
)

print("--- Inspecting Data in Qdrant ---")
for point in points[0]:
    print(f"Point ID: {point.id}")
    print(f"Payload: {point.payload}")
    print("-" * 20)