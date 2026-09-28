from product_details.wrapper.product_details_wrapper import ProductDetailsWrapper


IMAGE_PATH = "samples/images/img_004.jpeg"


print("=" * 60)
print("TRUSTLENS PRODUCT DETAILS TEST")
print("=" * 60)

print("\nLoading ProductDetailsWrapper...")

wrapper = ProductDetailsWrapper()

print("ProductDetailsWrapper loaded successfully.")

print("\nExtracting product details...")

result = wrapper.extract(
    image_path=IMAGE_PATH,
    product_name=None
)

print("\n" + "=" * 60)
print("PRODUCT DETAILS RESULT")
print("=" * 60)

print(result.to_dict())

print("\n" + "=" * 60)
print("INGREDIENTS")
print("=" * 60)

print(", ".join(result.ingredients))

print("\n" + "=" * 60)