"""
# Getting Started with DataChain

Before you begin, ensure you have
- DataChain installed in your environment.
- Download the Fashion Product Images (Small) dataset (see README.md)
- Save data in the  `data` directory
    - `data/images`
    - `data/styles.csv`
"""

import datachain as dc
from datachain import C
from datachain.sql.functions import path

# Define the paths
DATA_PATH = "gs://datachain-demo/fashion-product-images"
ANNOTATIONS_PATH = "gs://datachain-demo/fashion-product-images/styles_clean.csv"

print("\n# Create a Dataset")
dc_chain = dc.read_storage(DATA_PATH, type="image", anon=True).filter(
    C("file.path").glob("*.jpg")
)
dc_chain.show(3)

print("\n# Create a metadata DataChain")
dc_meta = dc.read_csv(ANNOTATIONS_PATH, source=False).persist()
dc_meta.show(3)

print("\n# Merge the original image and metadata datachains")
dc_annotated = dc_chain.merge(dc_meta, on=path.name(dc_chain.c("file.path")), right_on="filename")

print("\n# Save dataset")
dc_annotated.save("fashion-product-images")

print("\n# Filtering Data")
dc_filtered = dc.read_dataset(name="fashion-product-images").filter(
    (C("mastercategory") == "Apparel") & (C("subcategory") == "Topwear")
)
dc_filtered.show()

dc_filtered.save("fashion-topwear")
