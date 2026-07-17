import pandas as pd
from data_pipeline.mappings.base import FieldMapping
from data_pipeline.transformation.canonical import to_canonical
def test_mapping_is_isolated()->None:
    result=to_canonical(pd.DataFrame([{"external":"value"}]),FieldMapping({"external":"canonical"}))
    assert result.to_dict("records")==[{"canonical":"value"}]
