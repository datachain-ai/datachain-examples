import datachain as dc
from datachain import C
from datachain.toolkit import train_test_split


dc_filtered = (
    dc.read_dataset("fashion-product-images")
    .filter((C("masterCategory") == "Apparel") & (C("subCategory") == "Topwear"))
    .persist()
)

train, test, val = train_test_split(dc_filtered, [0.7, 0.2, 0.1])

dc_train = train.save("fashion-train")
dc_test = test.save("fashion-test")
dc_val = val.save("fashion-val")


print(train.count())
print(val.count())
print(test.count())
