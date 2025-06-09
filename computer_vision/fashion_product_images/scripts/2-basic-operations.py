import datachain as dc
from datachain import C

print("\n# Connect to a dataset:")
dc = dc.read_dataset("fashion-product-images")  # from 1-quick-start.py

print("\n# Filtering & Sorting:")
(
    dc.select(
        "file.path",
        "usage",
        "season",
        "year",
        "gender",
        "mastercategory",
        "subcategory",
        "articletype",
        "basecolour",
        "productdisplayname",
    )
    .filter(C("usage") == "Casual" and C("season") == "Summer")
    .order_by("year")
    .group_by("gender")
    .show()
)


print("\n# Add signals (columns) with map() method:")
dc_len = dc.read_dataset("fashion-product-images").map(
    prod_name_length=lambda file: len(file.name),
    output=int,
)

dc_len.show(3)

print("\n# Save a dataset (version):")
dc_len.save("fashion-tmp")

print("\n# Save a new version (with prod_name_length_2 column):")
(
    dc.read_dataset("fashion-summer-topwear-apparel")
    .map(prod_name_length_2=lambda file: len(file.name), output=int)
    .save("fashion-tmp")
)

# Load the latest version and show the first 3 rows -
print("\n# Load the latest version and show the first 3 rows:")
dc.read_dataset("fashion-tmp").limit(3)
